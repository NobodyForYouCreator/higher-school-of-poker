from fastapi import APIRouter
import json
from pathlib import Path

from backend.poker_engine.table import Table

router = APIRouter(tags=["table"])

tables_dict = {}
@router.get("/tables")
def tables():
    BASE_DIR = Path(__file__).resolve().parents[2]
    # parents[0] -> api
    # parents[1] -> rest_api
    # parents[2] -> backend

    TABLES_PATH = BASE_DIR / "temp_info" / "tables_list.json"

    with open(TABLES_PATH, 'r', encoding='utf-8') as f:
        tables = json.load(f)
    return {"status": 200, "tables": tables['tables_list']}


@router.get("/tables/create/")
def create_table(id: int):
    BASE_DIR = Path(__file__).resolve().parents[2]
    # parents[0] -> api
    # parents[1] -> rest_api
    # parents[2] -> backend

    TABLES_PATH = BASE_DIR / "temp_info" / "tables_list.json"

    with open(TABLES_PATH, 'r', encoding='utf-8') as f:
        tables = json.load(f)

    tables['tables_list'].append(id)

    with open(TABLES_PATH, 'w', encoding='utf-8') as f:
        json.dump(tables, f, indent=4, ensure_ascii=False)

    tables_dict[id] = Table(table_id=id)
    return {"status": 200, "added": id}


@router.get("/tables/")
def create_table(id: int):
    print(tables_dict)
    return {"info": tables_dict[id].table_id}
