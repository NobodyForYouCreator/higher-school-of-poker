from fastapi import APIRouter
import json
from pathlib import Path
from random import randint

from backend.poker_engine.table import Table

router = APIRouter(tags=["table"])

tables_dict = {}


@router.get("/tables")
def tables():
    return {"status": 200, "tables": {el.table_id for el in tables_dict.values()}}


@router.post("/tables/create")
def create_table():
    table_ind = randint(0, 100_000)  # DELETE

    tables_dict[table_ind] = Table(table_id=table_ind)
    return {"status": 200, "added": table_ind}


@router.get("/tables/{id}")
def get_table_info(id: int):
    print(tables_dict)
    return {"info": tables_dict[id]}


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
