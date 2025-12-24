from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.auth.jwt_tokens import decode_access_token
from backend.database.session import SessionLocal
from backend.models.user import User
from backend.poker_engine.game_state import PlayerAction
from backend.poker_engine.player_state import PlayerStatus
from backend.services.game_service import GameService
from backend.services.table_store import table_store

router = APIRouter(tags=["ws"])

_game_service = GameService()


def _ws_error(code: str, message: str) -> dict[str, Any]:
    return {"type": "error", "code": code, "message": message}


@dataclass(slots=True)
class _Conn:
    websocket: WebSocket
    user_id: int
    show_all: bool = False


_table_conns: dict[int, dict[WebSocket, _Conn]] = {}
_table_locks: dict[int, asyncio.Lock] = {}
_pending_leave_tasks: dict[tuple[int, int], asyncio.Task[None]] = {}
_pending_next_hand_tasks: dict[int, asyncio.Task[None]] = {}

LEAVE_GRACE_SECONDS = 60
NEXT_HAND_DELAY_SECONDS = 5


async def _credit_balance(user_id: int, amount: int) -> None:
    if amount <= 0:
        return
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if user is None:
            return
        user.balance = int(user.balance) + int(amount)
        await session.commit()


def _get_lock(table_id: int) -> asyncio.Lock:
    lock = _table_locks.get(table_id)
    if lock is None:
        lock = asyncio.Lock()
        _table_locks[table_id] = lock
    return lock


def _build_table_state(table_id: int, *, viewer_id: int, show_all: bool) -> dict[str, Any]:
    record = table_store.get(table_id)
    if record is None:
        raise KeyError("table_not_found")

    table = record.table
    game = table.game_state

    phase = "preflop"
    pot = 0
    board: list[str] = []
    current_player_id: int | None = None
    current_bet: int | None = None
    hand_active: bool = False
    winners: list[int] = []
    best_hand_rank: str | None = None
    best_hand_cards: list[str] = []

    reveal_all = show_all

    if game is not None:
        phase = str(getattr(game.phase, "value", "preflop"))
        pot = int(getattr(game, "pot", 0))
        board = [str(card) for card in getattr(game, "board", [])]
        current_bet = int(getattr(game, "current_bet", 0))
        hand_active = bool(getattr(game, "hand_active", False))
        winners = [int(p.user_id) for p in getattr(game, "winners", []) or []]
        if phase == "finished" and winners:
            reveal_all = True
        best = getattr(game, "best_hand", None)
        if best is not None:
            best_hand_rank = str(
                getattr(
                    getattr(best, "rank", None),
                    "name",
                    getattr(getattr(best, "rank", None), "value", ""),
                )
                or ""
            )
            best_hand_cards = [str(c) for c in getattr(best, "cards", []) or []]
        idx = getattr(game, "current_player_index", None)
        if idx is not None:
            try:
                current_player_id = int(game.players[int(idx)].user_id)
            except Exception:
                current_player_id = None

    players: list[dict[str, Any]] = []
    for p in table.public_players():
        hole_cards = [str(card) for card in getattr(p, "hole_cards", [])]
        if not (reveal_all or p.user_id == viewer_id):
            hole_cards = []

        player_entry: dict[str, Any] = {
            "user_id": int(p.user_id),
            "position": int(p.position),
            "stack": int(p.stack),
            "bet": int(getattr(p, "bet", 0)),
            "status": str(getattr(p.status, "value", getattr(p, "status", ""))),
        }
        if hole_cards:
            player_entry["hole_cards"] = hole_cards
        players.append(player_entry)

    return {
        "table_id": str(table_id),
        "phase": phase,
        "hand_active": hand_active,
        "pot": pot,
        "board": board,
        "players": players,
        "winners": winners,
        "best_hand_rank": best_hand_rank,
        "best_hand_cards": best_hand_cards,
        "current_player_id": current_player_id,
        "current_bet": current_bet,
        "min_bet": getattr(table, "big_blind", None),
    }


async def _try_send(conn: _Conn, message: dict[str, Any]) -> bool:
    try:
        await conn.websocket.send_text(json.dumps(message))
        return True
    except (WebSocketDisconnect, RuntimeError):
        return False
    except Exception:
        return False


