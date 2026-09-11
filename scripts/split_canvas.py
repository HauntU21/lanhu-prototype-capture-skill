#!/usr/bin/env python3
"""Split a full prototype canvas into overlapping, row-major PNG tiles."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError as exc:  # pragma: no cover - depends on the host runtime
    raise SystemExit(
        "Pillow is required. Run this script with the bundled workspace Python "
        "runtime or install Pillow in the active Python environment."
    ) from exc


def tile_positions(canvas_length: int, tile_length: int, overlap: int) -> list[int]:
    if canvas_length <= 0:
        raise ValueError("canvas length must be positive")
    if tile_length <= 0:
        raise ValueError("tile length must be positive")
    if overlap < 0 or overlap >= tile_length:
        raise ValueError("overlap must be non-negative and smaller than the tile")
    if canvas_length <= tile_length:
        return [0]

    step = tile_length - overlap
    count = math.ceil((canvas_length - overlap) / step)
    last_start = canvas_length - tile_length
    positions = [round(index * last_start / (count - 1)) for index in range(count)]
    return list(dict.fromkeys(positions))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="native-scale full-canvas image")
    parser.add_argument("--output", type=Path, required=True, help="tile output directory")
    parser.add_argument("--tile-width", type=int, default=1800)
    parser.add_argument("--tile-height", type=int, default=1200)
    parser.add_argument("--overlap-x", type=int, default=180)
    parser.add_argument("--overlap-y", type=int, default=120)
    parser.add_argument("--prefix", default="tile")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input.expanduser().resolve(strict=True)
    output_dir = args.output.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as opened:
        source = ImageOps.exif_transpose(opened)
        canvas_width, canvas_height = source.size
        x_positions = tile_positions(canvas_width, args.tile_width, args.overlap_x)
        y_positions = tile_positions(canvas_height, args.tile_height, args.overlap_y)
        tiles: list[dict[str, int | str]] = []

        for row_index, y in enumerate(y_positions, start=1):
            for column_index, x in enumerate(x_positions, start=1):
                right = min(x + args.tile_width, canvas_width)
                bottom = min(y + args.tile_height, canvas_height)
                filename = f"{args.prefix}_r{row_index:02d}_c{column_index:02d}.png"
                tile = source.crop((x, y, right, bottom))
                tile.save(output_dir / filename, format="PNG")
                tiles.append(
                    {
                        "file": filename,
                        "row": row_index,
                        "column": column_index,
                        "x": x,
                        "y": y,
                        "width": right - x,
                        "height": bottom - y,
                    }
                )

    manifest = {
        "source": str(input_path),
        "canvasWidth": canvas_width,
        "canvasHeight": canvas_height,
        "tileWidth": args.tile_width,
        "tileHeight": args.tile_height,
        "requestedOverlapX": args.overlap_x,
        "requestedOverlapY": args.overlap_y,
        "columns": len(x_positions),
        "rows": len(y_positions),
        "tiles": tiles,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
