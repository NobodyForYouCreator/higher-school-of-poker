from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from backend.poker_engine.cards import Card


class PlayerStatus(str, Enum):
    ACTIVE = "active"
    FOLDED = "folded"
    ALL_IN = "all_in"
    OUT = "out"
    SPECTATOR = "spectator"


@dataclass
class PlayerState:
    user_id: int
    stack: int
    position: int
    status: PlayerStatus = PlayerStatus.ACTIVE
    hole_cards: List[Card] = field(default_factory=list)
    bet: int = 0
    last_action: Optional[str] = None
    is_small_blind: bool = False
    is_big_blind: bool = False
    has_acted_in_round: bool = False

    def reset_for_new_hand(self) -> None:
        if self.stack <= 0:
            self.status = PlayerStatus.OUT
        elif self.status != PlayerStatus.SPECTATOR:
            self.status = PlayerStatus.ACTIVE
        self.hole_cards.clear()
        self.bet = 0
        self.last_action = None
        self.is_small_blind = False
        self.is_big_blind = False
        self.has_acted_in_round = False

    def reset_for_betting_round(self) -> None:
        self.bet = 0
        self.has_acted_in_round = False

    def fold(self) -> None:
        if self.status == PlayerStatus.ACTIVE:
            self.status = PlayerStatus.FOLDED
            self.last_action = "fold"

    def check(self) -> None:
        self.last_action = "check"
        self.has_acted_in_round = True

    def call(self, amount: int) -> int:
        committed = self._commit(amount, allow_partial=True)
        self.last_action = "call"
        self.has_acted_in_round = True
        return committed

    def bet_chips(self, amount: int) -> int:
        committed = self._commit(amount, allow_partial=False)
        self.last_action = "bet"
        self.has_acted_in_round = True
        return committed

    def raise_bet(self, amount: int) -> int:
        committed = self._commit(amount, allow_partial=False)
        self.last_action = "raise"
        self.has_acted_in_round = True
        return committed

    def go_all_in(self) -> int:
        if self.stack <= 0:
            raise RuntimeError("Player has no chips left to go all-in.")
        committed = self._commit(self.stack, allow_partial=False)
        self.last_action = "all_in"
        self.has_acted_in_round = True
        return committed

    def _commit(self, amount: int, allow_partial: bool) -> int:
        if amount < 0:
            raise ValueError("Bet amount must be non-negative")
        if not allow_partial and amount > self.stack:
            raise ValueError("Not enough chips to commit requested amount")
        commit_amount = min(amount, self.stack)
        self.stack -= commit_amount
        self.bet += commit_amount
        if self.stack == 0 and self.status != PlayerStatus.SPECTATOR:
            self.status = PlayerStatus.ALL_IN
        return commit_amount

    def is_first_to_play(self, start_position: int) -> bool:
        return self.position == start_position

    def is_active_in_hand(self) -> bool:
        return self.status in (PlayerStatus.ACTIVE, PlayerStatus.ALL_IN)
