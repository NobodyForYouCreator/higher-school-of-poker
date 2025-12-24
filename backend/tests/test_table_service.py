import asyncio

import pytest

from backend.models.user import User
from backend.rest.schemas.table import TableCreateRequest
from backend.services.table_service import InsufficientBalanceError, TableNotFoundError, TableService
from backend.services.table_store import TableStore


async def _noop_notify(_: int) -> None:
    return None


async def _noop_maybe_start(_: int) -> bool:
    return False


def _service_with_fixed_ids(ids: list[int]) -> TableService:
    it = iter(ids)
    store = TableStore(id_factory=lambda: next(it))
    return TableService(store, notify_table_changed=_noop_notify, maybe_start_game=_noop_maybe_start)


def _service_and_store_with_fixed_ids(ids: list[int]) -> tuple[TableService, TableStore]:
    it = iter(ids)
    store = TableStore(id_factory=lambda: next(it))
    service = TableService(store, notify_table_changed=_noop_notify, maybe_start_game=_noop_maybe_start)
    return service, store


class _FakeAsyncSession:
    def __init__(self, users: dict[int, User]) -> None:
        self.users = users

    async def get(self, model: type, pk: int) -> object | None:
        if model is User:
            return self.users.get(pk)
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


def test_create_list_get_join_leave_spectate() -> None:
    async def _run() -> None:
        service, store = _service_and_store_with_fixed_ids([123])
        db = _FakeAsyncSession(
            {
                1: User(id=1, username="u1", password_hash="x", balance=10_000),
                2: User(id=2, username="u2", password_hash="x", balance=10_000),
            }
        )

        created = service.create_table(TableCreateRequest(max_players=6, buy_in=5000, private=False))
        assert created.id == "123"
        assert created.players_count == 0
        assert created.spectators_count == 0

        tables = service.list_tables()
        assert [t.id for t in tables] == ["123"]

        detail0 = service.get_table_info(123)
        assert detail0.id == "123"
        assert detail0.seats == []

        ok = await service.join_table(123, user_id=1, db=db)
        assert ok.ok is True
        assert int(db.users[1].balance) == 5000

        detail1 = service.get_table_info(123)
        assert detail1.players_count == 1
        assert detail1.spectators_count == 0
        assert any(s.user_id == 1 and not s.is_spectator for s in detail1.seats)

        ok2 = await service.spectate_table(123, user_id=2, db=db)
        assert ok2.ok is True

        detail2 = service.get_table_info(123)
        assert detail2.players_count == 1
        assert detail2.spectators_count == 1
        assert any(s.user_id == 2 and s.is_spectator for s in detail2.seats)

        ok3 = await service.leave_table(123, user_id=1, db=db)
        assert ok3.ok is True
        assert int(db.users[1].balance) == 10_000
        detail3 = service.get_table_info(123)
        assert detail3.players_count == 0
        assert detail3.spectators_count == 1
        assert store.get(123) is not None

    asyncio.run(_run())


def test_table_not_found_errors() -> None:
    service = _service_with_fixed_ids([1])
    with pytest.raises(TableNotFoundError):
        service.get_table_info(999)


def test_table_auto_deleted_when_empty() -> None:
    async def _run() -> None:
        service, store = _service_and_store_with_fixed_ids([5])
        db = _FakeAsyncSession({1: User(id=1, username="u1", password_hash="x", balance=10_000)})
        service.create_table(TableCreateRequest(max_players=6, buy_in=5000, private=False))
        await service.join_table(5, user_id=1, db=db)
        assert store.get(5) is not None

        await service.leave_table(5, user_id=1, db=db)
        assert store.get(5) is None
        assert int(db.users[1].balance) == 10_000

    asyncio.run(_run())


def test_leave_mid_hand_forces_fold_and_eviction() -> None:
    async def _run() -> None:
        service, store = _service_and_store_with_fixed_ids([7])
        db = _FakeAsyncSession(
            {
                1: User(id=1, username="u1", password_hash="x", balance=10_000),
                2: User(id=2, username="u2", password_hash="x", balance=10_000),
            }
        )
        service.create_table(TableCreateRequest(max_players=6, buy_in=5000, private=False))
        await service.join_table(7, user_id=1, db=db)
        await service.join_table(7, user_id=2, db=db)

        record = store.get(7)
        assert record is not None
        record.table.start_game()
        assert record.table.game_state is not None
        assert record.table.game_state.hand_active is True

        before = int(db.users[1].balance)
        ok = await service.leave_table(7, user_id=1, db=db)
        assert ok.ok is True
        assert int(db.users[1].balance) > before
        assert record.table.game_state is not None
        assert record.table.game_state.hand_active is False
        assert [p.user_id for p in record.table.players] == [2]

    asyncio.run(_run())


def test_insufficient_balance_for_buy_in() -> None:
    async def _run() -> None:
        service, _store = _service_and_store_with_fixed_ids([9])
        db = _FakeAsyncSession({1: User(id=1, username="u1", password_hash="x", balance=1000)})
        service.create_table(TableCreateRequest(max_players=6, buy_in=5000, private=False))
        with pytest.raises(InsufficientBalanceError):
            await service.join_table(9, user_id=1, db=db)

    asyncio.run(_run())


def test_private_tables_are_not_listed() -> None:
    service = _service_with_fixed_ids([1, 2])
    service.create_table(TableCreateRequest(max_players=6, buy_in=5000, private=True))
    service.create_table(TableCreateRequest(max_players=6, buy_in=5000, private=False))
    tables = service.list_tables()
    assert [t.id for t in tables] == ["2"]
