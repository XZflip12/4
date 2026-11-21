"""Tests for the point quadtree."""

from image_compressor.quadtree import Point, QuadTree, Rectangle


def test_insert_and_query_range() -> None:
    tree = QuadTree(Rectangle(0, 0, 100, 100), capacity=1)
    points = [Point(10, 10, "a"), Point(80, 80, "b"), Point(50, 50, "c")]
    for point in points:
        assert tree.insert(point)

    assert set(tree.query_range(Rectangle(0, 0, 60, 60))) == {points[0], points[2]}


def test_remove_point() -> None:
    tree = QuadTree(Rectangle(0, 0, 10, 10))
    point = Point(2, 3)
    assert tree.insert(point)
    assert tree.remove(point)
    assert not tree.remove(point)
    assert list(tree) == []


def test_outside_point_is_rejected() -> None:
    tree = QuadTree(Rectangle(0, 0, 10, 10))
    assert not tree.insert(Point(10, 10))
