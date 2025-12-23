from __future__ import annotations

from dataclasses import dataclass
from random import randint
from typing import Callable

from backend.poker_engine.table import Table


@dataclass(slots=True)
class TableRecord:
    table: Table
    buy_in: int
    private: bool


class TableStore:
    def __init__(self, *, id_factory: Callable[[], int] | None = None) -> None:
        self._records: dict[int, TableRecord] = {}
        self._id_factory = id_factory or (lambda: randint(0, 100_000))

    def list_items(self) -> list[tuple[int, TableRecord]]:
        return list(self._records.items())

    def get(self, table_id: int) -> TableRecord | None:
        return self._records.get(table_id)

    def delete(self, table_id: int) -> bool:
        return self._records.pop(table_id, None) is not None

    def delete_if_empty(self, table_id: int) -> bool:
        record = self._records.get(table_id)
        if record is None:
            return False
        if not record.table.is_effectively_empty():
            return False
        del self._records[table_id]
        return True

    def create(self, *, max_players: int, buy_in: int, private: bool) -> tuple[int, TableRecord]:
        table_id = self._id_factory()
        while table_id in self._records:
            table_id = self._id_factory()

        table = Table(table_id=table_id, max_players=max_players)
        record = TableRecord(table=table, buy_in=buy_in, private=private)
        self._records[table_id] = record
        return table_id, record


table_store = TableStore()
