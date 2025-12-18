from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.poker_engine.cards import Card, HandEvaluator, HandRank, Rank, Suit
from backend.poker_engine.deck import Deck
from backend.poker_engine.game_state import GamePhase, GameState, PlayerAction
from backend.poker_engine.player_state import PlayerState, PlayerStatus
from backend.poker_engine.table import Table


RANK_MAP = {r.value: r for r in Rank}
SUIT_MAP = {
    "H": Suit.HEARTS,
    "D": Suit.DIAMONDS,
    "C": Suit.CLUBS,
    "S": Suit.SPADES,
}


def c(code: str) -> Card:
    code = code.strip().upper()
    if len(code) != 2:
        raise ValueError(f"Card code must be 2 chars like 'AH', got: {code!r}")
    return Card(rank=RANK_MAP[code[0]], suit=SUIT_MAP[code[1]])


def cards(text: str) -> List[Card]:
    return [c(tok) for tok in text.split() if tok.strip()]


def rig_deck(game: GameState, draw_sequence: Iterable[Card]) -> None:
    seq = list(draw_sequence)
    fixed_cards = list(reversed(seq))

    game.deck.shuffle = lambda: None
    game.deck.reset = lambda: setattr(game.deck, "cards", fixed_cards.copy())


@pytest.fixture
def heads_up_game_rigged_aa_vs_kk() -> tuple[GameState, PlayerState, PlayerState]:
    p0 = PlayerState(user_id=1, stack=1000, position=0)
    p1 = PlayerState(user_id=2, stack=1000, position=1)

    game = GameState(players=[p0, p1], dealer=0, small_blind=50, big_blind=100)

    seq = cards("AS KH AD KC  3D  2H 7C 9D  4S  JS  5C  QH")
    rig_deck(game, seq)
    return game, p0, p1


@pytest.mark.parametrize(
    "hole, board, expected_rank, expected_kickers",
    [
        ("AS KS", "QS JS TS 2H 3C", HandRank.STRAIGHT_FLUSH, (14,)), # стрит-флеш (A-high)
        ("AH AD", "AC AS KH 2D 3C", HandRank.FOUR_OF_A_KIND, (14, 13)), # каре тузов + кикер K
        ("KH KS", "KD 2H 2S 5C 6D", HandRank.FULL_HOUSE, (13, 2)), # фулл-хаус KKK22
        ("AH 9H", "KH 7H 2H QC 3S", HandRank.FLUSH, (14, 13, 9, 7, 2)), # флеш
        ("AS 2D", "3H 4C 5S KD QD", HandRank.STRAIGHT, (5,)), # wheel straight (A2345 => high=5)
        ("QH QS", "QD AC 9S 2D 3C", HandRank.THREE_OF_A_KIND, (12, 14, 9)), # сет дам + A9
        ("AH AC", "KH KC 9D 2S 3C", HandRank.TWO_PAIR, (14, 13, 9)), # две пары AA KK + 9
        ("AH AC", "KH QC JS 9D 2C", HandRank.ONE_PAIR, (14, 13, 12, 11)), # пара AA + KQJ
        ("AH 7C", "KS QD 9H 3C 2D", HandRank.HIGH_CARD, (14, 13, 12, 9, 7)), # хай-кард
    ],
)
def test_hand_evaluator_classification(hole, board, expected_rank, expected_kickers) -> None:
    ev = HandEvaluator.evaluate_best_hand(cards(hole), cards(board))
    assert ev.rank == expected_rank
    assert ev.kicker_values == expected_kickers


def test_hand_evaluation_comparison_and_eq() -> None:
    flush = HandEvaluator.evaluate_best_hand(cards("AH 9H"), cards("KH 7H 2H QC 3S"))
    straight = HandEvaluator.evaluate_best_hand(cards("AS 2D"), cards("3H 4C 5S KD QD"))
    assert flush > straight
    assert not (flush < straight)
    assert flush != straight

    a = HandEvaluator.evaluate_best_hand(cards("2H 3D"), cards("TS JH QD KC AS"))
    b = HandEvaluator.evaluate_best_hand(cards("4C 5C"), cards("TS JH QD KC AS"))
    assert a == b


