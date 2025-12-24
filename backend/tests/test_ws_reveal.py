import asyncio

from backend.services.table_store import TableStore
from backend.services.game_service import GameService
from backend.ws_api import tables as ws_tables
from backend.poker_engine.game_state import PlayerAction


def test_ws_reveals_all_hole_cards_after_finish_even_if_player_left() -> None:
    async def _run() -> None:
        store = TableStore(id_factory=lambda: 1)
        ws_tables.table_store = store
        table_id, record = store.create(max_players=6, buy_in=1000, private=False)
        table = record.table

        table.seat_player(1, 1000)
        table.seat_player(2, 1000)

        service = GameService()
        await service.start_hand(table)
        assert table.game_state is not None
        assert table.game_state.hand_active is True

        table.leave(1)
        assert table.game_state is not None
        assert table.game_state.hand_active is False
        assert table.last_hand_snapshot is not None

        state = ws_tables._build_table_state(table_id, viewer_id=2, show_all=False)
        players = sorted(state["players"], key=lambda p: p["user_id"])
        assert [p["user_id"] for p in players] == [1, 2]
        assert all(p.get("hole_cards") and len(p["hole_cards"]) == 2 for p in players)

    asyncio.run(_run())

