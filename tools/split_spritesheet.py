import argparse
from pathlib import Path

from PIL import Image


def split_spritesheet(
    input_path: str,
    output_prefix: str,
    tile_size: int = 32,
    cols: int = 2,
    rows: int = 4,
    head_ratio: float = 0.5,
) -> None:
    sheet = Image.open(input_path).convert("RGBA")

    expected_w = tile_size * cols
    expected_h = tile_size * rows
    if sheet.size != (expected_w, expected_h):
        print(
            f"The size of the spritesheet {sheet.size}, "
            f"based on cols/rows/tile-size, the expected {expected_w}x{expected_h}"
        )

    head_h = round(tile_size * head_ratio)
    body_h = tile_size - head_h

    head_sheet = Image.new("RGBA", (tile_size * cols, head_h * rows), (0, 0, 0, 0))
    body_sheet = Image.new("RGBA", (tile_size * cols, body_h * rows), (0, 0, 0, 0))

    for row in range(rows):
        for col in range(cols):
            x0 = col * tile_size
            y0 = row * tile_size
            tile = sheet.crop((x0, y0, x0 + tile_size, y0 + tile_size))

            head = tile.crop((0, 0, tile_size, head_h))
            body = tile.crop((0, head_h, tile_size, tile_size))

            head_sheet.paste(head, (col * tile_size, row * head_h))
            body_sheet.paste(body, (col * tile_size, row * body_h))

    head_path = f"{output_prefix}_head.png"
    body_path = f"{output_prefix}_body.png"
    head_sheet.save(head_path)
    body_sheet.save(body_path)

    print(f"Kész: {head_path} ({head_sheet.size[0]}x{head_sheet.size[1]})")
    print(f"Kész: {body_path} ({body_sheet.size[0]}x{body_sheet.size[1]})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Spritesheet szétválasztása fej és test rétegre.")
    parser.add_argument("input", help="A bemeneti spritesheet elérési útja (pl. player.png)")
    parser.add_argument(
        "--output-prefix",
        default=None,
        help="Kimeneti fájlok előtagja (alapértelmezett: a bemeneti fájl neve kiterjesztés nélkül)",
    )
    parser.add_argument("--tile-size", type=int, default=32, help="Egy karakter-csempe mérete pixelben (alapértelmezett: 32)")
    parser.add_argument("--cols", type=int, default=2, help="Oszlopok száma (pózok: álló, mozgó) (alapértelmezett: 2)")
    parser.add_argument("--rows", type=int, default=4, help="Sorok száma (irányok) (alapértelmezett: 4)")
    parser.add_argument(
        "--head-ratio",
        type=float,
        default=0.5,
        help="A csempe hányad része a fej, felülről (alapértelmezett: 0.5, azaz pontosan a felső fele)",
    )
    args = parser.parse_args()

    prefix = args.output_prefix or Path(args.input).stem
    split_spritesheet(
        input_path=args.input,
        output_prefix=prefix,
        tile_size=args.tile_size,
        cols=args.cols,
        rows=args.rows,
        head_ratio=args.head_ratio,
    )


if __name__ == "__main__":
    main()