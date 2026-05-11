# Blackjack Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested single-player Blackjack game with a terminal interface first and a lightweight tkinter GUI second.

**Architecture:** Keep Blackjack rules in a UI-free Python package under `src/blackjack`. The CLI and GUI both call the same `BlackjackGame` engine so deck behavior, legal actions, and settlement rules have one source of truth.

**Tech Stack:** Python 3.11 or newer, pytest, conda, tkinter from the Python distribution.

---

## File Structure

- Create `environment.yml`: conda environment named `blackjack-game` with Python and pytest.
- Create `pyproject.toml`: package metadata and pytest configuration.
- Create `README.md`: setup and run commands.
- Create `src/blackjack/__init__.py`: package exports.
- Create `src/blackjack/cards.py`: `Card`, `Deck`, ranks, suits, and card values.
- Create `src/blackjack/rules.py`: `Hand`, hand scoring, Blackjack, and bust helpers.
- Create `src/blackjack/game.py`: `BlackjackGame`, round phases, legal actions, dealer play, and payouts.
- Create `src/blackjack/cli.py`: terminal loop.
- Create `src/blackjack/gui.py`: tkinter app.
- Create `tests/test_cards.py`: deck and dealing behavior.
- Create `tests/test_rules.py`: hand scoring behavior.
- Create `tests/test_game.py`: game flow and payout behavior.

## Commands

Use these commands from `C:\Projects\black_jack`.

- Create/update environment: `conda env update -f environment.yml --prune`
- Run tests: `conda run -n blackjack-game pytest`
- Run terminal game: `conda run -n blackjack-game python -m blackjack.cli`
- Run GUI: `conda run -n blackjack-game python -m blackjack.gui`

If `conda` is not available, first inspect the local installation with `where conda` and `where python`, then use the available Python only for temporary verification.

### Task 1: Project Scaffolding

**Files:**
- Create: `environment.yml`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/blackjack/__init__.py`

- [ ] **Step 1: Create directories**

Run: `New-Item -ItemType Directory -Force -Path src/blackjack, tests`

Expected: both directories exist.

- [ ] **Step 2: Write environment and package files**

`environment.yml`:

```yaml
name: blackjack-game
channels:
  - conda-forge
dependencies:
  - python>=3.11
  - pytest>=8
```

`pyproject.toml`:

```toml
[project]
name = "blackjack-game"
version = "0.1.0"
description = "A single-player Blackjack game with terminal and tkinter interfaces."
requires-python = ">=3.11"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

`README.md`:

````markdown
# Blackjack Game

Single-player Blackjack against a dealer.

## Setup

```powershell
conda env update -f environment.yml --prune
```

## Test

```powershell
conda run -n blackjack-game pytest
```

## Play in Terminal

```powershell
conda run -n blackjack-game python -m blackjack.cli
```

## Play GUI

```powershell
conda run -n blackjack-game python -m blackjack.gui
```
````

`src/blackjack/__init__.py`:

````python
"""Blackjack game package."""
````

- [ ] **Step 3: Create or update the conda environment**

Run: `conda env update -f environment.yml --prune`

Expected: command succeeds and reports the `blackjack-game` environment is ready.

- [ ] **Step 4: Verify the package can import**

Run: `conda run -n blackjack-game python -c "import blackjack; print(blackjack.__doc__)"`

Expected: prints `Blackjack game package.`

- [ ] **Step 5: Commit**

Run:

```powershell
git add environment.yml pyproject.toml README.md src/blackjack/__init__.py
git commit -m "Add Python project scaffold"
```

### Task 2: Cards and Deck

**Files:**
- Create: `src/blackjack/cards.py`
- Test: `tests/test_cards.py`

- [ ] **Step 1: Write failing deck tests**

`tests/test_cards.py`:

```python
from blackjack.cards import Card, Deck


def test_new_deck_contains_52_unique_cards():
    deck = Deck.standard()

    assert len(deck.cards) == 52
    assert len(set(deck.cards)) == 52


def test_shuffle_preserves_same_cards_but_can_change_order():
    deck = Deck.standard()
    before = set(deck.cards)

    deck.shuffle(seed=7)

    assert set(deck.cards) == before
    assert len(deck.cards) == 52


def test_deal_pops_from_top_of_deck():
    top = Card("A", "spades")
    bottom = Card("9", "hearts")
    deck = Deck([bottom, top])

    dealt = deck.deal()

    assert dealt == top
    assert deck.cards == [bottom]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda run -n blackjack-game pytest tests/test_cards.py -v`

