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
    assert game.dealer_display() == "[7♥] [?]"
    assert game.phase == Phase.PLAYER_TURN


def test_hit_adds_one_card_and_bust_settles_round():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("9", "clubs"),
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
        Card("8", "clubs"),
        Card("6", "hearts"),
        Card("10", "spades"),
    ])

    game.start_round(10)
    game.stand()

    assert game.dealer_hand.value == 24
    assert game.result.outcome == "dealer_bust"
    assert game.chips == 110


def test_double_down_doubles_bet_deals_one_card_and_settles():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("5", "clubs"),
        Card("9", "clubs"),
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
        Card("Q", "diamonds"),
        Card("K", "clubs"),
        Card("A", "clubs"),
        Card("A", "hearts"),
    ])

    game.start_round(10)

    assert game.result.outcome == "push"
    assert game.chips == 100


def test_split_is_legal_for_initial_pair_and_creates_two_hands():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("9", "clubs"),
        Card("7", "diamonds"),
        Card("6", "clubs"),
        Card("8", "hearts"),
        Card("5", "spades"),
        Card("8", "clubs"),
    ])

    game.start_round(10)

    assert Action.SPLIT in game.legal_actions()

    game.split()

    assert len(game.player_hands) == 2
    assert game.current_hand_index == 0
    assert [card.rank for card in game.player_hands[0].cards] == ["8", "7"]
    assert [card.rank for card in game.player_hands[1].cards] == ["8", "9"]
    assert game.hand_bets == [10, 10]
    assert Action.SPLIT not in game.legal_actions()
    assert Action.DOUBLE not in game.legal_actions()


def test_split_hands_settle_independently_against_dealer():
    game = BlackjackGame(starting_chips=100, deck_factory=lambda: [
        Card("10", "clubs"),
        Card("4", "clubs"),
        Card("10", "diamonds"),
        Card("8", "hearts"),
        Card("7", "spades"),
        Card("8", "spades"),
    ])

    game.start_round(10)
    game.split()
    game.stand()
    game.stand()

    assert game.phase == Phase.SETTLED
    assert [result.outcome for result in game.hand_results] == ["dealer_win", "player_win"]
    assert game.chips == 100