def test_determine_winners_split_pot_tie_hand() -> None:
    board = cards("TS JH QD KC AS")
    p1 = PlayerState(user_id=1, stack=1000, position=0, hole_cards=cards("2H 3D"))
    p2 = PlayerState(user_id=2, stack=1000, position=1, hole_cards=cards("4C 5C"))

    winners, best = HandEvaluator.determine_winners([p1, p2], board)
    assert best.rank == HandRank.STRAIGHT
    assert {p.user_id for p in winners} == {1, 2}


def test_deck_reset_has_52_unique_cards() -> None:
    deck = Deck()
    assert len(deck.cards) == 52
    assert len(set(deck.cards)) == 52


def test_deck_draw_card_and_draw_many() -> None:
    deck = Deck()
    n0 = len(deck.cards)
    x = deck.draw_card()
    assert isinstance(x, Card)
    assert len(deck.cards) == n0 - 1

    many = deck.draw_many_cards(3)
    assert len(many) == 3
    assert len(deck.cards) == n0 - 1 - 3


def test_deck_errors() -> None:
    deck = Deck()
    deck.cards = []
    with pytest.raises(RuntimeError, match="Deck is empty"):
        deck.draw_card()

    deck.reset()
    with pytest.raises(RuntimeError, match="Not enough cards"):
        deck.draw_many_cards(10_000)


def test_player_commit_rules_and_all_in_status() -> None:
    p = PlayerState(user_id=1, stack=10, position=0)

    with pytest.raises(ValueError, match="non-negative"):
        p.call(-1)

    with pytest.raises(ValueError, match="Not enough chips"):
        p.bet_chips(999)

    p2 = PlayerState(user_id=2, stack=10, position=1)
    committed = p2.call(20)
    assert committed == 10
    assert p2.stack == 0
    assert p2.bet == 10
    assert p2.status == PlayerStatus.ALL_IN


def test_player_reset_for_new_hand_sets_out_if_stack_zero() -> None:
    p = PlayerState(user_id=1, stack=0, position=0)
    p.hole_cards = cards("AS KD")
    p.bet = 123
    p.status = PlayerStatus.ACTIVE

    p.reset_for_new_hand()
    assert p.status == PlayerStatus.OUT
    assert p.hole_cards == []
    assert p.bet == 0


def test_game_state_init_requires_two_players() -> None:
    with pytest.raises(ValueError, match="At least two"):
        GameState(players=[PlayerState(1, 1000, 0)], dealer=0)


def test_start_game_requires_two_eligible_players() -> None:
    p0 = PlayerState(1, 1000, 0, status=PlayerStatus.SPECTATOR)
    p1 = PlayerState(2, 1000, 1, status=PlayerStatus.ACTIVE)
    game = GameState([p0, p1], dealer=0)

    with pytest.raises(RuntimeError, match="Not enough players"):
        game.start_game()