Expected: FAIL with `ModuleNotFoundError` or missing `blackjack.cards`.

- [ ] **Step 3: Implement cards and deck**

`src/blackjack/cards.py`:

```python
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
    def standard(cls) -> "Deck":
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda run -n blackjack-game pytest tests/test_cards.py -v`

Expected: all three tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/blackjack/cards.py tests/test_cards.py
git commit -m "Add card and deck model"
```

### Task 3: Hand Rules

**Files:**
- Create: `src/blackjack/rules.py`
- Test: `tests/test_rules.py`

- [ ] **Step 1: Write failing hand tests**

`tests/test_rules.py`:

```python
from blackjack.cards import Card
from blackjack.rules import Hand


def test_hand_totals_number_and_face_cards():
    hand = Hand([Card("10", "spades"), Card("K", "hearts")])

    assert hand.value == 20
    assert not hand.is_bust


def test_ace_counts_as_eleven_when_safe():
    hand = Hand([Card("A", "spades"), Card("9", "hearts")])

    assert hand.value == 20


def test_ace_falls_back_to_one_to_avoid_bust():
    hand = Hand([Card("A", "spades"), Card("9", "hearts"), Card("5", "clubs")])

    assert hand.value == 15


def test_blackjack_requires_two_card_twenty_one():
    assert Hand([Card("A", "spades"), Card("K", "hearts")]).is_blackjack
    assert not Hand([Card("A", "spades"), Card("5", "hearts"), Card("5", "clubs")]).is_blackjack


def test_bust_is_value_over_twenty_one():
    hand = Hand([Card("K", "spades"), Card("9", "hearts"), Card("5", "clubs")])

    assert hand.value == 24
    assert hand.is_bust
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda run -n blackjack-game pytest tests/test_rules.py -v`

Expected: FAIL with missing `blackjack.rules`.

- [ ] **Step 3: Implement hand rules**

`src/blackjack/rules.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field

from blackjack.cards import Card


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)

    def add(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def value(self) -> int:
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "A")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21

    @property
    def is_bust(self) -> bool:
        return self.value > 21

    def display(self) -> str:
        return " ".join(card.display() for card in self.cards)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda run -n blackjack-game pytest tests/test_rules.py -v`

Expected: all hand tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/blackjack/rules.py tests/test_rules.py
git commit -m "Add Blackjack hand rules"
```

### Task 4: Game Engine

**Files:**
- Create: `src/blackjack/game.py`
- Test: `tests/test_game.py`

- [ ] **Step 1: Write failing round setup tests**

Add to `tests/test_game.py`:

```python
from blackjack.cards import Card
from blackjack.game import BlackjackGame, Phase


def rigged_deck(cards):
    return list(cards)


def test_start_round_deals_two_cards_each_and_hides_dealer_hole_card():
    deck_cards = rigged_deck([
        Card("9", "clubs"),
        Card("8", "diamonds"),
        Card("7", "hearts"),
        Card("6", "spades"),
    ])
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: deck_cards)

    game.start_round(10)

    assert [card.rank for card in game.player_hand.cards] == ["6", "8"]
    assert [card.rank for card in game.dealer_hand.cards] == ["7", "9"]
    assert game.dealer_visible_cards() == [Card("7", "hearts")]
    assert game.phase == Phase.PLAYER_TURN
```

- [ ] **Step 2: Run setup test to verify it fails**

Run: `conda run -n blackjack-game pytest tests/test_game.py::test_start_round_deals_two_cards_each_and_hides_dealer_hole_card -v`

Expected: FAIL with missing `blackjack.game`.

- [ ] **Step 3: Implement minimal engine setup**

`src/blackjack/game.py`:

```python
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
        self.log = []
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

    def settle_round(self) -> RoundResult:
        self.phase = Phase.SETTLED
        self.result = RoundResult("push", 0, "Push.")
        return self.result
```

- [ ] **Step 4: Run setup test to verify it passes**

