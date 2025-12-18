from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Iterable, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.poker_engine.player_state import PlayerState


class Suit(str, Enum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"


class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


RANK_ORDER = [
    Rank.TWO,
    Rank.THREE,
    Rank.FOUR,
    Rank.FIVE,
    Rank.SIX,
    Rank.SEVEN,
    Rank.EIGHT,
    Rank.NINE,
    Rank.TEN,
    Rank.JACK,
    Rank.QUEEN,
    Rank.KING,
    Rank.ACE,
]

RANK_VALUE = {rank: index + 2 for index, rank in enumerate(RANK_ORDER)}


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    @property
    def value(self) -> int:
        return RANK_VALUE[self.rank]

    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value[0].upper()}"


class HandRank(Enum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8


@dataclass(frozen=True)
class HandEvaluation:
    rank: HandRank
    kicker_values: tuple[int, ...]
    cards: tuple[Card, ...]

    def score(self) -> tuple[int, ...]:
        return (self.rank.value,) + self.kicker_values

    def __lt__(self, other: "HandEvaluation") -> bool:
        return self.score() < other.score()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HandEvaluation):
            return NotImplemented
        return self.score() == other.score()


class HandEvaluator:
    """Utility that evaluates best poker hand for a player."""

    @staticmethod
    def evaluate_best_hand(
        hole_cards: Sequence[Card],
        board_cards: Sequence[Card],
    ) -> HandEvaluation:
        combined = list(hole_cards) + list(board_cards)
        if len(combined) < 5:
            raise ValueError("At least 5 cards required to evaluate a hand.")
        best = None
        for combo in combinations(combined, 5):
            evaluation = HandEvaluator._classify_hand(combo)
            if best is None or best < evaluation:
                best = evaluation
        if best is None:
            raise RuntimeError("Unable to evaluate hand.")
        return best

    @staticmethod
    def determine_winners(
        players: Iterable["PlayerState"],
        board_cards: Sequence[Card],
    ) -> tuple[list["PlayerState"], HandEvaluation]:
        """Return winning players and the best board evaluation."""
        evaluations = []
        for player in players:
            evaluation = HandEvaluator.evaluate_best_hand(
                player.hole_cards, board_cards
            )
            evaluations.append((player, evaluation))
        if not evaluations:
            return [], HandEvaluation(HandRank.HIGH_CARD, (), tuple())
        # Find best score
        _, best_eval = max(evaluations, key=lambda item: item[1])
        winners = [
            player for player, evaluation in evaluations if evaluation == best_eval
        ]
        return winners, best_eval

    @staticmethod
    def _classify_hand(cards: Sequence[Card]) -> HandEvaluation:
        values = sorted((card.value for card in cards), reverse=True)
        suits = [card.suit for card in cards]
        counts = {value: values.count(value) for value in set(values)}
        ordered_cards = tuple(sorted(cards, reverse=True, key=lambda c: c.value))

        is_flush = len(set(suits)) == 1
        is_straight, straight_high = HandEvaluator._detect_straight(values)

        sorted_by_count = sorted(
            counts.items(), key=lambda item: (item[1], item[0]), reverse=True
        )

        if is_straight and is_flush:
            return HandEvaluation(HandRank.STRAIGHT_FLUSH, (straight_high,), ordered_cards)

        if sorted_by_count[0][1] == 4:
            quad_value = sorted_by_count[0][0]
            kicker = max(value for value in values if value != quad_value)
            return HandEvaluation(HandRank.FOUR_OF_A_KIND, (quad_value, kicker), ordered_cards)

        if sorted_by_count[0][1] == 3 and sorted_by_count[1][1] == 2:
            triple = sorted_by_count[0][0]
            pair = sorted_by_count[1][0]
            return HandEvaluation(HandRank.FULL_HOUSE, (triple, pair), ordered_cards)

        if is_flush:
            return HandEvaluation(HandRank.FLUSH, tuple(values), ordered_cards)

        if is_straight:
            return HandEvaluation(HandRank.STRAIGHT, (straight_high,), ordered_cards)

        if sorted_by_count[0][1] == 3:
            triple = sorted_by_count[0][0]
            kickers = tuple(value for value in values if value != triple)
            return HandEvaluation(HandRank.THREE_OF_A_KIND, (triple,) + kickers, ordered_cards)

        if sorted_by_count[0][1] == 2 and sorted_by_count[1][1] == 2:
            pair_high = max(sorted_by_count[0][0], sorted_by_count[1][0])
            pair_low = min(sorted_by_count[0][0], sorted_by_count[1][0])
            kicker = max(value for value in values if value not in (pair_high, pair_low))
            return HandEvaluation(
                HandRank.TWO_PAIR, (pair_high, pair_low, kicker), ordered_cards
            )

        if sorted_by_count[0][1] == 2:
            pair = sorted_by_count[0][0]
            kickers = tuple(value for value in values if value != pair)
            return HandEvaluation(
                HandRank.ONE_PAIR, (pair,) + kickers, ordered_cards
            )

        return HandEvaluation(HandRank.HIGH_CARD, tuple(values), ordered_cards)

    @staticmethod
    def _detect_straight(values: Sequence[int]) -> tuple[bool, int]:
        unique_values = sorted(set(values), reverse=True)
        # Handle wheel straight (A2345)
        if 14 in unique_values:
            unique_values.append(1)
        consecutive = 1
        best_high = None
        for index in range(1, len(unique_values)):
            if unique_values[index - 1] - 1 == unique_values[index]:
                consecutive += 1
                if consecutive >= 5:
                    best_high = unique_values[index - 4]
                    break
            else:
                consecutive = 1
        if best_high is None:
            return False, 0
        return True, best_high