def test_preflop_blinds_posted_and_turn_order(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    assert game.small_blind_index == 1
    assert game.big_blind_index == 0
    assert game.pot == 150
    assert game.current_bet == 100

    assert game.current_player_index == 1

    assert [str(x) for x in p0.hole_cards] == ["AS", "AD"]
    assert [str(x) for x in p1.hole_cards] == ["KH", "KC"]


def test_fold_finishes_hand_and_awards_pot(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    game.apply_action(p1, PlayerAction.FOLD)

    assert game.phase == GamePhase.FINISHED
    assert not game.hand_active
    assert game.pot == 0
    assert len(game.winners) == 1
    assert game.winners[0].user_id == p0.user_id

    assert p0.stack == 1050
    assert p1.stack == 950


def test_illegal_check_when_facing_bet(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    with pytest.raises(RuntimeError, match="Cannot check when facing a bet"):
        game.apply_action(p1, PlayerAction.CHECK)


def test_bet_not_allowed_when_current_bet_nonzero(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    with pytest.raises(RuntimeError, match="Betting is not available"):
        game.apply_action(p1, PlayerAction.BET, amount=200)


def test_raise_rules_and_errors(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    with pytest.raises(RuntimeError, match="Raise must exceed current bet"):
        game.apply_action(p1, PlayerAction.RAISE, amount=100)

    game.apply_action(p1, PlayerAction.RAISE, amount=300)
    assert game.current_bet == 300
    assert game.pot > 150

    with pytest.raises(RuntimeError, match="Raise is below minimum allowed size"):
        game.apply_action(p0, PlayerAction.RAISE, amount=350)


def test_raise_when_no_bet_to_raise(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    game.apply_action(p1, PlayerAction.CALL)
    game.apply_action(p0, PlayerAction.CHECK)

    assert game.phase == GamePhase.FLOP
    assert game.current_bet == 0

    idx = game.current_player_index
    assert idx is not None
    to_act = game.players[idx]
    with pytest.raises(RuntimeError, match="No bet to raise"):
        game.apply_action(to_act, PlayerAction.RAISE, amount=200)


def test_all_in_auto_advance_to_showdown(heads_up_game_rigged_aa_vs_kk) -> None:
    game, p0, p1 = heads_up_game_rigged_aa_vs_kk
    game.start_game()

    game.apply_action(p1, PlayerAction.ALL_IN)
    game.apply_action(p0, PlayerAction.ALL_IN)

    assert game.phase == GamePhase.FINISHED
    assert not game.hand_active
    assert len(game.winners) == 1
    assert game.winners[0].user_id == 1
    assert p0.stack == 2000
    assert p1.stack == 0


def test_distribute_pot_remainder_branch() -> None:
    p0 = PlayerState(user_id=1, stack=0, position=0)
    p1 = PlayerState(user_id=2, stack=0, position=1)
    game = GameState(players=[p0, p1], dealer=0)

    game.pot = 5
    game._distribute_pot([p0, p1])

    assert p0.stack == 3
    assert p1.stack == 2
    assert game.pot == 0


def test_table_seat_leave_and_positions() -> None:
    t = Table(max_players=5)
    p0 = t.seat_player(1, 1000)
    p1 = t.seat_player(2, 1000)
    p2 = t.seat_player(3, 1000)

    assert [p.position for p in t.players] == [0, 1, 2]

    t.leave(user_id=2)
    assert [p.user_id for p in t.players] == [1, 3]
    assert [p.position for p in t.players] == [0, 1]


def test_table_full_raises() -> None:
    t = Table(max_players=2)
    t.seat_player(1, 1000)
    t.seat_player(2, 1000)
    with pytest.raises(RuntimeError, match="table is full"):
        t.seat_player(3, 1000)


def test_table_start_game_requires_two_players() -> None:
    t = Table()
    t.seat_player(1, 1000)
    with pytest.raises(RuntimeError, match="At least two"):
        t.start_game()


def test_table_apply_action_requires_started() -> None:
    t = Table()
    t.seat_player(1, 1000)
    t.seat_player(2, 1000)
    with pytest.raises(RuntimeError, match="Game has not been started"):
        t.apply_action(1, PlayerAction.CHECK)


def test_table_advances_dealer_after_hand_finished() -> None:
    t = Table()
    t.seat_player(1, 1000)
    t.seat_player(2, 1000)
    t.seat_player(3, 1000)

    assert t.dealer == 0

    t.start_game()
    gs = t.game_state
    assert gs is not None
    assert gs.hand_active

    t.apply_action(1, PlayerAction.FOLD)

    while gs.hand_active:
        idx = gs.current_player_index
        assert idx is not None
        pl = gs.players[idx]
        t.apply_action(pl.user_id, PlayerAction.FOLD)
    assert t.dealer == 1
