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
        self.action_delay_ms = 500
        self.dealing = False

        self.status_var = tk.StringVar(value="Place a bet to start.")
        self.chips_var = tk.StringVar()
        self.deck_var = tk.StringVar()
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
        tk.Label(info, textvariable=self.deck_var, font=("Segoe UI", 12), fg="white", bg="#14532d").pack(side="left", padx=24)
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
        self.split_button = tk.Button(buttons, text="Split", width=12, command=self.split)
        for button in (self.new_button, self.hit_button, self.stand_button, self.double_button, self.split_button):
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
            return
        self._animate_initial_deal()

    def hit(self) -> None:
        self._delay_action("Dealing player card...", self.game.hit)

    def stand(self) -> None:
        self._delay_action("Dealer playing...", self.game.stand)

    def double_down(self) -> None:
        self._delay_action("Doubling down...", self.game.double_down)

    def split(self) -> None:
        self._delay_action("Splitting hand...", self.game.split)

    def _cards(self, cards) -> str:
        return " ".join(card.display() for card in cards) or "(none)"

    def _refresh(self) -> None:
        self.chips_var.set(f"Chips: {self.game.chips:g}")
        self.deck_var.set(f"牌堆: {len(self.game.deck)} 张")
        self.dealer_var.set(f"Dealer: {self.game.dealer_display()}")
        self.player_var.set(self._player_text())
        self.log_var.set("\n".join(self.game.log[-4:]))

        if self.game.result:
            self.status_var.set(f"{self.game.result.message} Chip change: {self.game.result.chip_delta:g}")
        elif self.game.phase == Phase.PLAYER_TURN:
            self.status_var.set("Choose your action.")
        else:
            self.status_var.set("Place a bet to start.")

        self._set_button_states()

    def _player_text(self) -> str:
        if not self.game.split_active:
            cards = self.game.player_hand.display() or "(none)"
            return f"Player: {cards} ({self.game.player_hand.value})"
        lines = []
        for index, hand in enumerate(self.game.player_hands):
            marker = ">" if index == self.game.current_hand_index and self.game.phase == Phase.PLAYER_TURN else " "
            lines.append(f"{marker} Hand {index + 1}: {hand.display()} ({hand.value})")
        return "\n".join(lines)

    def _set_button_states(self, disabled: bool = False) -> None:
        legal = set() if disabled else self.game.legal_actions()
        self.hit_button.config(state=tk.NORMAL if Action.HIT in legal else tk.DISABLED)
        self.stand_button.config(state=tk.NORMAL if Action.STAND in legal else tk.DISABLED)
        self.double_button.config(state=tk.NORMAL if Action.DOUBLE in legal else tk.DISABLED)
        self.split_button.config(state=tk.NORMAL if Action.SPLIT in legal else tk.DISABLED)
        can_start = not disabled and self.game.phase != Phase.PLAYER_TURN and self.game.chips > 0
        self.new_button.config(state=tk.NORMAL if can_start else tk.DISABLED)

    def _delay_action(self, status: str, action) -> None:
        self.status_var.set(status)
        self._set_button_states(disabled=True)
        self.after(self.action_delay_ms, lambda: self._complete_delayed_action(action))

    def _complete_delayed_action(self, action) -> None:
        action()
        self._refresh()

    def _animate_initial_deal(self) -> None:
        self.dealing = True
        self._set_button_states(disabled=True)
        self.dealer_var.set("Dealer: (none)")
        self.player_var.set("Player: (none)")
        self.status_var.set("Dealing...")
        first = self.game.player_hands[0]
        sequence = [
            (f"Player: {first.cards[0].display()}", "Dealer: (none)"),
            (f"Player: {first.cards[0].display()}", f"Dealer: {self.game.dealer_hand.cards[0].display()}"),
            (
                f"Player: {first.cards[0].display()} {first.cards[1].display()}",
                f"Dealer: {self.game.dealer_hand.cards[0].display()}",
            ),
            (
                f"Player: {first.display()} ({first.value})",
                f"Dealer: {self.game.dealer_hand.cards[0].display()} [?]",
            ),
        ]
        for index, (player_text, dealer_text) in enumerate(sequence, start=1):
            self.after(self.action_delay_ms * index, lambda p=player_text, d=dealer_text: self._show_deal_step(p, d))
        self.after(self.action_delay_ms * (len(sequence) + 1), self._finish_initial_deal)

    def _show_deal_step(self, player_text: str, dealer_text: str) -> None:
        self.player_var.set(player_text)
        self.dealer_var.set(dealer_text)
        self.deck_var.set(f"牌堆: {len(self.game.deck)} 张")

    def _finish_initial_deal(self) -> None:
        self.dealing = False
        self._refresh()


def main() -> None:
    app = BlackjackApp()
    app.mainloop()


if __name__ == "__main__":
    main()
