"""Command-line interface for quadtree image compression."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

try:
    from .compression import ImageQuadTree, save_gif
except ImportError:
    from compression import ImageQuadTree, save_gif


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
        "--no-gif-boundaries",
        action="store_true",
        help="do not draw quadtree boundaries in the generated GIF",
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


def _ensure_parent_dir(path: Path) -> None:
    """Create parent directory for an output path if needed."""
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    """Run the image compression CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input.is_file():
        parser.error(f"input image not found: {args.input}")
    if args.duration <= 0:
        parser.error("--duration must be positive")

    _ensure_parent_dir(args.output)
    if args.boundaries:
        _ensure_parent_dir(args.boundaries)
    if args.gif:
        _ensure_parent_dir(args.gif)

    try:
        with Image.open(args.input) as source:
            tree = ImageQuadTree(
                source,
                compression=args.compression,
                min_size=args.min_size,
                max_depth=args.max_depth,
                workers=args.workers,
            )
            tree.build()

            compressed = tree.compress()
            try:
                compressed.save(args.output)
            finally:
                compressed.close()

            if args.boundaries:
                bounded = tree.with_boundaries()
                try:
                    bounded.save(args.boundaries)
                finally:
                    bounded.close()

            if args.gif:
                frames = tree.animation_frames(
                    show_boundaries=not args.no_gif_boundaries
                )
                try:
                    save_gif(frames, str(args.gif), args.duration)
                finally:
                    for frame in frames:
                        frame.close()
    except ValueError as exc:
        parser.error(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())