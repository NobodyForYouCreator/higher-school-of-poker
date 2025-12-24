from __future__ import annotations

from typing import Awaitable, Callable

from backend.rest.schemas.common import OkResponse
from backend.rest.schemas.table import TableCreateRequest, TableDetail, TableSeat, TableSummary
from backend.models.user import User
from backend.services.table_store import TableRecord, TableStore
from backend.poker_engine.player_state import PlayerStatus
from sqlalchemy.ext.asyncio import AsyncSession


class TableNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InsufficientBalanceError(Exception):
    pass


class TableService:
    def __init__(
        self,
        store: TableStore,
        *,
        notify_table_changed: Callable[[int], Awaitable[None]],
        maybe_start_game: Callable[[int], Awaitable[bool]],
    ) -> None:
        self._store = store
        self._notify_table_changed = notify_table_changed
        self._maybe_start_game = maybe_start_game

    def list_tables(self, *, include_private: bool = False) -> list[TableSummary]:
        items = self._store.list_items()
        if not include_private:
            items = [(table_id, record) for table_id, record in items if not record.private]
        return [self._serialize_summary(table_id, record) for table_id, record in items]

    def create_table(self, payload: TableCreateRequest) -> TableSummary:
        table_id, record = self._store.create(
            max_players=payload.max_players,
            buy_in=payload.buy_in,
            private=payload.private,
        )
        return self._serialize_summary(table_id, record)

    def get_table_info(self, table_id: int) -> TableDetail:
        record = self._require(table_id)
        return self._serialize_detail(table_id, record)

    async def join_table(self, table_id: int, *, user_id: int, db: AsyncSession) -> OkResponse:
        record = self._require(table_id)
        user = await self._require_user(db, user_id)

        cashout = record.table.leave(user_id)
        if cashout:
            user.balance = int(user.balance) + cashout

        if int(user.balance) < int(record.buy_in):
            raise InsufficientBalanceError("Not enough balance for buy-in")

        waiting = bool(record.table.game_state is not None and getattr(record.table.game_state, "hand_active", False))
        record.table.seat_player(user_id, record.buy_in, initial_status=PlayerStatus.WAITING if waiting else None)
        user.balance = int(user.balance) - int(record.buy_in)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            record.table.leave(user_id)
            raise
        await self._notify_table_changed(table_id)
        await self._maybe_start_game(table_id)
        return OkResponse()

    async def leave_table(self, table_id: int, *, user_id: int, db: AsyncSession) -> OkResponse:
        record = self._require(table_id)
        await self._cashout_user(db, record, user_id)
        self._store.delete_if_empty(table_id)
        await self._notify_table_changed(table_id)
        return OkResponse()

    async def spectate_table(self, table_id: int, *, user_id: int, db: AsyncSession) -> OkResponse:
        record = self._require(table_id)
        await self._cashout_user(db, record, user_id)
        record.table.seat_player(user_id, record.buy_in, is_spectator=True)
        await self._notify_table_changed(table_id)
        return OkResponse()

    def _require(self, table_id: int) -> TableRecord:
        record = self._store.get(table_id)
        if record is None:
            raise TableNotFoundError(f"Table not found: {table_id}")
        return record

    @staticmethod
    async def _require_user(db: AsyncSession, user_id: int) -> User:
        user = await db.get(User, user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        return user

    async def _cashout_user(self, db: AsyncSession, record: TableRecord, user_id: int) -> int:
        user = await self._require_user(db, user_id)
        cashout = record.table.leave(user_id)
        if not cashout:
            return 0
        user.balance = int(user.balance) + cashout
        await db.commit()
        return cashout

    @staticmethod
    def _serialize_summary(table_id: int, record: TableRecord) -> TableSummary:
        players = record.table.public_players()
        spectators = record.table.public_spectators()
        return TableSummary(
            id=str(table_id),
            max_players=record.table.max_players,
            buy_in=record.buy_in,
            private=record.private,
            players_count=len(players),
            spectators_count=len(spectators),
        )

    def _serialize_detail(self, table_id: int, record: TableRecord) -> TableDetail:
        info = self._serialize_summary(table_id, record)
        seats: list[TableSeat] = [
            TableSeat(position=player.position, user_id=player.user_id, stack=player.stack, is_spectator=False)
            for player in record.table.public_players()
        ] + [
            TableSeat(position=-1, user_id=spectator.user_id, stack=spectator.stack, is_spectator=True)
            for spectator in record.table.public_spectators()
        ]
        return TableDetail(**info.model_dump(), seats=seats)