Run: `conda run -n blackjack-game pytest tests/test_game.py::test_start_round_deals_two_cards_each_and_hides_dealer_hole_card -v`

Expected: PASS.

- [ ] **Step 5: Write failing action and payout tests**

Replace `tests/test_game.py` with:

```python
from blackjack.cards import Card
from blackjack.game import Action, BlackjackGame, Phase


def test_start_round_deals_two_cards_each_and_hides_dealer_hole_card():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("9", "clubs"),
        Card("8", "diamonds"),
        Card("7", "hearts"),
        Card("6", "spades"),
    ])

    game.start_round(10)

    assert [card.rank for card in game.player_hand.cards] == ["6", "8"]
    assert [card.rank for card in game.dealer_hand.cards] == ["7", "9"]
    assert game.dealer_visible_cards() == [Card("7", "hearts")]
    assert game.phase == Phase.PLAYER_TURN


def test_hit_adds_one_card_and_bust_settles_round():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("K", "clubs"),
        Card("5", "diamonds"),
        Card("6", "clubs"),
        Card("9", "hearts"),
        Card("10", "spades"),
    ])

    game.start_round(10)
    game.hit()

    assert game.player_hand.value == 25
    assert game.phase == Phase.SETTLED
    assert game.result.outcome == "player_bust"
    assert game.chips == 90


def test_stand_runs_dealer_to_seventeen_and_player_wins_when_dealer_busts():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("K", "clubs"),
        Card("8", "diamonds"),
        Card("6", "clubs"),
        Card("10", "hearts"),
        Card("10", "spades"),
    ])

    game.start_round(10)
    game.stand()

    assert game.dealer_hand.value == 24
    assert game.result.outcome == "dealer_bust"
    assert game.chips == 110


def test_double_down_doubles_bet_deals_one_card_and_settles():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("K", "clubs"),
        Card("7", "diamonds"),
        Card("6", "clubs"),
        Card("5", "hearts"),
        Card("5", "spades"),
    ])

    game.start_round(10)
    game.double_down()

    assert game.bet == 20
    assert len(game.player_hand.cards) == 3
    assert game.phase == Phase.SETTLED
    assert game.result.outcome == "player_win"
    assert game.chips == 120


def test_double_down_is_unavailable_after_hit():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("2", "clubs"),
        Card("7", "diamonds"),
        Card("6", "clubs"),
        Card("5", "hearts"),
        Card("5", "spades"),
    ])

    game.start_round(10)
    game.hit()

    assert Action.DOUBLE not in game.legal_actions()


def test_player_blackjack_pays_three_to_two():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("9", "clubs"),
        Card("A", "diamonds"),
        Card("7", "clubs"),
        Card("K", "hearts"),
    ])

    game.start_round(10)

    assert game.phase == Phase.SETTLED
    assert game.result.outcome == "player_blackjack"
    assert game.chips == 115


def test_push_leaves_chips_unchanged():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("K", "clubs"),
        Card("10", "diamonds"),
        Card("Q", "clubs"),
        Card("J", "hearts"),
    ])

    game.start_round(10)

    assert game.result.outcome == "push"
    assert game.chips == 100
```

- [ ] **Step 6: Run action and payout tests to verify they fail**

Run: `conda run -n blackjack-game pytest tests/test_game.py -v`

Expected: FAIL with missing `hit`, `stand`, `double_down`, or incorrect settlement.

- [ ] **Step 7: Implement full engine**

Replace `src/blackjack/game.py` with:

```python
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
```

- [ ] **Step 8: Run full game tests to verify they pass**

Run: `conda run -n blackjack-game pytest tests/test_game.py -v`

Expected: all game tests pass.

- [ ] **Step 9: Run all tests**

Run: `conda run -n blackjack-game pytest`

Expected: all tests pass.

- [ ] **Step 10: Commit**

Run:

```powershell
git add src/blackjack/game.py tests/test_game.py
git commit -m "Add Blackjack game engine"
```

### Task 5: Terminal Interface

**Files:**
- Create: `src/blackjack/cli.py`

- [ ] **Step 1: Write CLI module**

`src/blackjack/cli.py`:

