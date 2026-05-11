from __future__ import annotations

from dataclasses import dataclass
import random


RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = ("clubs", "diamonds", "hearts", "spades")


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        if self.rank == "A":
            return 11
        if self.rank in {"J", "Q", "K"}:
            return 10
        return int(self.rank)

    def display(self) -> str:
        return f"[{self.rank} {self.suit}]"


class Deck:
    def __init__(self, cards: list[Card]):
        self.cards = list(cards)

    @classmethod
    def standard(cls) -> Deck:
        return cls([Card(rank, suit) for suit in SUITS for rank in RANKS])

    def shuffle(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        rng.shuffle(self.cards)

    def deal(self) -> Card:
        if not self.cards:
            raise IndexError("cannot deal from an empty deck")
        return self.cards.pop()

    def __len__(self) -> int:
        return len(self.cards)
