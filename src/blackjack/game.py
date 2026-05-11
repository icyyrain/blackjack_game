from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from blackjack.cards import Card, Deck
from blackjack.rules import Hand


class Phase(str, Enum):
    BETTING = "betting"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    SETTLED = "settled"


class Action(str, Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"


@dataclass
class RoundResult:
    outcome: str
    chip_delta: float
    message: str


DeckFactory = Callable[[], list[Card] | Deck]


@dataclass
class BlackjackGame:
    starting_chips: float = 100
    deck_factory: DeckFactory | None = None
    chips: float = field(init=False)
    bet: float = field(default=0, init=False)
    deck: Deck = field(init=False)
    player_hand: Hand = field(default_factory=Hand, init=False)
    dealer_hand: Hand = field(default_factory=Hand, init=False)
    phase: Phase = field(default=Phase.BETTING, init=False)
    result: RoundResult | None = field(default=None, init=False)
    log: list[str] = field(default_factory=list, init=False)
    player_has_acted: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.chips = self.starting_chips
        self.deck = Deck([])

    def _new_deck(self) -> Deck:
        if self.deck_factory is None:
            deck = Deck.standard()
            deck.shuffle()
            return deck
        created = self.deck_factory()
        if isinstance(created, Deck):
            return created
        return Deck(created)

    def start_round(self, bet: float) -> None:
        if bet <= 0:
            raise ValueError("bet must be greater than zero")
        if bet > self.chips:
            raise ValueError("bet cannot exceed available chips")
        self.bet = bet
        self.deck = self._new_deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.result = None
        self.log = ["New round started."]
        self.player_has_acted = False
        self.phase = Phase.PLAYER_TURN

        self.player_hand.add(self.deck.deal())
        self.dealer_hand.add(self.deck.deal())
        self.player_hand.add(self.deck.deal())
        self.dealer_hand.add(self.deck.deal())

        if self.player_hand.is_blackjack or self.dealer_hand.is_blackjack:
            self.settle_round()

    def dealer_visible_cards(self) -> list[Card]:
        if self.phase == Phase.PLAYER_TURN:
            return self.dealer_hand.cards[:1]
        return list(self.dealer_hand.cards)

    def legal_actions(self) -> set[Action]:
        if self.phase != Phase.PLAYER_TURN:
            return set()
        actions = {Action.HIT, Action.STAND}
        if len(self.player_hand.cards) == 2 and not self.player_has_acted and self.chips >= self.bet * 2:
            actions.add(Action.DOUBLE)
        return actions

    def hit(self) -> RoundResult | None:
        self._require_action(Action.HIT)
        self.player_has_acted = True
        self.player_hand.add(self.deck.deal())
        self.log.append("Player hits.")
        if self.player_hand.is_bust:
            return self.settle_round()
        return None

    def stand(self) -> RoundResult:
        self._require_action(Action.STAND)
        self.player_has_acted = True
        self.phase = Phase.DEALER_TURN
        self.log.append("Player stands.")
        self.dealer_play()
        return self.settle_round()

    def double_down(self) -> RoundResult:
        self._require_action(Action.DOUBLE)
        self.bet *= 2
        self.player_has_acted = True
        self.player_hand.add(self.deck.deal())
        self.log.append("Player doubles down.")
        if self.player_hand.is_bust:
            return self.settle_round()
        self.phase = Phase.DEALER_TURN
        self.dealer_play()
        return self.settle_round()

    def dealer_play(self) -> None:
        self.phase = Phase.DEALER_TURN
        while self.dealer_hand.value < 17:
            self.dealer_hand.add(self.deck.deal())
            self.log.append("Dealer draws.")

    def settle_round(self) -> RoundResult:
        if self.player_hand.is_blackjack and self.dealer_hand.is_blackjack:
            result = RoundResult("push", 0, "Both sides have Blackjack. Push.")
        elif self.player_hand.is_blackjack:
            result = RoundResult("player_blackjack", self.bet * 1.5, "Blackjack pays 3:2.")
        elif self.dealer_hand.is_blackjack:
            result = RoundResult("dealer_blackjack", -self.bet, "Dealer has Blackjack.")
        elif self.player_hand.is_bust:
            result = RoundResult("player_bust", -self.bet, "Player busts.")
        elif self.dealer_hand.is_bust:
            result = RoundResult("dealer_bust", self.bet, "Dealer busts.")
        elif self.player_hand.value > self.dealer_hand.value:
            result = RoundResult("player_win", self.bet, "Player wins.")
        elif self.player_hand.value < self.dealer_hand.value:
            result = RoundResult("dealer_win", -self.bet, "Dealer wins.")
        else:
            result = RoundResult("push", 0, "Push.")

        self.chips += result.chip_delta
        self.phase = Phase.SETTLED
        self.result = result
        self.log.append(result.message)
        return result

    def _require_action(self, action: Action) -> None:
        if action not in self.legal_actions():
            raise ValueError(f"{action.value} is not legal now")