async def _broadcast_state(table_id: int) -> None:
    conns_map = _table_conns.get(table_id)
    if not conns_map:
        return
    conns = list(conns_map.values())
    dead_sockets: list[WebSocket] = []

    record = table_store.get(table_id)
    if record is None:
        message = _ws_error("table_not_found", "Table not found")
        for conn in conns:
            ok = await _try_send(conn, message)
            if not ok:
                dead_sockets.append(conn.websocket)
        for ws in dead_sockets:
            conns_map.pop(ws, None)
        return

    for conn in conns:
        try:
            state = _build_table_state(table_id, viewer_id=conn.user_id, show_all=conn.show_all)
            ok = await _try_send(conn, {"type": "table_state", "payload": state})
            if not ok:
                dead_sockets.append(conn.websocket)
        except Exception as exc:
            ok = await _try_send(conn, _ws_error("broadcast_failed", str(exc)))
            if not ok:
                dead_sockets.append(conn.websocket)

    for ws in dead_sockets:
        conns_map.pop(ws, None)


def _cancel_pending_leave(table_id: int, user_id: int) -> None:
    task = _pending_leave_tasks.pop((table_id, user_id), None)
    if task is not None and not task.done():
        task.cancel()


def _schedule_delayed_leave(table_id: int, user_id: int) -> None:
    if (table_id, user_id) in _pending_leave_tasks:
        return

    async def _leave_later() -> None:
        try:
            await asyncio.sleep(LEAVE_GRACE_SECONDS)
            lock = _get_lock(table_id)
            async with lock:
                conns_map = _table_conns.get(table_id) or {}
                still_connected = any(c.user_id == user_id for c in conns_map.values())
                if still_connected:
                    return

                record = table_store.get(table_id)
                if record is not None:
                    try:
                        cashout = record.table.leave(user_id)
                        await _credit_balance(user_id, cashout)
                    except Exception:
                        pass
                    table_store.delete_if_empty(table_id)
                await _broadcast_state(table_id)
        finally:
            _pending_leave_tasks.pop((table_id, user_id), None)

    _pending_leave_tasks[(table_id, user_id)] = asyncio.create_task(_leave_later())


def _cancel_pending_next_hand(table_id: int) -> None:
    task = _pending_next_hand_tasks.pop(table_id, None)
    if task is not None and not task.done():
        task.cancel()


def _schedule_next_hand(table_id: int) -> None:
    if table_id in _pending_next_hand_tasks:
        return

    async def _start_later() -> None:
        try:
            await asyncio.sleep(NEXT_HAND_DELAY_SECONDS)
            lock = _get_lock(table_id)
            async with lock:
                record = table_store.get(table_id)
                if record is None:
                    return

                table = record.table
                game = table.game_state
                if game is not None and bool(getattr(game, "hand_active", False)):
                    return

                eligible = [p for p in table.public_players() if p.stack > 0]
                if len(eligible) < 2:
                    return

                try:
                    await _game_service.start_hand(table)
                except Exception:
                    return

                await _broadcast_state(table_id)
        finally:
            _pending_next_hand_tasks.pop(table_id, None)

    _pending_next_hand_tasks[table_id] = asyncio.create_task(_start_later())


async def notify_table_changed(table_id: int) -> None:
    """Broadcast the latest table state to all WS clients (if any)."""
    lock = _get_lock(table_id)
    async with lock:
        await _broadcast_state(table_id)


async def maybe_start_game(table_id: int) -> bool:
    """Start a new hand if the table has enough eligible players; broadcast state if started."""
    lock = _get_lock(table_id)
    async with lock:
        record = table_store.get(table_id)
        if record is None:
            return False

        table = record.table
        game = table.game_state
        if game is not None and bool(getattr(game, "hand_active", False)):
            return False

        eligible = [p for p in table.public_players() if p.stack > 0 and p.status != PlayerStatus.SPECTATOR]
        if len(eligible) < 2:
            return False

        _cancel_pending_next_hand(table_id)
        try:
            await _game_service.start_hand(table)
        except Exception:
            return False

        await _broadcast_state(table_id)
        return True


