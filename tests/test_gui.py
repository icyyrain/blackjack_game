from blackjack.gui import initial_deal_deck_count


def test_initial_deal_deck_count_matches_visible_animation_steps():
    counts = [initial_deal_deck_count(final_deck_count=48, shown_cards=shown) for shown in range(1, 5)]

    assert counts == [51, 50, 49, 48]
