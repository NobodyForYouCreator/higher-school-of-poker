import asyncio

from backend.models.player_stats import PlayerStats, StatsDelta, update_stats
from backend.services.game_service import GameService
from backend.poker_engine.game_state import PlayerAction
from backend.poker_engine.table import Table


class _FakeAsyncSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.stats_by_user: dict[int, PlayerStats] = {}

    def add(self, obj: object) -> None:
        self.added.append(obj)
        if isinstance(obj, PlayerStats):
            self.stats_by_user[obj.user_id] = obj

    async def flush(self) -> None:
        return None

    async def get(self, model: type, pk: int) -> object | None:
        if model is PlayerStats:
            return self.stats_by_user.get(pk)
        return None

    async def commit(self) -> None:
        return None


def test_update_stats_rules() -> None:
    stats = PlayerStats(user_id=1)
    update_stats(
        stats,
        [
            StatsDelta(user_id=1, won_hand=True, bet=100, net_stack_delta=50, resulting_balance=1550),
            StatsDelta(user_id=1, won_hand=False, bet=200, net_stack_delta=-75, resulting_balance=1475),
        ],
    )
    assert stats.hands_won == 1
    assert stats.hands_lost == 1
    assert stats.max_bet == 200
    assert stats.max_balance == 1550
    assert stats.won_stack == 50
    assert stats.lost_stack == 75


def test_game_service_updates_player_stats() -> None:
    async def _run() -> None:
        table = Table(table_id=1)
        table.seat_player(1, 1500)
        table.seat_player(2, 1500)
        gs = GameService()
        session = _FakeAsyncSession()

        await gs.start_hand(table)
        await gs.apply_action(table, 2, PlayerAction.FOLD, 0, session)  # triggers stats update + commit

        assert 1 in session.stats_by_user
        assert 2 in session.stats_by_user
        s1 = session.stats_by_user[1]
        s2 = session.stats_by_user[2]

        assert (s1.hands_won, s1.hands_lost) == (1, 0)
        assert (s2.hands_won, s2.hands_lost) == (0, 1)

        assert s1.won_stack > 0
        assert s2.lost_stack > 0

    asyncio.run(_run())

