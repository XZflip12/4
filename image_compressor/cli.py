"""Command-line interface for quadtree image compression."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from .compression import ImageQuadTree, save_gif


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Compress an image with a quadtree."
    )
    parser.add_argument("input", type=Path, help="input image path")
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="compressed image path"
    )
    parser.add_argument(
        "-b", "--boundaries", type=Path, help="path for image with tree boundaries"
    )
    parser.add_argument(
        "-g", "--gif", type=Path, help="path for a step-by-step GIF"
    )
    parser.add_argument(
        "-c",
        "--compression",
        type=int,
        default=50,
        help="compression level from 0 (accurate) to 100 (strong), default: 50",
    )
    parser.add_argument("--min-size", type=int, default=2)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--duration", type=int, default=250)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the image compression CLI."""
    args = build_parser().parse_args(argv)
    if not args.input.is_file():
        raise FileNotFoundError(f"input image not found: {args.input}")
    with Image.open(args.input) as source:
        tree = ImageQuadTree(
            source,
            compression=args.compression,
            min_size=args.min_size,
            max_depth=args.max_depth,
            workers=args.workers,
        )
        tree.compress().save(args.output)
        if args.boundaries:
            tree.with_boundaries().save(args.boundaries)
        if args.gif:
            save_gif(tree.animation_frames(), str(args.gif), args.duration)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
