"""Tests for image compression."""

from pathlib import Path

from PIL import Image

from image_compressor.compression import ImageQuadTree, save_gif


def test_uniform_image_becomes_one_leaf() -> None:
    image = Image.new("RGB", (8, 8), (20, 40, 60))
    tree = ImageQuadTree(image, compression=50)
    root = tree.build()
    assert root.is_leaf
    assert tree.compress().getpixel((4, 4)) == (20, 40, 60)


def test_compression_splits_high_contrast_image() -> None:
    image = Image.new("RGB", (8, 8), "white")
    for x in range(4):
        for y in range(8):
            image.putpixel((x, y), (0, 0, 0))
    tree = ImageQuadTree(image, compression=0, min_size=1)
    assert not tree.build().is_leaf
    assert tree.with_boundaries().size == image.size


def test_boundaries_are_in_animation_gif_for_four_uniform_regions(
    tmp_path: Path,
) -> None:
    image = Image.new("RGB", (8, 8))
    colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0))
    quadrants = ((0, 0), (4, 0), (0, 4), (4, 4))
    for quadrant, color in zip(quadrants, colors):
        for x in range(quadrant[0], quadrant[0] + 4):
            for y in range(quadrant[1], quadrant[1] + 4):
                image.putpixel((x, y), color)

    tree = ImageQuadTree(image, compression=0, min_size=1)
    frames = tree.animation_frames()
    gif_path = tmp_path / "boundaries.gif"
    save_gif(frames, str(gif_path))
    with Image.open(gif_path) as gif:
        gif.seek(gif.n_frames - 1)
        visualizations = (tree.with_boundaries(), frames[-1], gif.convert("RGB"))

    for result in visualizations:
        assert all(
            result.getpixel((x, y)) == (255, 0, 0)
            for x in (3, 4, 5)
            for y in range(8)
        )
        assert all(
            result.getpixel((x, y)) == (255, 0, 0)
            for x in range(8)
            for y in (3, 4, 5)
        )


def test_animation_contains_multiple_levels() -> None:
    image = Image.new("RGB", (8, 8), "white")
    image.putpixel((0, 0), (0, 0, 0))
    tree = ImageQuadTree(image, compression=0, min_size=1)
    assert len(tree.animation_frames()) > 1
