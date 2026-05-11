from blackjack.game import Phase
from blackjack.gui import BlackjackApp, initial_deal_deck_count


def test_initial_deal_deck_count_matches_visible_animation_steps():
    counts = [initial_deal_deck_count(final_deck_count=48, shown_cards=shown) for shown in range(1, 5)]

    assert counts == [51, 50, 49, 48]


def test_game_over_prompt_can_restart(monkeypatch):
    app = BlackjackApp()
    try:
        monkeypatch.setattr("blackjack.gui.messagebox.askyesno", lambda *args, **kwargs: True)

        app.game.chips = 0
        app._handle_game_over()

        assert app.game.chips == 100
        assert app.game.phase == Phase.BETTING
        assert app.status_var.get() == "Place a bet to start."
    finally:
        app.destroy()


def test_game_over_prompt_can_exit(monkeypatch):
    app = BlackjackApp()
    destroyed = []
    try:
        monkeypatch.setattr("blackjack.gui.messagebox.askyesno", lambda *args, **kwargs: False)
        monkeypatch.setattr(app, "destroy", lambda: destroyed.append(True))

        app.game.chips = 0
        app._handle_game_over()

        assert destroyed == [True]
    finally:
        if not destroyed:
            app.destroy()
