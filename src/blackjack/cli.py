from __future__ import annotations

import sys
import time

from blackjack.game import Action, BlackjackGame, Phase


DEAL_DELAY_SECONDS = 0.5


def format_cards(cards) -> str:
    return " ".join(card.display() for card in cards) or "(none)"


def print_state(game: BlackjackGame) -> None:
    print()
    print(f"Chips: {game.chips:g} | Bet: {game.bet:g} | 牌堆: {len(game.deck)} 张")
    print(f"Dealer: {game.dealer_display()}")
    if game.split_active:
        for index, hand in enumerate(game.player_hands):
            marker = ">" if index == game.current_hand_index and game.phase == Phase.PLAYER_TURN else " "
            print(f"{marker} Hand {index + 1}: {hand.display()} ({hand.value})")
    else:
        print(f"Player: {game.player_hand.display()} ({game.player_hand.value})")
    if game.result:
        print(f"Result: {game.result.message} Chip change: {game.result.chip_delta:g}")


def ask_bet(game: BlackjackGame) -> float | None:
    while True:
        try:
            raw = input(f"Bet amount, or quit (chips {game.chips:g}): ").strip().lower()
        except EOFError:
            return None
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
    aliases = {
        "h": Action.HIT,
        "hit": Action.HIT,
        "s": Action.STAND,
        "stand": Action.STAND,
        "d": Action.DOUBLE,
        "double": Action.DOUBLE,
        "p": Action.SPLIT,
        "split": Action.SPLIT,
    }
    while True:
        raw = input(f"Action ({labels}): ").strip().lower()
        action = aliases.get(raw)
        if action in legal:
            return action
        print("Choose one of the listed actions.")


def show_initial_deal(game: BlackjackGame) -> None:
    sequence = [
        ("Player receives", game.player_hands[0].cards[0].display()),
        ("Dealer receives", game.dealer_hand.cards[0].display()),
        ("Player receives", game.player_hands[0].cards[1].display()),
        ("Dealer receives", "[?]"),
    ]
    for label, card in sequence:
        time.sleep(DEAL_DELAY_SECONDS)
        print(f"{label}: {card}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    game = BlackjackGame(starting_chips=100)
    print("Blackjack")

    while game.chips > 0:
        bet = ask_bet(game)
        if bet is None:
            break
        game.start_round(bet)
        show_initial_deal(game)

        while game.phase == Phase.PLAYER_TURN:
            print_state(game)
            action = ask_action(game)
            time.sleep(DEAL_DELAY_SECONDS)
            if action == Action.HIT:
                game.hit()
            elif action == Action.STAND:
                game.stand()
            elif action == Action.DOUBLE:
                game.double_down()
            elif action == Action.SPLIT:
                game.split()

        print_state(game)
        print("-" * 40)

    print("Thanks for playing.")


if __name__ == "__main__":
    main()