```python
from __future__ import annotations

from blackjack.game import Action, BlackjackGame, Phase


def format_cards(cards) -> str:
    return " ".join(card.display() for card in cards) or "(none)"


def print_state(game: BlackjackGame) -> None:
    print()
    print(f"Chips: {game.chips:g} | Bet: {game.bet:g} | Deck: {len(game.deck)} cards")
    print(f"Dealer: {format_cards(game.dealer_visible_cards())}")
    print(f"Player: {game.player_hand.display()} ({game.player_hand.value})")
    if game.result:
        print(f"Result: {game.result.message} Chip change: {game.result.chip_delta:g}")


def ask_bet(game: BlackjackGame) -> float | None:
    while True:
        raw = input(f"Bet amount, or quit (chips {game.chips:g}): ").strip().lower()
        if raw in {"q", "quit", "exit"}:
            return None
        try:
            bet = float(raw)
            if 0 < bet <= game.chips:
                return bet
        except ValueError:
            pass
        print("Enter a number greater than 0 and no more than your chips.")


def ask_action(game: BlackjackGame) -> Action:
    legal = game.legal_actions()
    labels = "/".join(action.value for action in sorted(legal, key=lambda item: item.value))
    while True:
        raw = input(f"Action ({labels}): ").strip().lower()
        for action in legal:
            if raw == action.value or raw == action.value[0]:
                return action
        print("Choose one of the listed actions.")


def main() -> None:
    game = BlackjackGame(starting_chips=100)
    print("Blackjack")

    while game.chips > 0:
        bet = ask_bet(game)
        if bet is None:
            break
        game.start_round(bet)

        while game.phase == Phase.PLAYER_TURN:
            print_state(game)
            action = ask_action(game)
            if action == Action.HIT:
                game.hit()
            elif action == Action.STAND:
                game.stand()
            elif action == Action.DOUBLE:
                game.double_down()

        print_state(game)
        print("-" * 40)

    print("Thanks for playing.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run import check**

Run: `conda run -n blackjack-game python -m blackjack.cli`

Expected: program starts and prompts for a bet. Exit with `quit`.

- [ ] **Step 3: Run tests**

Run: `conda run -n blackjack-game pytest`

Expected: all tests pass.

- [ ] **Step 4: Commit**

Run:

```powershell
git add src/blackjack/cli.py README.md
git commit -m "Add terminal Blackjack interface"
```

### Task 6: Tkinter GUI

**Files:**
- Create: `src/blackjack/gui.py`

- [ ] **Step 1: Verify tkinter import**

Run: `conda run -n blackjack-game python -c "import tkinter; print('tkinter ok')"`

Expected: prints `tkinter ok`.

- [ ] **Step 2: Write GUI module**

`src/blackjack/gui.py`:

```python
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from blackjack.game import Action, BlackjackGame, Phase


class BlackjackApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Blackjack")
        self.geometry("760x520")
        self.configure(bg="#14532d")
        self.game = BlackjackGame(starting_chips=100)

        self.status_var = tk.StringVar(value="Place a bet to start.")
        self.chips_var = tk.StringVar()
        self.bet_var = tk.StringVar(value="10")
        self.dealer_var = tk.StringVar()
        self.player_var = tk.StringVar()
        self.log_var = tk.StringVar()

        self._build()
        self._refresh()

    def _build(self) -> None:
        title = tk.Label(self, text="Blackjack", font=("Segoe UI", 24, "bold"), fg="white", bg="#14532d")
        title.pack(pady=12)

        info = tk.Frame(self, bg="#14532d")
        info.pack(fill="x", padx=24)
        tk.Label(info, textvariable=self.chips_var, font=("Segoe UI", 12), fg="white", bg="#14532d").pack(side="left")
        tk.Label(info, text="Bet:", font=("Segoe UI", 12), fg="white", bg="#14532d").pack(side="right")
        tk.Entry(info, textvariable=self.bet_var, width=8).pack(side="right", padx=8)

        self.dealer_label = tk.Label(self, textvariable=self.dealer_var, font=("Consolas", 16), fg="white", bg="#166534")
        self.dealer_label.pack(fill="x", padx=24, pady=16, ipady=18)

        tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 13), fg="white", bg="#14532d").pack(pady=6)

        self.player_label = tk.Label(self, textvariable=self.player_var, font=("Consolas", 16), fg="white", bg="#166534")
        self.player_label.pack(fill="x", padx=24, pady=16, ipady=18)

        buttons = tk.Frame(self, bg="#14532d")
        buttons.pack(pady=10)
        self.new_button = tk.Button(buttons, text="New Round", width=12, command=self.new_round)
        self.hit_button = tk.Button(buttons, text="Hit", width=12, command=self.hit)
        self.stand_button = tk.Button(buttons, text="Stand", width=12, command=self.stand)
        self.double_button = tk.Button(buttons, text="Double", width=12, command=self.double_down)
        for button in (self.new_button, self.hit_button, self.stand_button, self.double_button):
            button.pack(side="left", padx=6)

        tk.Label(self, textvariable=self.log_var, font=("Segoe UI", 10), justify="left", fg="white", bg="#14532d").pack(
            fill="x", padx=24, pady=12
        )

    def new_round(self) -> None:
        try:
            self.game.start_round(float(self.bet_var.get()))
        except ValueError as exc:
            messagebox.showerror("Invalid bet", str(exc))
        self._refresh()

    def hit(self) -> None:
        self.game.hit()
        self._refresh()

    def stand(self) -> None:
        self.game.stand()
        self._refresh()

    def double_down(self) -> None:
        self.game.double_down()
        self._refresh()

    def _cards(self, cards) -> str:
        return " ".join(card.display() for card in cards) or "(none)"

    def _refresh(self) -> None:
        self.chips_var.set(f"Chips: {self.game.chips:g}")
        dealer_cards = self._cards(self.game.dealer_visible_cards())
        player_cards = self.game.player_hand.display() or "(none)"
        self.dealer_var.set(f"Dealer: {dealer_cards}")
        self.player_var.set(f"Player: {player_cards} ({self.game.player_hand.value})")
        self.log_var.set("\n".join(self.game.log[-4:]))

        if self.game.result:
            self.status_var.set(f"{self.game.result.message} Chip change: {self.game.result.chip_delta:g}")
        elif self.game.phase == Phase.PLAYER_TURN:
            self.status_var.set("Choose your action.")
        else:
            self.status_var.set("Place a bet to start.")

        legal = self.game.legal_actions()
        self.hit_button.config(state=tk.NORMAL if Action.HIT in legal else tk.DISABLED)
        self.stand_button.config(state=tk.NORMAL if Action.STAND in legal else tk.DISABLED)
        self.double_button.config(state=tk.NORMAL if Action.DOUBLE in legal else tk.DISABLED)
        self.new_button.config(state=tk.NORMAL if self.game.phase != Phase.PLAYER_TURN and self.game.chips > 0 else tk.DISABLED)


def main() -> None:
    app = BlackjackApp()
    app.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run GUI import check**

Run: `conda run -n blackjack-game python -c "from blackjack.gui import BlackjackApp; print(BlackjackApp.__name__)"`

Expected: prints `BlackjackApp`.

- [ ] **Step 4: Launch GUI manually**

Run: `conda run -n blackjack-game python -m blackjack.gui`

Expected: Blackjack window opens. Start a round, verify Hit/Stand/Double buttons update, then close the window.

- [ ] **Step 5: Run tests**

Run: `conda run -n blackjack-game pytest`

Expected: all tests pass.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/blackjack/gui.py README.md
git commit -m "Add tkinter Blackjack interface"
```

### Task 7: Final Verification

**Files:**
- Modify: `README.md` if any commands changed during implementation.

- [ ] **Step 1: Run full test suite**

Run: `conda run -n blackjack-game pytest`

Expected: all tests pass.

- [ ] **Step 2: Verify terminal entry point**

Run: `conda run -n blackjack-game python -m blackjack.cli`

Expected: game prompts for a bet. Enter `quit` and confirm it exits cleanly.

- [ ] **Step 3: Verify GUI entry point**

Run: `conda run -n blackjack-game python -m blackjack.gui`

Expected: window opens and a playable round can be started.

- [ ] **Step 4: Check git status**

Run: `git status --short --branch`

Expected: clean working tree on the current branch.

- [ ] **Step 5: Commit final README adjustments if needed**

Run:

```powershell
git add README.md
git commit -m "Document Blackjack run commands"
```

Only run this commit if `README.md` changed after the GUI commit.
