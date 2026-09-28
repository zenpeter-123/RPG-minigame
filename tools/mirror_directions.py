import argparse
from pathlib import Path

from PIL import Image


def flip_tile(tile: Image.Image, flip: str) -> Image.Image:
    if flip == "horizontal":
        return tile.transpose(Image.FLIP_LEFT_RIGHT)
    if flip == "vertical":
        return tile.transpose(Image.FLIP_TOP_BOTTOM)
    if flip == "both":
        return tile.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    if flip == "none":
        return tile
    raise ValueError(f"Ismeretlen flip mód: {flip}")


def mirror_spritesheet(input_path: str, output_path: str, flip: str, tile_size: int = 128) -> None:
    sheet = Image.open(input_path).convert("RGBA")
    w, h = sheet.size
    if h != tile_size or w % tile_size != 0:
        print(
            f"Figyelem: a kép mérete {sheet.size}, "
            f"de {tile_size} magasságot és {tile_size} többszörös szélességet vártam."
        )
    n_frames = w // tile_size

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(n_frames):
        x0 = i * tile_size
        tile = sheet.crop((x0, 0, x0 + tile_size, tile_size))
        out.paste(flip_tile(tile, flip), (x0, 0))

    out.save(output_path)
    print(f"Kész: {output_path} ({n_frames} képkocka, {out.size[0]}x{out.size[1]})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Spritesheet irány-generálás tükrözéssel.")
    parser.add_argument("input", help="Bemeneti spritesheet (pl. sword_up_left.png)")
    parser.add_argument("--output", help="Kimeneti fájl neve (ha nem --all-t használsz)")
    parser.add_argument(
        "--flip",
        choices=["horizontal", "vertical", "both", "none"],
        default="horizontal",
        help="Tükrözés iránya (alapértelmezett: horizontal, azaz up-left -> up-right)",
    )
    parser.add_argument("--tile-size", type=int, default=128, help="Egy képkocka mérete pixelben (alapértelmezett: 128)")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Mindhárom irányt legyártja egyszerre (up-right, down-left, down-right) a bemenetből, ami up-left-nek feltételezett",
    )
    parser.add_argument("--prefix", default=None, help="--all esetén a kimeneti fájlok előtagja (alapértelmezett: a bemenet neve _up_left nélkül)")
    args = parser.parse_args()

    if args.all:
        prefix = args.prefix or Path(args.input).stem.replace("_up_left", "")
        mirror_spritesheet(args.input, f"{prefix}_up_right.png", "horizontal", args.tile_size)
        mirror_spritesheet(args.input, f"{prefix}_down_left.png", "vertical", args.tile_size)
        mirror_spritesheet(args.input, f"{prefix}_down_right.png", "both", args.tile_size)
    else:
        if not args.output:
            parser.error("--output kötelező, ha nem --all-t használsz")
        mirror_spritesheet(args.input, args.output, args.flip, args.tile_size)


if __name__ == "__main__":
    main()
