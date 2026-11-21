"""Quadtree image compression package."""

from .compression import ImageQuadTree
from .quadtree import Point, Rectangle, QuadTree

__all__ = ["ImageQuadTree", "Point", "QuadTree", "Rectangle"]
