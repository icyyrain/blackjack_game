from pathlib import Path

from blackjack.card_images import card_image_name, card_image_path, resource_root
from blackjack.cards import Card


def test_card_image_name_uses_asset_rank_and_suit_codes():
    assert card_image_name(Card("A", "clubs")) == "AC.png"
    assert card_image_name(Card("10", "hearts")) == "TH.png"
    assert card_image_name(Card("K", "spades")) == "KS.png"


def test_card_image_path_uses_resource_root():
    root = Path("assets")

    assert card_image_path(Card("Q", "diamonds"), root=root) == root / "cards" / "QD.png"


def test_resource_root_points_at_project_assets_in_source_tree():
    assert resource_root().name == "assets"
