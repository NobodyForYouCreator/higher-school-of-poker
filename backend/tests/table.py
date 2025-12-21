from pathlib import Path
from random import randint

from fastapi import APIRouter, Request, Query, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.poker_engine.table import Table
from backend.poker_engine.game_state import PlayerAction
from backend.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.game_service import GameService

router = APIRouter(tags=["table"])

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
tables_dict: dict[int, Table] = {}

game_service = GameService()


@router.get("/tables", response_class=HTMLResponse)
def tables(request: Request, format: str | None = Query(default=None)):
    table_entries = [_serialize_table(table) for table in tables_dict.values()]
    accepts = request.headers.get("accept", "")
    wants_json = format == "json" or "application/json" in accepts
    if wants_json:
        return {"status": 200, "tables": table_entries}
    return templates.TemplateResponse(
        "tables.html",
        {"request": request, "tables": table_entries},
    )


@router.post("/tables/create")
def create_table():
    table_ind = randint(0, 100_000)

    tables_dict[table_ind] = Table(table_id=table_ind)
    return {"status": 200, "added": table_ind}


@router.get("/tables/{table_id}", response_class=HTMLResponse)
def get_table_info(request: Request, table_id: int):
    table = tables_dict.get(table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    data = _serialize_table(table)
    current_bet_value = table.game_state.current_bet if table.game_state else 0
    data.update(
        {
            "players_list": [
                {
                    "user_id": player.user_id,
                    "stack": player.stack,
                    "status": player.status.value,
                    "position": player.position,
                    "bet": player.bet,
                    "bet_percent": int(player.bet / current_bet_value * 100) if current_bet_value else 0,
                }
                for player in table.players
            ],
            "spectators_list": [
                {
                    "user_id": spectator.user_id,
                    "status": spectator.status.value,
                }
                for spectator in table.spectators
            ],
            "pot": table.game_state.pot if table.game_state else 0,
            "phase": table.game_state.phase.value if table.game_state else "waiting",
            "board": [
                str(card) for card in (table.game_state.board if table.game_state else [])
            ],
            "current_bet": current_bet_value,
        }
    )
    return templates.TemplateResponse(
        "table_detail.html",
        {"request": request, "table": data},
    )


@router.get("/tables/{table_id}/game_started", response_class=HTMLResponse)
async def start_or_resume_game(
    request: Request,
    table_id: int,
    error: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    table = tables_dict.get(table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    status_message: str | None = None
    if not table.game_state or not table.game_state.hand_active:
        try:
            await game_service.start_hand(table)
            status_message = "Новая раздача началась."
        except RuntimeError as exc:
            status_message = str(exc)
    context = {
        "request": request,
        "table": _build_game_snapshot(table),
        "actions": _available_actions(),
        "status_message": status_message,
        "error": error,
    }
    return templates.TemplateResponse("table_game.html", context)


@router.post("/tables/{table_id}/game_started")
async def apply_game_action(
    request: Request,
    table_id: int,
    user_id: int = Form(...),
    action: str = Form(...),
    amount: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    table = tables_dict.get(table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    if not table.game_state or not table.game_state.hand_active:
        return RedirectResponse(f"/api/tables/{table_id}", status_code=303)
    try:
        player_action = PlayerAction(action)
    except ValueError:
        context = {
            "request": request,
            "table": _build_game_snapshot(table),
            "actions": _available_actions(),
            "error": "Неизвестное действие.",
        }
        return templates.TemplateResponse("table_game.html", context, status_code=400)
    amount_value = 0
    if amount and amount.strip():
        try:
            amount_value = int(amount)
        except ValueError:
            context = {
                "request": request,
                "table": _build_game_snapshot(table),
                "actions": _available_actions(),
                "error": "Сумма должна быть числом.",
            }
            return templates.TemplateResponse("table_game.html", context, status_code=400)
    try:
        await game_service.apply_action(table, user_id, player_action, amount_value, db)
    except Exception as exc:
        context = {
            "request": request,
            "table": _build_game_snapshot(table),
            "actions": _available_actions(),
            "error": str(exc),
        }
        return templates.TemplateResponse("table_game.html", context, status_code=400)
    if table.game_state and not table.game_state.hand_active:
        return templates.TemplateResponse(
            "table_game_result.html",
            _result_context(request, table),
        )
    return RedirectResponse(f"/api/tables/{table_id}/game_started", status_code=303)


@router.post("/tables/{table_id}/join/{user_id}")
def join_table(table_id: int, user_id: int):
    tables_dict[table_id].seat_player(user_id, 1500)
    return {"connected to": table_id}


@router.post("/tables/{table_id}/leave/{user_id}")
def leave_table(table_id: int, user_id: int):
    tables_dict[table_id].leave(user_id)
    return {"leaved to": table_id}


@router.post("/tables/{table_id}/spectate/{user_id}")
def spectator_join_table(table_id: int, user_id: int):
    tables_dict[table_id].seat_player(user_id, 1500, is_spectator=True)
    return {"spectating to": table_id}


def _serialize_table(table: Table) -> dict:
    phase = None
    if table.game_state:
        phase = table.game_state.phase.value
        current_bet = table.game_state.current_bet
        pot = table.game_state.pot
    else:
        current_bet = 0
        pot = 0
    return {
        "table_id": table.table_id,
        "max_players": table.max_players,
        "players": len(table.players),
        "spectators": len(table.spectators),
        "small_blind": table.small_blind,
        "big_blind": table.big_blind,
        "status": phase or "waiting",
        "current_bet": current_bet,
        "pot": pot,
    }


def _build_game_snapshot(table: Table) -> dict:
    game = table.game_state
    current_player_id = None
    if game and game.current_player_index is not None:
        current_player_id = game.players[game.current_player_index].user_id
    board = [str(card) for card in game.board] if game else []
    current_bet = game.current_bet if game else 0
    players = []
    for player in table.players:
        bet_percent = 0
        if current_bet > 0:
            bet_percent = min(100, int(player.bet / current_bet * 100))
        players.append(
            {
                "user_id": player.user_id,
                "stack": player.stack,
                "bet": player.bet,
                "status": player.status.value,
                "position": player.position,
                "cards": [str(card) for card in player.hole_cards],
                "is_turn": current_player_id == player.user_id,
                "bet_percent": bet_percent,
            }
        )
    spectators = [
        {
            "user_id": spectator.user_id,
            "status": spectator.status.value,
        }
        for spectator in table.spectators
    ]
    return {
        "table_id": table.table_id,
        "phase": game.phase.value if game else "waiting",
        "pot": game.pot if game else 0,
        "board": board,
        "players": players,
        "spectators": spectators,
        "current_player_id": current_player_id,
        "current_bet": current_bet,
        "small_blind": table.small_blind,
        "big_blind": table.big_blind,
        "max_players": table.max_players,
    }


def _available_actions() -> list[dict]:
    return [
        {"value": PlayerAction.CHECK.value, "label": "Check"},
        {"value": PlayerAction.CALL.value, "label": "Call"},
        {"value": PlayerAction.BET.value, "label": "Bet"},
        {"value": PlayerAction.RAISE.value, "label": "Raise"},
        {"value": PlayerAction.FOLD.value, "label": "Fold"},
        {"value": PlayerAction.ALL_IN.value, "label": "All-in"},
    ]


def _result_context(request: Request, table: Table) -> dict:
    game = table.game_state
    winners = []
    winning_hand = None
    if game:
        winners = [
            {
                "user_id": player.user_id,
                "stack": player.stack,
            }
            for player in game.winners
        ]
        if game.best_hand:
            winning_hand = {
                "rank": game.best_hand.rank.name,
                "cards": [str(card) for card in game.best_hand.cards],
            }
    return {
        "request": request,
        "table_id": table.table_id,
        "winners": winners,
        "winning_hand": winning_hand,
        "board": [str(card) for card in (game.board if game else [])],
    }
