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
