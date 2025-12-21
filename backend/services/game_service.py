from __future__ import annotations

from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.poker_engine.table import Table
from backend.poker_engine.game_state import PlayerAction
from backend.poker_engine.player_state import PlayerState
from backend.models.finished_game import FinishedGame
from backend.models.player_game import PlayerGame
from backend.models.player_stats import PlayerStats, StatsDelta, update_stats


class GameService:
    def __init__(self) -> None:
        self._start_stacks: Dict[int, Dict[int, int]] = {}

    async def start_hand(self, table: Table) -> None:
        self._start_stacks[table.table_id] = {player.user_id: player.stack for player in table.players}
        table.start_game()

    async def apply_action(self, table: Table, user_id: int, action: PlayerAction, amount: int, db: AsyncSession) -> None:
        table.apply_action(user_id, action, amount)
        if not table.game_state.hand_active:
            await self._record_finished_hand(table, db)

    async def _record_finished_hand(self, table: Table, db: AsyncSession) -> None:
        game_state = table.game_state
        start_stacks = self._start_stacks.pop(table.table_id, None)
        if start_stacks is None:
            return
        winner_ids: List[int] = [p.user_id for p in (game_state.winners or [])]
        board_str = [str(card) for card in game_state.board]
        finished_game = FinishedGame(
            table_id=table.table_id,
            pot=game_state.pot,
            board=board_str,
            winners=winner_ids,
        )
        db.add(finished_game)
        await db.flush()
        for p in game_state.players:
            initial_stack = start_stacks.get(p.user_id, 0)
            net_delta = p.stack - initial_stack
            player_game = PlayerGame(
                finished_game_uuid=finished_game.uuid,
                table_id=table.table_id,
                user_id=p.user_id,
                hole_cards=[str(c) for c in p.hole_cards],
                bet=p.bet,
                net_stack_delta=net_delta,
                resulting_balance=p.stack,
                won_hand=p in game_state.winners if game_state.winners else False,
            )
            db.add(player_game)
            existing = await db.get(PlayerStats, p.user_id)
            if existing is None:
                existing = PlayerStats(user_id=p.user_id)
                db.add(existing)
                await db.flush()
            delta = StatsDelta(
                user_id=p.user_id,
                won_hand=p in game_state.winners if game_state.winners else False,
                bet=p.bet,
                net_stack_delta=net_delta,
                resulting_balance=p.stack,
            )
            update_stats(existing, [delta])
        await db.commit()