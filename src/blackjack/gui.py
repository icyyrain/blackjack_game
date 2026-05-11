from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from blackjack.card_images import card_back_path, card_image_path
from blackjack.cards import Card
from blackjack.game import Action, BlackjackGame, Phase


INITIAL_DEAL_CARDS = 4


def initial_deal_deck_count(final_deck_count: int, shown_cards: int) -> int:
    return final_deck_count + max(INITIAL_DEAL_CARDS - shown_cards, 0)


class BlackjackApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Blackjack")
        self.geometry("1210x720")
        self.configure(bg="#14532d")
        self.game = BlackjackGame(starting_chips=100)
        self.starting_chips = 100
        self.action_delay_ms = 500
        self.dealing = False
        self.card_panel_height = 176

        self.status_var = tk.StringVar(value="Place a bet to start.")
        self.chips_var = tk.StringVar()
        self.deck_var = tk.StringVar()
        self.bet_var = tk.StringVar(value="10")
        self.dealer_var = tk.StringVar()
        self.player_var = tk.StringVar()
        self.log_var = tk.StringVar()
        self.card_images: dict[str, tk.PhotoImage] = {}
        self.card_view_mode = "images"

        self._build()
        self._refresh()

    def _build(self) -> None:
        title = tk.Label(
            self,
            text="Blackjack",
            font=("Georgia", 30, "bold italic"),
            fg="#f8fafc",
            bg="#14532d",
        )
        title.pack(pady=12)

        info = tk.Frame(self, bg="#14532d")
        info.pack(fill="x", padx=24)
        tk.Label(info, textvariable=self.chips_var, font=("Segoe UI", 12), fg="white", bg="#14532d").pack(side="left")
        tk.Label(info, textvariable=self.deck_var, font=("Segoe UI", 12), fg="white", bg="#14532d").pack(side="left", padx=24)
        tk.Label(info, text="Bet:", font=("Segoe UI", 12), fg="white", bg="#14532d").pack(side="right")
        tk.Entry(info, textvariable=self.bet_var, width=8).pack(side="right", padx=8)
        tk.Button(info, text="Rules", width=8, command=self.show_rules).pack(side="right", padx=8)
        self.view_button = tk.Button(info, text="Text Cards", width=10, command=self.toggle_card_view)
        self.view_button.pack(side="right", padx=8)

        self.dealer_panel = tk.Frame(self, bg="#166534", height=self.card_panel_height)
        self.dealer_panel.pack(fill="x", padx=24, pady=16)
        self.dealer_panel.pack_propagate(False)
        self.dealer_content = tk.Frame(self.dealer_panel, bg="#166534")
        self.dealer_content.pack(expand=True)
        self.dealer_title_label = tk.Label(
            self.dealer_content,
            textvariable=self.dealer_var,
            font=("Segoe UI", 14, "bold"),
            fg="#f8fafc",
            bg="#166534",
        )
        self.dealer_title_label.pack(pady=(0, 4))
        self.dealer_cards_frame = tk.Frame(self.dealer_content, bg="#166534")
        self.dealer_cards_frame.pack()

        tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 13), fg="white", bg="#14532d").pack(pady=6)

        self.player_panel = tk.Frame(self, bg="#166534", height=self.card_panel_height)
        self.player_panel.pack(fill="x", padx=24, pady=16)
        self.player_panel.pack_propagate(False)
        self.player_content = tk.Frame(self.player_panel, bg="#166534")
        self.player_content.pack(expand=True)
        self.player_title_label = tk.Label(
            self.player_content,
            textvariable=self.player_var,
            font=("Segoe UI", 14, "bold"),
            fg="#f8fafc",
            bg="#166534",
        )
        self.player_title_label.pack(pady=(0, 4))
        self.player_cards_frame = tk.Frame(self.player_content, bg="#166534")
        self.player_cards_frame.pack()

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
        self._delay_action("Dealing player card...", lambda: self.game.hit(auto_dealer=False))

    def stand(self) -> None:
        self._delay_action("Dealer playing...", lambda: self.game.stand(auto_dealer=False))

    def double_down(self) -> None:
        self._delay_action("Doubling down...", lambda: self.game.double_down(auto_dealer=False))

    def split(self) -> None:
        self.status_var.set("Splitting hand...")
        self._set_button_states(disabled=True)
        self.after(self.action_delay_ms, self._begin_split_animation)

    def show_rules(self) -> None:
        messagebox.showinfo(
            "Blackjack Rules",
            "\n".join(
                [
                    "Goal: beat the dealer without going over 21.",
                    "",
                    "Actions:",
                    "- Hit: take one card.",
                    "- Stand: end your hand.",
                    "- Double: double your bet, take one card, then stand.",
                    "- Split: available only on an initial pair. Creates two hands.",
                    "",
                    "Dealer:",
                    "- Dealer reveals the hidden card after you stand.",
                    "- Dealer draws until reaching 17 or higher.",
                    "",
                    "Payouts:",
                    "- Blackjack pays 2:1.",
                    "- Normal win pays 1:1.",
                    "- Push returns your bet.",
                    "",
                    "Split notes:",
                    "- Split is allowed once.",
                    "- Double is not available after split.",
                    "- A split-hand 21 is not a natural Blackjack.",
                ]
            ),
        )

    def toggle_card_view(self) -> None:
        self.card_view_mode = "text" if self.card_view_mode == "images" else "images"
        self.view_button.config(text="Image Cards" if self.card_view_mode == "text" else "Text Cards")
        self._refresh()

    def _refresh(self) -> None:
        self.chips_var.set(f"Chips: {self.game.chips:g}")
        self.deck_var.set(f"Deck: {len(self.game.deck)} cards")
        self._refresh_dealer_area()
        self._refresh_player_area()
        self.log_var.set("\n".join(self.game.log[-4:]))

        if self.game.result:
            self.status_var.set(f"{self.game.result.message} Chip change: {self.game.result.chip_delta:g}")
        elif self.game.phase == Phase.PLAYER_TURN:
            self.status_var.set("Choose your action.")
        else:
            self.status_var.set("Place a bet to start.")

        self._set_button_states()
        if self.game.result and self.game.chips <= 0:
            self.after_idle(self._handle_game_over)

    def _handle_game_over(self) -> None:
        restart = messagebox.askyesno("Game over", "You are out of chips. Start a new game?")
        if restart:
            self.game = BlackjackGame(starting_chips=self.starting_chips)
            self.status_var.set("Place a bet to start.")
            self._refresh()
            return
        self.destroy()

    def _dealer_text(self, hide_hole_card: bool = False) -> str:
        if not self.game.dealer_hand.cards:
            return "Dealer:"
        if self.game.phase == Phase.PLAYER_TURN or hide_hole_card:
            visible_value = self.game.dealer_hand.cards[0].value
            return f"Dealer: ({visible_value}+?)"
        return f"Dealer: ({self.game.dealer_hand.value})"

    def _player_text(self) -> str:
        if not self.game.split_active:
            return f"Player: ({self.game.player_hand.value})"
        return "Player hands"

    def _refresh_dealer_area(self, hide_hole_card: bool = False) -> None:
        self.dealer_var.set(self._dealer_text(hide_hole_card=hide_hole_card))
        self._set_card_title_fonts()
        hidden_indexes = (
            {1}
            if (self.game.phase == Phase.PLAYER_TURN or hide_hole_card) and len(self.game.dealer_hand.cards) > 1
            else set()
        )
        self._render_card_row(self.dealer_cards_frame, self.game.dealer_hand.cards, hidden_indexes=hidden_indexes)

    def _refresh_player_area(self) -> None:
        self.player_var.set(self._player_text())
        self._set_card_title_fonts()
        self._clear_frame(self.player_cards_frame)
        if not self.game.split_active:
            self.player_panel.config(height=self.card_panel_height)
            self.player_panel.pack_propagate(False)
            self._render_card_row(self.player_cards_frame, self.game.player_hand.cards)
            return
        self.player_panel.config(height=self.card_panel_height)
        self.player_panel.pack_propagate(False)
        for index, hand in enumerate(self.game.player_hands):
            hand_frame = tk.Frame(self.player_cards_frame, bg="#166534")
            hand_frame.pack(side="left", padx=10)
            marker = "> " if index == self.game.current_hand_index and self.game.phase == Phase.PLAYER_TURN else ""
            tk.Label(
                hand_frame,
                text=f"{marker}Hand {index + 1}: ({hand.value})",
                font=("Consolas", 16),
                fg="#f8fafc",
                bg="#166534",
            ).pack(side="left", padx=(0, 8))
            row = tk.Frame(hand_frame, bg="#166534")
            row.pack(side="left")
            self._render_card_row(row, hand.cards)

    def _clear_frame(self, frame: tk.Frame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _set_card_title_fonts(self) -> None:
        self.dealer_title_label.config(font=("Consolas", 16))
        self.player_title_label.config(font=("Consolas", 16))

    def _card_photo(self, card: Card | None) -> tk.PhotoImage:
        path = card_back_path() if card is None else card_image_path(card)
        key = str(path)
        if key not in self.card_images:
            self.card_images[key] = tk.PhotoImage(master=self, file=key)
        return self.card_images[key]

    def _render_card_row(
        self,
        frame: tk.Frame,
        cards: list[Card],
        hidden_indexes: set[int] | None = None,
    ) -> None:
        self._clear_frame(frame)
        if not cards:
            tk.Label(frame, text="(none)", font=("Segoe UI", 12), fg="#d1d5db", bg="#166534").pack()
            return
        hidden = hidden_indexes or set()
        if self.card_view_mode == "text":
            text = " ".join("[?]" if index in hidden else card.display() for index, card in enumerate(cards))
            tk.Label(
                frame,
                text=text,
                font=("Consolas", 16),
                fg="#f8fafc",
                bg="#166534",
            ).pack()
            return
        for index, card in enumerate(cards):
            photo = self._card_photo(None if index in hidden else card)
            label = tk.Label(frame, image=photo, bg="#166534", borderwidth=0)
            label.image = photo
            label.pack(side="left", padx=5)

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
        result = action()
        if self._should_delay_dealer_reveal(result):
            self._show_player_bust_before_dealer_reveal()
            self.after(self.action_delay_ms, self._refresh)
            return
        self._refresh()
        if self.game.phase == Phase.DEALER_TURN and not self.game.result:
            self._animate_dealer_turn()

    def _should_delay_dealer_reveal(self, result) -> bool:
        return bool(result and self.game.result and self.game.result.outcome == "player_bust")

    def _show_player_bust_before_dealer_reveal(self) -> None:
        self.chips_var.set(f"Chips: {self.game.chips:g}")
        self.deck_var.set(f"Deck: {len(self.game.deck)} cards")
        self._refresh_dealer_area(hide_hole_card=True)
        self._refresh_player_area()
        self.log_var.set("\n".join(self.game.log[-4:]))
        self.status_var.set("Player busts. Dealer reveals...")
        self._set_button_states(disabled=True)

    def _animate_initial_deal(self) -> None:
        self.dealing = True
        self._set_button_states(disabled=True)
        self.dealer_var.set("Dealer:")
        self.player_var.set("Player:")
        self._render_card_row(self.dealer_cards_frame, [])
        self._render_card_row(self.player_cards_frame, [])
        self.status_var.set("Dealing...")
        first = self.game.player_hands[0]
        sequence = [
            ("Player:", [first.cards[0]], "Dealer:", [], set()),
            ("Player:", [first.cards[0]], "Dealer:", [self.game.dealer_hand.cards[0]], set()),
            ("Player:", [first.cards[0], first.cards[1]], "Dealer:", [self.game.dealer_hand.cards[0]], set()),
            (
                f"Player: ({first.value})",
                first.cards,
                f"Dealer: ({self.game.dealer_hand.cards[0].value}+?)",
                self.game.dealer_hand.cards,
                {1},
            ),
        ]
        for index, (player_text, player_cards, dealer_text, dealer_cards, hidden_indexes) in enumerate(sequence, start=1):
            deck_count = initial_deal_deck_count(len(self.game.deck), index)
            self.after(
                self.action_delay_ms * index,
                lambda p=player_text,
                pc=player_cards,
                d=dealer_text,
                dc=dealer_cards,
                h=hidden_indexes,
                count=deck_count: self._show_deal_step(p, pc, d, dc, h, count),
            )
        self.after(self.action_delay_ms * (len(sequence) + 1), self._finish_initial_deal)

    def _show_deal_step(
        self,
        player_text: str,
        player_cards: list[Card],
        dealer_text: str,
        dealer_cards: list[Card],
        hidden_indexes: set[int],
        deck_count: int,
    ) -> None:
        self.player_var.set(player_text)
        self.dealer_var.set(dealer_text)
        self._render_card_row(self.player_cards_frame, player_cards)
        self._render_card_row(self.dealer_cards_frame, dealer_cards, hidden_indexes=hidden_indexes)
        self.deck_var.set(f"Deck: {deck_count} cards")

    def _finish_initial_deal(self) -> None:
        self.dealing = False
        self._refresh()

    def _animate_dealer_turn(self) -> None:
        self._set_button_states(disabled=True)
        if self.game.dealer_should_draw():
            self.status_var.set("Dealer draws...")
            self.after(self.action_delay_ms, self._dealer_draw_step)
            return
        self.game.finish_dealer_turn()
        self._refresh()

    def _dealer_draw_step(self) -> None:
        self.game.dealer_draw()
        self._refresh()
        self.after(self.action_delay_ms, self._animate_dealer_turn)

    def _begin_split_animation(self) -> None:
        self.game.split(deal_replacements=False)
        self._refresh()
        self.status_var.set("Dealing split hands...")
        self.after(self.action_delay_ms, self._deal_split_replacement_step)

    def _deal_split_replacement_step(self) -> None:
        self.game.deal_split_replacement()
        self._refresh()
        if self.game.split_replacement_index < len(self.game.player_hands):
            self.status_var.set("Dealing split hands...")
            self.after(self.action_delay_ms, self._deal_split_replacement_step)
            return
        self.status_var.set("Choose your action.")
        self._set_button_states()


def main() -> None:
    app = BlackjackApp()
    app.mainloop()


if __name__ == "__main__":
    main()
