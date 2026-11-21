"""Tests for image compression."""

from PIL import Image

from image_compressor.compression import ImageQuadTree


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


def test_animation_contains_multiple_levels() -> None:
    image = Image.new("RGB", (8, 8), "white")
    image.putpixel((0, 0), (0, 0, 0))
    tree = ImageQuadTree(image, compression=0, min_size=1)
    assert len(tree.animation_frames()) > 1
