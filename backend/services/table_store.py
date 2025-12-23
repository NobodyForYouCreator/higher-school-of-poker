from __future__ import annotations

from dataclasses import dataclass

from backend.poker_engine.table import Table


@dataclass(slots=True)
class TableRecord:
    table: Table
    buy_in: int
    private: bool


tables_dict: dict[int, TableRecord] = {}

