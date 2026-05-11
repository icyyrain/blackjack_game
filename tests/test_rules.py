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
