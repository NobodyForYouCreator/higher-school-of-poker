from random import shuffle

from backend.poker_engine.cards import Card, Rank, Suit


class Deck:
    def __init__(self) -> None:
        self.cards: list[Card] = []
        self.reset()

    def shuffle(self) -> None:
        shuffle(self.cards)

    def reset(self) -> None:
        self.cards = [Card(rank=rank, suit=suit) for suit in Suit for rank in Rank]
        self.shuffle()

    def draw_card(self) -> Card:
        if not self.cards:
            raise RuntimeError("Deck is empty.")
        return self.cards.pop()

    def draw_many_cards(self, amount: int) -> list[Card]:
        if amount > len(self.cards):
            raise RuntimeError("Not enough cards left in deck.")
        return [self.draw_card() for _ in range(amount)]
