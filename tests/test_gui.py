import pytest

from blackjack.game import BlackjackGame, Phase
from blackjack.cards import Card
from blackjack.gui import BlackjackApp, initial_deal_deck_count


@pytest.fixture(scope="module")
def app():
    app = BlackjackApp()
    yield app
    app.destroy()


@pytest.fixture(autouse=True)
def reset_app(app):
    app.game = BlackjackGame(starting_chips=app.starting_chips)
    app.card_view_mode = "images"
    app.view_button.config(text="Text Cards")
    app._refresh()
    yield


def test_initial_deal_deck_count_matches_visible_animation_steps():
    counts = [initial_deal_deck_count(final_deck_count=48, shown_cards=shown) for shown in range(1, 5)]

    assert counts == [51, 50, 49, 48]


def test_initial_window_size_is_expanded(app):
    app.update_idletasks()
    assert app.geometry().startswith("1210x720")


def test_game_over_prompt_can_restart(app, monkeypatch):
    monkeypatch.setattr("blackjack.gui.messagebox.askyesno", lambda *args, **kwargs: True)

    app.game.chips = 0
    app._handle_game_over()

    assert app.game.chips == 100
    assert app.game.phase == Phase.BETTING
    assert app.status_var.get() == "Place a bet to start."


def test_game_over_prompt_can_exit(app, monkeypatch):
    destroyed = []
    monkeypatch.setattr("blackjack.gui.messagebox.askyesno", lambda *args, **kwargs: False)
    monkeypatch.setattr(app, "destroy", lambda: destroyed.append(True))

    app.game.chips = 0
    app._handle_game_over()

    assert destroyed == [True]


def test_refresh_renders_card_images_for_active_round(app):
    app.game.deck_factory = lambda: [
        Card("9", "clubs"),
        Card("6", "spades"),
        Card("8", "diamonds"),
        Card("10", "hearts"),
    ]

    app.game.start_round(10)
    app._refresh()

    player_images = [
        child.cget("image")
        for child in app.player_cards_frame.winfo_children()
        if child.winfo_class() == "Label" and child.cget("image")
    ]
    dealer_images = [
        child.cget("image")
        for child in app.dealer_cards_frame.winfo_children()
        if child.winfo_class() == "Label" and child.cget("image")
    ]

    assert len(player_images) == 2
    assert len(dealer_images) == 2
    assert app.dealer_title_label.cget("font") == "Consolas 16"
    assert app.player_title_label.cget("font") == "Consolas 16"
    assert app.dealer_panel.cget("height") == app.card_panel_height
    assert app.player_panel.cget("height") == app.card_panel_height
    assert app.dealer_panel.pack_propagate() is None
    assert app.player_panel.pack_propagate() is None


def test_toggle_card_view_renders_text_cards_for_active_round(app):
    app.game.deck_factory = lambda: [
        Card("9", "clubs"),
        Card("6", "spades"),
        Card("8", "diamonds"),
        Card("10", "hearts"),
    ]

    app.game.start_round(10)
    app._refresh()
    app.toggle_card_view()

    player_labels = [
        child
        for child in app.player_cards_frame.winfo_children()
        if child.winfo_class() == "Label"
    ]
    dealer_labels = [
        child
        for child in app.dealer_cards_frame.winfo_children()
        if child.winfo_class() == "Label"
    ]

    assert app.card_view_mode == "text"
    assert app.view_button.cget("text") == "Image Cards"
    assert len(player_labels) == 1
    assert len(dealer_labels) == 1
    assert "[?]" in dealer_labels[0].cget("text")
    assert app.dealer_title_label.cget("font") == "Consolas 16"
    assert dealer_labels[0].cget("font") == "Consolas 16"


def test_split_hands_stay_horizontal_with_matching_font(app):
    app.game.deck_factory = lambda: [
        Card("9", "clubs"),
        Card("8", "spades"),
        Card("6", "diamonds"),
        Card("8", "hearts"),
    ]

    app.game.start_round(10)
    app.game.split(deal_replacements=False)
    app._refresh()

    hand_frames = [
        child
        for child in app.player_cards_frame.winfo_children()
        if child.winfo_class() == "Frame"
    ]
    hand_labels = [
        frame.winfo_children()[0]
        for frame in hand_frames
    ]

    assert len(hand_frames) == 2
    assert all(frame.pack_info()["side"] == "left" for frame in hand_frames)
    assert all(label.cget("font") == "Consolas 16" for label in hand_labels)
    assert app.player_panel.cget("height") == app.card_panel_height
    assert app.player_panel.pack_propagate() is None
