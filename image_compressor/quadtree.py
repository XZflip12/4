"""Two-dimensional point quadtree implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Point:
    """A point stored in a quadtree."""

    x: float
    y: float
    value: object = None


@dataclass(frozen=True)
class Rectangle:
    """Axis-aligned rectangle represented by its top-left corner and size."""

    x: float
    y: float
    width: float
    height: float

    def contains(self, point: Point) -> bool:
        """Return whether the rectangle contains the point."""
        return (
            self.x <= point.x < self.x + self.width
            and self.y <= point.y < self.y + self.height
        )

    def intersects(self, other: "Rectangle") -> bool:
        """Return whether two rectangles overlap."""
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )


class QuadTree(Generic[T]):
    """A bounded point quadtree supporting insertion, deletion and range queries."""

    def __init__(
        self,
        boundary: Rectangle,
        capacity: int = 8,
        max_depth: int = 24,
    ) -> None:
        """Create a tree for *boundary* with a maximum leaf capacity."""
        if capacity < 1:
            raise ValueError("capacity must be positive")
        if boundary.width <= 0 or boundary.height <= 0:
            raise ValueError("boundary dimensions must be positive")
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative")
        self._boundary = boundary
        self._capacity = capacity
        self._max_depth = max_depth
        self._points: list[Point] = []
        self._children: Optional[tuple[QuadTree[T], ...]] = None

    @property
    def boundary(self) -> Rectangle:
        """Return the boundary covered by this node."""
        return self._boundary

    @property
    def points(self) -> tuple[Point, ...]:
        """Return points held directly by this node."""
        return tuple(self._points)

    @property
    def children(self) -> tuple["QuadTree[T]", ...]:
        """Return child nodes, or an empty tuple for a leaf."""
        return self._children or ()

    def insert(self, point: Point) -> bool:
        """Insert a point and return whether it was inside this tree."""
        if not self._boundary.contains(point):
            return False
        if self._children is None:
            if len(self._points) < self._capacity or self._max_depth == 0:
                self._points.append(point)
                return True
            self._subdivide()
        for child in self.children:
            if child.insert(point):
                return True
        return False

    def remove(self, point: Point) -> bool:
        """Remove one equal point and return whether it was found."""
        if not self._boundary.contains(point):
            return False
        for index, candidate in enumerate(self._points):
            if candidate == point:
                self._points.pop(index)
                return True
        for child in self.children:
            if child.remove(point):
                self._collapse_if_empty()
                return True
        return False

    def query_range(self, area: Rectangle) -> list[Point]:
        """Return all points contained in *area*."""
        if not self._boundary.intersects(area):
            return []
        result = [point for point in self._points if area.contains(point)]
        for child in self.children:
            result.extend(child.query_range(area))
        return result

    def __iter__(self) -> Iterator[Point]:
        """Iterate through all points in the subtree."""
        yield from self._points
        for child in self.children:
            yield from child

    def _subdivide(self) -> None:
        half_width = self._boundary.width / 2
        half_height = self._boundary.height / 2
        x, y = self._boundary.x, self._boundary.y
        depth = self._max_depth - 1
        boundaries = (
            Rectangle(x, y, half_width, half_height),
            Rectangle(x + half_width, y, half_width, half_height),
            Rectangle(x, y + half_height, half_width, half_height),
            Rectangle(x + half_width, y + half_height, half_width, half_height),
        )
        self._children = tuple(
            QuadTree(boundary, self._capacity, depth) for boundary in boundaries
        )
        old_points = self._points
        self._points = []
        for point in old_points:
            for child in self.children:
                if child.insert(point):
                    break

    def _collapse_if_empty(self) -> None:
        if self._children and not any(self._children):
            self._children = None
