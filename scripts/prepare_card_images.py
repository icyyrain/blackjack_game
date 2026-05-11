from __future__ import annotations

import argparse
from pathlib import Path

import cairosvg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "assets" / "poker-super2-box-qr"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "assets" / "cards"

CARD_NAMES = [
    f"{rank}{suit}"
    for suit in ("C", "D", "H", "S")
    for rank in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K")
]


def convert_svg_to_png(source: Path, output: Path, width: int, height: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(source),
        write_to=str(output),
        output_width=width,
        output_height=height,
    )


def convert_card_images(source_dir: Path, output_dir: Path, width: int, height: int) -> int:
    converted = 0
    for card_name in CARD_NAMES:
        source = source_dir / f"{card_name}.svg"
        if not source.exists():
            raise FileNotFoundError(f"Missing SVG card asset: {source}")
        convert_svg_to_png(source, output_dir / f"{card_name}.png", width, height)
        converted += 1

    back_source = source_dir / "1B.svg"
    if not back_source.exists():
        raise FileNotFoundError(f"Missing SVG card back asset: {back_source}")
    convert_svg_to_png(back_source, output_dir / "back.png", width, height)
    converted += 1
    return converted


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert SVG card assets to PNG files for the Tkinter GUI.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--height", type=int, default=134)
    args = parser.parse_args()

    count = convert_card_images(args.source_dir, args.output_dir, args.width, args.height)
    print(f"Converted {count} card images to {args.output_dir}")


if __name__ == "__main__":
    main()
