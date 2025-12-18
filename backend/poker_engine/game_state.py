from __future__ import annotations

from enum import Enum
from typing import List, Optional

from backend.poker_engine.cards import Card, HandEvaluator
from backend.poker_engine.deck import Deck
from backend.poker_engine.player_state import PlayerState, PlayerStatus


class GamePhase(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"
    FINISHED = "finished"


class PlayerAction(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class GameState:
    """Manages a single hand of Texas Hold'em."""

    def __init__(
        self,
        players: List[PlayerState],
        dealer: int,
        small_blind: int = 50,
        big_blind: int = 100,
    ):
        if len(players) < 2:
            raise ValueError("At least two players are required to start a game.")

        self.players = players
        self.dealer_position = dealer % len(players)
        self.deck = Deck()
        self.board: List[Card] = []
        self.phase = GamePhase.FINISHED
        self.pot = 0
        self.small_blind_amount = small_blind
        self.big_blind_amount = big_blind
        self.minimum_raise = big_blind
        self.current_bet = 0
        self.current_player_index: Optional[int] = None
        self.small_blind_index = 0
        self.big_blind_index = 0
        self.last_raiser_index: Optional[int] = None
        self.hand_active = False
        self.winners: List[PlayerState] = []
        self.best_hand = None

    def start_game(self) -> None:
        """Prepare deck, deal cards and move to the preflop round."""
        eligible = [
            player
            for player in self.players
            if player.stack > 0 and player.status != PlayerStatus.SPECTATOR
        ]
        if len(eligible) < 2:
            raise RuntimeError("Not enough players with chips to start the game.")
        self._prepare_new_hand()
        self.phase = GamePhase.PREFLOP
        self.current_player_index = self._start_betting_round(
            self._next_index(self.big_blind_index), preserve_existing_bets=True
        )

    def apply_action(
        self,
        player: PlayerState,
        action: PlayerAction,
        amount: int = 0,
    ) -> None:
        """Apply user action to current betting round."""
        if not self.hand_active:
            raise RuntimeError("The hand is finished.")
        try:
            player_index = self.players.index(player)
        except ValueError as exc:
            raise RuntimeError("Player not seated at this table.") from exc
        if self.current_player_index is None:
            raise RuntimeError("No player should act right now.")
        if player_index != self.current_player_index:
            raise RuntimeError("It is not this player's turn.")
        if player.status not in (PlayerStatus.ACTIVE, PlayerStatus.ALL_IN):
            raise RuntimeError("Player cannot act right now.")

        if action == PlayerAction.FOLD:
            player.fold()
            player.has_acted_in_round = True
            if len(self._players_still_in_hand()) <= 1:
                self._finish_with_single_player()
                return
        elif action == PlayerAction.CHECK:
            if player.bet != self.current_bet:
                raise RuntimeError("Cannot check when facing a bet.")
            player.check()
        elif action == PlayerAction.CALL:
            required = self.current_bet - player.bet
            if required < 0:
                required = 0
            committed = player.call(required)
            self.pot += committed
        elif action == PlayerAction.BET:
            if self.current_bet != 0:
                raise RuntimeError("Betting is not available after someone has bet.")
            if amount < self.minimum_raise:
                raise RuntimeError("Bet amount is smaller than minimum bet.")
            committed = player.bet_chips(amount)
            self.current_bet = player.bet
            self.pot += committed
            self.minimum_raise = amount
            self.last_raiser_index = player_index
            self._reset_round_actions(except_index=player_index)
        elif action == PlayerAction.RAISE:
            if self.current_bet == 0:
                raise RuntimeError("No bet to raise.")
            if amount <= self.current_bet:
                raise RuntimeError("Raise must exceed current bet.")
            raise_size = amount - self.current_bet
            if raise_size < self.minimum_raise:
                raise RuntimeError("Raise is below minimum allowed size.")
            required = amount - player.bet
            committed = player.raise_bet(required)
            self.pot += committed
            self.current_bet = player.bet
            self.minimum_raise = raise_size
            self.last_raiser_index = player_index
            self._reset_round_actions(except_index=player_index)
        elif action == PlayerAction.ALL_IN:
            if player.stack <= 0:
                raise RuntimeError("Player cannot go all-in with zero stack.")
            committed = player.go_all_in()
            self.pot += committed
            if player.bet > self.current_bet:
                raise_size = player.bet - self.current_bet
                self.current_bet = player.bet
                if raise_size >= self.minimum_raise:
                    self.minimum_raise = raise_size
                    self.last_raiser_index = player_index
                    self._reset_round_actions(except_index=player_index)
            # If all-in did not reach current bet or raise size too small, action counts as call
        else:
            raise ValueError(f"Unsupported action {action}")

        self._advance_turn()

    def advance_phase(self) -> None:
        """Move to the next phase once betting is complete."""
        if not self.hand_active:
            return
        while True:
            if self.phase == GamePhase.PREFLOP:
                self.phase = GamePhase.FLOP
                self._deal_board_cards(3)
                start_index = self._next_index(self.dealer_position)
                self.current_player_index = self._start_betting_round(start_index)
            elif self.phase == GamePhase.FLOP:
                self.phase = GamePhase.TURN
                self._deal_board_cards(1)
                start_index = self._next_index(self.dealer_position)
                self.current_player_index = self._start_betting_round(start_index)
            elif self.phase == GamePhase.TURN:
                self.phase = GamePhase.RIVER
                self._deal_board_cards(1)
                start_index = self._next_index(self.dealer_position)
                self.current_player_index = self._start_betting_round(start_index)
            elif self.phase == GamePhase.RIVER:
                self.phase = GamePhase.SHOWDOWN
                self._run_showdown()
                return
            elif self.phase == GamePhase.SHOWDOWN:
                self.phase = GamePhase.FINISHED
                self.hand_active = False
                return
            else:
                return

            if self.current_player_index is not None:
                return
            # No players can act (all-in or folded). Proceed to next phase automatically.
            if self.phase in (GamePhase.SHOWDOWN, GamePhase.FINISHED):
                return
            continue

    # --- Helpers -----------------------------------------------------------------

    def _prepare_new_hand(self) -> None:
        self.deck.reset()
        self.board = []
        self.pot = 0
        self.winners = []
        self.best_hand = None
        self.hand_active = True
        for player in self.players:
            player.reset_for_new_hand()
        self.small_blind_index = self._next_eligible_index(self.dealer_position)
        self.big_blind_index = self._next_eligible_index(self.small_blind_index)
        self.players[self.small_blind_index].is_small_blind = True
        self.players[self.big_blind_index].is_big_blind = True
        self._post_blind(self.small_blind_index, self.small_blind_amount)
        self._post_blind(self.big_blind_index, self.big_blind_amount)
        self.current_bet = max(p.bet for p in self.players)
        self.minimum_raise = self.big_blind_amount
        self._deal_private_cards()

    def _post_blind(self, player_index: int, amount: int) -> None:
        player = self.players[player_index]
        if player.status in (PlayerStatus.OUT, PlayerStatus.SPECTATOR):
            return
        blind_amount = min(amount, player.stack) if player.stack > 0 else 0
        if blind_amount == 0:
            return
        committed = player.bet_chips(blind_amount)
        self.pot += committed

    def _deal_private_cards(self) -> None:
        for _ in range(2):
            for player in self.players:
                if player.status in (PlayerStatus.SPECTATOR, PlayerStatus.OUT):
                    continue
                player.hole_cards.append(self.deck.draw_card())

    def _deal_board_cards(self, amount: int) -> None:
        # Simulate burn
        self.deck.draw_card()
        self.board.extend(self.deck.draw_many_cards(amount))

    def _start_betting_round(
        self,
        start_index: int,
        preserve_existing_bets: bool = False,
    ) -> Optional[int]:
        if not preserve_existing_bets:
            for player in self.players:
                player.reset_for_betting_round()
            self.current_bet = 0
            self.minimum_raise = self.big_blind_amount
        for player in self.players:
            can_act = player.status == PlayerStatus.ACTIVE and player.stack >= 0
            player.has_acted_in_round = not can_act
        return self._find_next_player(start_index)

    def _advance_turn(self) -> None:
        if not self.hand_active:
            return
        if len(self._players_still_in_hand()) <= 1:
            self._finish_with_single_player()
            return
        if self._is_round_complete():
            self.current_player_index = None
            self.advance_phase()
            return
        next_index = self._find_next_player(self._next_index(self.current_player_index))
        self.current_player_index = next_index
        if self.current_player_index is None:
            self.advance_phase()

    def _is_round_complete(self) -> bool:
        active_players = [p for p in self.players if p.status == PlayerStatus.ACTIVE]
        if len(active_players) == 0:
            return True
        if len(active_players) == 1:
            return True
        for player in active_players:
            if not player.has_acted_in_round:
                return False
            if player.bet != self.current_bet:
                return False
        return True

    def _run_showdown(self) -> None:
        contenders = [
            player for player in self.players if player.is_active_in_hand()
        ]
        if not contenders:
            self.phase = GamePhase.FINISHED
            self.hand_active = False
            return
        winners, best_hand = HandEvaluator.determine_winners(contenders, self.board)
        self.winners = winners
        self.best_hand = best_hand
        self._distribute_pot(winners)
        self.phase = GamePhase.FINISHED
        self.hand_active = False

    def _distribute_pot(self, winners: List[PlayerState]) -> None:
        if not winners or self.pot == 0:
            return
        share = self.pot // len(winners)
        remainder = self.pot % len(winners)
        for index, winner in enumerate(winners):
            bonus = 1 if index < remainder else 0
            winner.stack += share + bonus
        self.pot = 0

    def _finish_with_single_player(self) -> None:
        remaining = self._players_still_in_hand()
        if not remaining:
            self.hand_active = False
            self.phase = GamePhase.FINISHED
            return
        winner = remaining[0]
        winner.stack += self.pot
        self.winners = [winner]
        self.pot = 0
        self.hand_active = False
        self.phase = GamePhase.FINISHED

    def _find_next_player(self, start_index: int) -> Optional[int]:
        if not self.players:
            return None
        index = start_index % len(self.players)
        for _ in range(len(self.players)):
            player = self.players[index]
            can_act = player.status == PlayerStatus.ACTIVE and not player.has_acted_in_round
            if can_act:
                return index
            index = self._next_index(index)
        return None

    def _count_active_players(self) -> int:
        return sum(1 for player in self.players if player.status == PlayerStatus.ACTIVE)

    def _players_still_in_hand(self) -> List[PlayerState]:
        return [
            player
            for player in self.players
            if player.status in (PlayerStatus.ACTIVE, PlayerStatus.ALL_IN)
        ]

    def _next_index(self, index: int) -> int:
        return (index + 1) % len(self.players)

    def _next_eligible_index(self, from_index: int) -> int:
        index = self._next_index(from_index)
        for _ in range(len(self.players)):
            player = self.players[index]
            if player.status not in (PlayerStatus.OUT, PlayerStatus.SPECTATOR) and player.stack > 0:
                return index
            index = self._next_index(index)
        raise RuntimeError("Unable to find eligible player for blinds.")

    def _reset_round_actions(self, except_index: Optional[int] = None) -> None:
        for idx, player in enumerate(self.players):
            if idx == except_index:
                player.has_acted_in_round = True
                continue
            if player.status == PlayerStatus.ACTIVE:
                player.has_acted_in_round = False
            else:
                player.has_acted_in_round = True
