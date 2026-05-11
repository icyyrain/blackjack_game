# Blackjack Game Design

Date: 2026-05-11

## Goal

Build a standard single-player Blackjack game in Python. The player should be able to play against a dealer with realistic 52-card deck behavior, including a fresh shuffle at the start of each round and dealing by popping cards from the top of the deck.

The project will start with a tested terminal game, then add a lightweight graphical interface using the same game engine.

## Scope

Included:

- One player versus one dealer.
- One standard 52-card deck per round.
- Fresh shuffle during each round initialization.
- Deal cards from the top of the deck with `pop`.
- Player actions: hit, stand, and double down.
- Double down is available only when the player has exactly two initial cards, has not taken another action, and has enough chips to double the bet.
- Double down deals exactly one card to the player, then automatically stands.
- Blackjack pays 3:2.
- Dealer stands on 17 or higher.
- Bets, chip balance, round outcome, and remaining deck size are visible to the player.
- Terminal interface first, followed by a simple GUI.
- Initialize the project as a git repository and commit major milestones.
- Create a conda environment for development and running the game.

Not included in the first version:

- Split.
- Insurance.
- Surrender.
- Multi-player seats.
- Multi-deck shoes.
- Card counting hints or strategy advice.
- Networked or persistent user accounts.

## Architecture

The implementation will separate Blackjack rules from presentation:

- `cards.py`: card and deck model.
- `rules.py`: hand value and outcome helpers.
- `game.py`: stateful game engine and player/dealer actions.
- `cli.py`: terminal game loop.
- `gui.py`: tkinter graphical interface.

The core engine will have no dependency on the terminal or GUI. Both interfaces will call the same engine methods so there is only one source of truth for game behavior.

## Core Model

`Card` represents one playing card with a rank and suit.

`Deck` owns the current list of cards. It can create a complete 52-card deck, shuffle it, and deal from the top by popping one card. Tests will verify uniqueness and deal order.

`Hand` owns a list of cards and computes Blackjack values. Aces count as 11 when possible and fall back to 1 as needed to avoid busting.

`BlackjackGame` owns round state:

- chip balance
- current bet
- player hand
- dealer hand
- deck
- allowed actions
- current phase
- final outcome
- message log

The game engine exposes methods such as:

- `start_round(bet)`
- `hit()`
- `stand()`
- `double_down()`
- `dealer_play()`
- `settle_round()`

## Game Flow

1. The player starts with an initial chip balance.
2. The player enters a bet.
3. A fresh 52-card deck is created and shuffled.
4. The player and dealer each receive two cards from the deck top.
5. The player sees both player cards and only the dealer's upcard.
6. If either side has Blackjack, the round settles immediately.
7. Otherwise the player may hit, stand, or double down if eligible.
8. If the player busts, the round settles immediately.
9. If the player stands or doubles, the dealer reveals the hidden card and draws until reaching at least 17.
10. The game compares final totals and updates chips.
11. The player can start another round while they have chips remaining.

## Payouts

- Player Blackjack: win 1.5 times the bet, unless dealer also has Blackjack.
- Normal player win: win 1 times the bet.
- Push: bet is returned with no net change.
- Player loss: lose the bet.
- Player bust: lose immediately.
- Dealer bust: player wins normally.

Chip accounting will be tested through observable chip balance changes after settlement.

## Terminal Interface

The terminal version will be the first playable interface. It will show:

- chip balance
- current bet
- player's full hand and score
- dealer upcard during player decisions
- full dealer hand after reveal
- legal actions for the current state
- round result and chip change
- remaining deck count

Commands will be simple text actions, such as `hit`, `stand`, `double`, and `quit`.

## Graphical Interface

The GUI will use tkinter to keep the conda environment lightweight.

The first GUI will prioritize clarity over animation:

- Dealer area at the top.
- Player area at the bottom.
- Status and log area in the middle.
- Bet and chip controls.
- Buttons for Hit, Stand, Double, and New Round.
- Double button enabled only when the action is legal.
- Text-based card faces such as `[A spades]` or `[10 hearts]` initially.

Later visual polish can replace text card faces with image assets without changing the game engine.

## Conda Environment

The project will include an `environment.yml` for a conda environment named `blackjack-game`.

Initial dependencies:

- Python
- pytest

tkinter is expected to be available with the Python distribution. If verification shows tkinter is missing in this environment, the environment file will be adjusted during implementation.

## Testing Strategy

Implementation will follow test-driven development for the core behavior.

Initial tests will cover:

- A new deck contains exactly 52 unique cards.
- Shuffling preserves the same set of cards.
- Dealing pops from the top and reduces deck size.
- Hand values handle aces correctly.
- Blackjack is detected only with two-card 21.
- Bust detection works.
- Initial round deals two cards each to player and dealer.
- Hit adds one player card.
- Stand triggers dealer play and settlement.
- Double down doubles the bet, deals one card, then settles.
- Double down is unavailable after a hit.
- Dealer stands on 17 or higher.
- Player Blackjack pays 3:2.
- Push, normal win, loss, and bust settlement update chips correctly.

CLI and GUI tests will be lighter than engine tests. The engine carries most correctness guarantees.

## Git Workflow

The project will be initialized as a git repository.

Expected milestone commits:

- Design spec.
- Project scaffolding and conda environment.
- Core deck and hand rules.
- Game engine.
- Terminal interface.
- GUI interface.

Generated local brainstorming files under `.superpowers/` will be ignored.

## Risks and Decisions

The first version intentionally excludes split, insurance, surrender, and multi-deck shoes. Those features change the state model and should be added after the single-hand engine is stable.

The GUI will be built after the terminal version is playable. This keeps rule debugging separate from visual event handling and makes the game easier to test.
