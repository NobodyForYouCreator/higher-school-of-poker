from __future__ import annotations

from dataclasses import dataclass
from random import randint

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.poker_engine.table import Table

router = APIRouter(tags=["table"])


class TableCreateRequest(BaseModel):
    max_players: int = Field(ge=2, le=9)
    buy_in: int = Field(ge=0)
    private: bool = False


@dataclass(slots=True)
class TableRecord:
    table: Table
    buy_in: int
    private: bool


tables_dict: dict[int, TableRecord] = {}


def _serialize_summary(table_id: int, record: TableRecord) -> dict:
    return {
        "id": str(table_id),
        "max_players": record.table.max_players,
        "buy_in": record.buy_in,
        "private": record.private,
        "players_count": len(record.table.players),
        "spectators_count": len(record.table.spectators),
    }


@router.get("/tables")
def list_tables() -> list[dict]:
    return [_serialize_summary(table_id, record) for table_id, record in tables_dict.items()]


@router.post("/tables/create")
def create_table(payload: TableCreateRequest) -> dict:
    table_id = randint(0, 100_000)
    while table_id in tables_dict:
        table_id = randint(0, 100_000)

    table = Table(table_id=table_id, max_players=payload.max_players)
    tables_dict[table_id] = TableRecord(table=table, buy_in=payload.buy_in, private=payload.private)
    return _serialize_summary(table_id, tables_dict[table_id])


@router.get("/tables/{table_id}")
def get_table_info(table_id: int) -> dict:
    record = tables_dict.get(table_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Table not found")

    info = _serialize_summary(table_id, record)
    info["seats"] = [
        {
            "position": player.position,
            "user_id": player.user_id,
            "stack": player.stack,
            "is_spectator": False,
        }
        for player in record.table.players
    ] + [
        {
            "position": -1,
            "user_id": spectator.user_id,
            "stack": spectator.stack,
            "is_spectator": True,
        }
        for spectator in record.table.spectators
    ]
    return info


def _current_user_id(request: Request) -> int:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return int(user_id)


@router.post("/tables/{table_id}/join")
def join_table(request: Request, table_id: int) -> dict:
    record = tables_dict.get(table_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Table not found")

    user_id = _current_user_id(request)
    already_in = any(p.user_id == user_id for p in record.table.players)
    if not already_in:
        record.table.seat_player(user_id, record.buy_in)
    return {"ok": True}


@router.post("/tables/{table_id}/leave")
def leave_table(request: Request, table_id: int) -> dict:
    record = tables_dict.get(table_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Table not found")

    user_id = _current_user_id(request)
    record.table.leave(user_id)
    return {"ok": True}


@router.post("/tables/{table_id}/spectate")
def spectate_table(request: Request, table_id: int) -> dict:
    record = tables_dict.get(table_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Table not found")

    user_id = _current_user_id(request)
    already_in = any(p.user_id == user_id for p in record.table.spectators)
    if not already_in:
        record.table.seat_player(user_id, record.buy_in, is_spectator=True)
    return {"ok": True}

