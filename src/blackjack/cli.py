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
