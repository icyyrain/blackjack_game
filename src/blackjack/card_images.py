from __future__ import annotations

from pathlib import Path
import sys

from blackjack.cards import Card


CARD_IMAGE_DIR = "cards"

_RANK_CODES = {
    "A": "A",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "T",
    "J": "J",
    "Q": "Q",
    "K": "K",
}

_SUIT_CODES = {
    "clubs": "C",
    "diamonds": "D",
    "hearts": "H",
    "spades": "S",
}


def resource_root() -> Path:
    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        return Path(bundled_root) / "assets"
    return Path(__file__).resolve().parents[2] / "assets"


def card_image_name(card: Card) -> str:
    return f"{_RANK_CODES[card.rank]}{_SUIT_CODES[card.suit]}.png"


def card_image_path(card: Card, root: Path | None = None) -> Path:
    asset_root = resource_root() if root is None else root
    return asset_root / CARD_IMAGE_DIR / card_image_name(card)


def card_back_path(root: Path | None = None) -> Path:
    asset_root = resource_root() if root is None else root
    return asset_root / CARD_IMAGE_DIR / "back.png"
