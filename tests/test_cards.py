from blackjack.cards import Card, Deck


def test_new_deck_contains_52_unique_cards():
    deck = Deck.standard()

    assert len(deck.cards) == 52
    assert len(set(deck.cards)) == 52


def test_shuffle_preserves_same_cards_but_can_change_order():
    deck = Deck.standard()
    before = set(deck.cards)

    deck.shuffle(seed=7)

    assert set(deck.cards) == before
    assert len(deck.cards) == 52


def test_deal_pops_from_top_of_deck():
    top = Card("A", "spades")
    bottom = Card("9", "hearts")
    deck = Deck([bottom, top])

    dealt = deck.deal()

    assert dealt == top
    assert deck.cards == [bottom]


def test_card_display_uses_suit_symbols():
    assert Card("A", "spades").display() == "[A♠]"
    assert Card("10", "hearts").display() == "[10♥]"
    assert Card("Q", "diamonds").display() == "[Q♦]"
    assert Card("2", "clubs").display() == "[2♣]"