@router.websocket("/ws/tables/{table_id}")
async def table_ws(websocket: WebSocket, table_id: str) -> None:
    await websocket.accept()

    token = websocket.query_params.get("token")
    if not token:
        await websocket.send_text(json.dumps(_ws_error("missing_token", "Missing token")))
        await websocket.close(code=1008)
        return

    try:
        user_id = decode_access_token(token)
    except Exception:
        await websocket.send_text(json.dumps(_ws_error("invalid_token", "Invalid token")))
        await websocket.close(code=1008)
        return

    try:
        table_id_int = int(table_id)
    except ValueError:
        await websocket.send_text(json.dumps(_ws_error("invalid_table_id", "Invalid table_id")))
        await websocket.close(code=1008)
        return

    if table_store.get(table_id_int) is None:
        await websocket.send_text(json.dumps(_ws_error("table_not_found", "Table not found")))
        await websocket.close(code=1008)
        return

    conn = _Conn(websocket=websocket, user_id=user_id)
    _table_conns.setdefault(table_id_int, {})[websocket] = conn
    _cancel_pending_leave(table_id_int, user_id)

    lock = _get_lock(table_id_int)
    async with lock:
        await _broadcast_state(table_id_int)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps(_ws_error("invalid_json", "Invalid JSON")))
                continue

            msg_type = msg.get("type")
            payload = msg.get("payload") or {}

            async with lock:
                record = table_store.get(table_id_int)
                if record is None:
                    await websocket.send_text(json.dumps(_ws_error("table_not_found", "Table not found")))
                    continue

                table = record.table

                if msg_type == "toggle_show_all":
                    is_spectator = any(s.user_id == user_id for s in table.spectators)
                    if not is_spectator:
                        await websocket.send_text(
                            json.dumps(_ws_error("spectator_only", "Show cards is available to spectators only"))
                        )
                        continue
                    conn.show_all = bool(payload.get("show", False))
                    await _broadcast_state(table_id_int)
                    continue

                if msg_type != "player_action":
                    await websocket.send_text(json.dumps(_ws_error("unknown_message_type", "Unknown message type")))
                    continue

                action_str = payload.get("action")
                amount = payload.get("amount") or 0

                is_spectator = any(s.user_id == user_id for s in table.spectators)
                if is_spectator:
                    await websocket.send_text(json.dumps(_ws_error("spectator_cannot_act", "Spectators cannot act")))
                    continue

                is_seated = any(p.user_id == user_id for p in table.public_players())
                if not is_seated:
                    await websocket.send_text(
                        json.dumps(_ws_error("player_not_seated", "Player is not seated at this table"))
                    )
                    continue

                if not isinstance(action_str, str):
                    await websocket.send_text(json.dumps(_ws_error("missing_action", "Missing action")))
                    continue

                if table.game_state is None or not getattr(table.game_state, "hand_active", False):
                    _cancel_pending_next_hand(table_id_int)
                    try:
                        await _game_service.start_hand(table)
                    except Exception as exc:
                        await websocket.send_text(json.dumps(_ws_error("start_hand_failed", str(exc))))
                        continue

                try:
                    player_action = PlayerAction(action_str)
                except ValueError:
                    await websocket.send_text(json.dumps(_ws_error("invalid_action", "Invalid action")))
                    continue

                try:
                    async with SessionLocal() as session:
                        await _game_service.apply_action(table, user_id, player_action, int(amount), session)
                except Exception as exc:
                    await websocket.send_text(json.dumps(_ws_error("action_failed", str(exc))))
                    continue

                await _broadcast_state(table_id_int)
                if table.game_state is not None and not getattr(table.game_state, "hand_active", False):
                    _schedule_next_hand(table_id_int)

    except WebSocketDisconnect:
        pass
    finally:
        lock = _get_lock(table_id_int)
        async with lock:
            conns_map = _table_conns.get(table_id_int)
            if conns_map is not None:
                conns_map.pop(websocket, None)

            still_connected = False
            conns_map = _table_conns.get(table_id_int)
            if conns_map is not None:
                still_connected = any(c.user_id == user_id for c in conns_map.values())

            if not still_connected:
                record = table_store.get(table_id_int)
                if record is not None:
                    _schedule_delayed_leave(table_id_int, user_id)

            if not _table_conns.get(table_id_int):
                _table_conns.pop(table_id_int, None)
                _table_locks.pop(table_id_int, None)
