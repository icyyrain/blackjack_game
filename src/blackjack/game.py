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
    SPLIT = "split"


@dataclass
class RoundResult:
    outcome: str
    chip_delta: float
    message: str
    hand_index: int | None = None


DeckFactory = Callable[[], list[Card] | Deck]


@dataclass
class BlackjackGame:
    starting_chips: float = 100
    deck_factory: DeckFactory | None = None
    chips: float = field(init=False)
    bet: float = field(default=0, init=False)
    deck: Deck = field(init=False)
    player_hand: Hand = field(default_factory=Hand, init=False)
    player_hands: list[Hand] = field(default_factory=list, init=False)
    hand_bets: list[float] = field(default_factory=list, init=False)
    hand_results: list[RoundResult] = field(default_factory=list, init=False)
    current_hand_index: int = field(default=0, init=False)
    split_active: bool = field(default=False, init=False)
    split_replacement_index: int = field(default=0, init=False)
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
        self.player_hands = [self.player_hand]
        self.hand_bets = [bet]
        self.hand_results = []
        self.current_hand_index = 0
        self.split_active = False
        self.split_replacement_index = 0
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

    def dealer_display(self) -> str:
        if not self.dealer_hand.cards:
            return "(none)"
        if self.phase == Phase.PLAYER_TURN:
            return f"{self.dealer_hand.cards[0].display()} [?]"
        return self.dealer_hand.display()

    def legal_actions(self) -> set[Action]:
        if self.phase != Phase.PLAYER_TURN:
            return set()
        actions = {Action.HIT, Action.STAND}
        if (
            not self.split_active
            and len(self.player_hand.cards) == 2
            and not self.player_has_acted
            and self.chips >= self.bet * 2
        ):
            actions.add(Action.DOUBLE)
            first, second = self.player_hand.cards
            if first.value == second.value:
                actions.add(Action.SPLIT)
        return actions

    def hit(self, auto_dealer: bool = True) -> RoundResult | None:
        self._require_action(Action.HIT)
        self.player_has_acted = True
        self.player_hand.add(self.deck.deal())
        self.log.append("Player hits.")
        if self.player_hand.is_bust:
            self.log.append(f"Hand {self.current_hand_index + 1} busts.")
            if not self.split_active:
                return self.settle_round()
            if self._advance_split_hand():
                return None
            if auto_dealer:
                return self.finish_player_turn()
            return self.begin_dealer_turn()
        return None

    def stand(self, auto_dealer: bool = True) -> RoundResult:
        self._require_action(Action.STAND)
        self.player_has_acted = True
        self.log.append(f"Hand {self.current_hand_index + 1} stands.")
        if self._advance_split_hand():
            return RoundResult("next_hand", 0, "Next split hand.", self.current_hand_index)
        if auto_dealer:
            return self.finish_player_turn()
        return self.begin_dealer_turn()

    def double_down(self, auto_dealer: bool = True) -> RoundResult:
        self._require_action(Action.DOUBLE)
        self.bet *= 2
        self.hand_bets[self.current_hand_index] = self.bet
        self.player_has_acted = True
        self.player_hand.add(self.deck.deal())
        self.log.append("Player doubles down.")
        if self.player_hand.is_bust:
            return self.settle_round()
        if not auto_dealer:
            return self.begin_dealer_turn()
        return self.finish_player_turn()

    def split(self, deal_replacements: bool = True) -> None:
        self._require_action(Action.SPLIT)
        first, second = self.player_hand.cards
        self.split_active = True
        self.player_hands = [Hand([first]), Hand([second])]
        self.hand_bets = [self.bet, self.bet]
        self.hand_results = []
        self.current_hand_index = 0
        self.player_hand = self.player_hands[0]
        self.player_has_acted = False
        self.split_replacement_index = 0
        if deal_replacements:
            self.deal_split_replacement()
            self.deal_split_replacement()
        self.log.append("Player splits.")

    def deal_split_replacement(self) -> Card:
        if not self.split_active or self.split_replacement_index >= len(self.player_hands):
            raise ValueError("no split hand needs a replacement card")
        hand = self.player_hands[self.split_replacement_index]
        card = self.deck.deal()
        hand.add(card)
        self.split_replacement_index += 1
        self.log.append(f"Hand {self.split_replacement_index} receives a card.")
        return card

    def finish_player_turn(self) -> RoundResult:
        self.begin_dealer_turn()
        self.dealer_play()
        return self.settle_round()

    def begin_dealer_turn(self) -> RoundResult:
        self.phase = Phase.DEALER_TURN
        return RoundResult("dealer_turn", 0, "Dealer turn.")

    def dealer_should_draw(self) -> bool:
        return self.phase == Phase.DEALER_TURN and self.dealer_hand.value < 17

    def dealer_draw(self) -> Card:
        if not self.dealer_should_draw():
            raise ValueError("dealer cannot draw now")
        card = self.deck.deal()
        self.dealer_hand.add(card)
        self.log.append("Dealer draws.")
        return card

    def finish_dealer_turn(self) -> RoundResult:
        if self.phase != Phase.DEALER_TURN:
            raise ValueError("dealer turn has not started")
        return self.settle_round()

    def dealer_play(self) -> None:
        self.phase = Phase.DEALER_TURN
        while self.dealer_hand.value < 17:
            self.dealer_draw()

    def settle_round(self) -> RoundResult:
        self.hand_results = [
            self._settle_hand(hand, bet, index) for index, (hand, bet) in enumerate(zip(self.player_hands, self.hand_bets))
        ]
        chip_delta = sum(result.chip_delta for result in self.hand_results)
        if len(self.hand_results) == 1:
            result = self.hand_results[0]
        else:
            summary = ", ".join(f"Hand {item.hand_index + 1}: {item.message}" for item in self.hand_results)
            result = RoundResult("split_settled", chip_delta, summary)

        self.chips += chip_delta
        self.phase = Phase.SETTLED
        self.result = result
        self.log.append(result.message)
        return result

    def _settle_hand(self, hand: Hand, bet: float, hand_index: int) -> RoundResult:
        natural_blackjack = not self.split_active and hand.is_blackjack
        if natural_blackjack and self.dealer_hand.is_blackjack:
            return RoundResult("push", 0, "Both sides have Blackjack. Push.", hand_index)
        if natural_blackjack:
            return RoundResult("player_blackjack", bet * 2, "Congratulations! You have Blackjack.", hand_index)
        if self.dealer_hand.is_blackjack:
            return RoundResult("dealer_blackjack", -bet, "Dealer has Blackjack.", hand_index)
        if hand.is_bust:
            return RoundResult("player_bust", -bet, "Player busts.", hand_index)
        if self.dealer_hand.is_bust:
            return RoundResult("dealer_bust", bet, "Dealer busts.", hand_index)
        if hand.value > self.dealer_hand.value:
            return RoundResult("player_win", bet, "Player wins.", hand_index)
        if hand.value < self.dealer_hand.value:
            return RoundResult("dealer_win", -bet, "Dealer wins.", hand_index)
        return RoundResult("push", 0, "Push.", hand_index)

    def _advance_split_hand(self) -> bool:
        if not self.split_active or self.current_hand_index >= len(self.player_hands) - 1:
            return False
        self.current_hand_index += 1
        self.player_hand = self.player_hands[self.current_hand_index]
        self.player_has_acted = False
        self.log.append(f"Playing hand {self.current_hand_index + 1}.")
        return True

    def _require_action(self, action: Action) -> None:
        if action not in self.legal_actions():
            raise ValueError(f"{action.value} is not legal now")
