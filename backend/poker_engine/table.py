from __future__ import annotations

from typing import List, Optional, Set

from backend.poker_engine.game_state import GameState, PlayerAction
from backend.poker_engine.player_state import PlayerState, PlayerStatus


class Table:
    def __init__(
            self,
            max_players: int = 9,
            small_blind: int = 50,
            big_blind: int = 100,
            table_id: int = 0
    ):
        self.max_players = max_players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players: List[PlayerState] = []
        self.spectators: List[PlayerState] = []
        self._pending_leave_user_ids: Set[int] = set()
        self.dealer = 0
        self.game_state: Optional[GameState] = None
        self.table_id = table_id

    def seat_player(self, user_id: int, stack: int, is_spectator: bool = False) -> PlayerState:
        if is_spectator:
            spectator = PlayerState(user_id=user_id, stack=-1, position=-1, status=PlayerStatus.SPECTATOR)
            self.spectators.append(spectator)
            return spectator

        if len(self.players) >= self.max_players:
            raise RuntimeError("The table is full.")
        position = len(self.players)
        player = PlayerState(user_id=user_id, stack=stack, position=position)
        self.players.append(player)
        return player

    def leave(self, user_id: int) -> int:
        self.spectators[:] = [spectator for spectator in self.spectators if spectator.user_id != user_id]

        player = next((p for p in self.players if p.user_id == user_id), None)
        if player is None:
            self._pending_leave_user_ids.discard(user_id)
            return 0

        cashout = max(0, int(getattr(player, "stack", 0)))
        if self.game_state is not None and bool(getattr(self.game_state, "hand_active", False)):
            self._pending_leave_user_ids.add(user_id)
            try:
                self.game_state.force_fold(player)
            except Exception:
                pass
            player.stack = 0
            if not bool(getattr(self.game_state, "hand_active", False)):
                self._advance_dealer_button()
                self._evict_pending_leavers()
            return cashout

        self._pending_leave_user_ids.discard(user_id)
        self.players[:] = [p for p in self.players if p.user_id != user_id]
        for idx, p in enumerate(self.players):
            p.position = idx
        return cashout

    def start_game(self) -> GameState:
        if len(self.players) < 2:
            raise RuntimeError("At least two players required to start.")
        self.game_state = GameState(
            players=self.players,
            dealer=self.dealer,
            small_blind=self.small_blind,
            big_blind=self.big_blind,
        )
        self.game_state.start_game()
        return self.game_state

    def apply_action(
            self,
            user_id: int,
            action: PlayerAction,
            amount: int = 0,
    ) -> None:
        if not self.game_state:
            raise RuntimeError("Game has not been started.")
        player = self._get_player_by_id(user_id)
        self.game_state.apply_action(player, action, amount)
        if not self.game_state.hand_active:
            self._advance_dealer_button()
            self._evict_pending_leavers()

    def public_players(self) -> list[PlayerState]:
        return [p for p in self.players if p.user_id not in self._pending_leave_user_ids]

    def public_spectators(self) -> list[PlayerState]:
        return list(self.spectators)

    def is_effectively_empty(self) -> bool:
        return not self.players and not self.spectators

    def _evict_pending_leavers(self) -> None:
        if not self._pending_leave_user_ids:
            return
        self.players[:] = [p for p in self.players if p.user_id not in self._pending_leave_user_ids]
        self._pending_leave_user_ids.clear()
        for idx, p in enumerate(self.players):
            p.position = idx

    def _advance_dealer_button(self) -> None:
        if not self.players:
            self.dealer = 0
            return
        next_index = (self.dealer + 1) % len(self.players)
        for _ in range(len(self.players)):
            player = self.players[next_index]
            if player.stack > 0 and player.status != PlayerStatus.SPECTATOR:
                self.dealer = next_index
                return
            next_index = (next_index + 1) % len(self.players)

    def _get_player_by_id(self, user_id: int) -> PlayerState:
        for player in self.players:
            if player.user_id == user_id:
                return player
        raise RuntimeError(f"Player with id {user_id} is not at the table.")
