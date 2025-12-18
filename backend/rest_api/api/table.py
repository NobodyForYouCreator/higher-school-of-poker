from pathlib import Path
from random import randint

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.poker_engine.table import Table

router = APIRouter(tags=["table"])

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
tables_dict: dict[int, Table] = {}


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
    table_ind = randint(0, 100_000)  # DELETE

    tables_dict[table_ind] = Table(table_id=table_ind)
    return {"status": 200, "added": table_ind}


@router.get("/tables/{table_id}", response_class=HTMLResponse)
def get_table_info(request: Request, table_id: int):
    table = tables_dict.get(table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    data = _serialize_table(table)
    data.update(
        {
            "players_list": [
                {
                    "user_id": player.user_id,
                    "stack": player.stack,
                    "status": player.status.value,
                    "position": player.position,
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
        }
    )
    return templates.TemplateResponse(
        "table_detail.html",
        {"request": request, "table": data},
    )


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
    return {
        "table_id": table.table_id,
        "max_players": table.max_players,
        "players": len(table.players),
        "spectators": len(table.spectators),
        "small_blind": table.small_blind,
        "big_blind": table.big_blind,
        "status": phase or "waiting",
    }
