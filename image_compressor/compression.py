"""Quadtree-based image compression."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Iterable, Optional

from PIL import Image, ImageDraw


Color = tuple[int, int, int]


@dataclass
class ImageNode:
    """A node in an image quadtree."""

    box: tuple[int, int, int, int]
    color: Color
    children: Optional[tuple["ImageNode", ...]] = None

    @property
    def is_leaf(self) -> bool:
        """Return whether this node has no children."""
        return self.children is None


class ImageQuadTree:
    """Build and render a quadtree representation of an RGB image."""

    def __init__(
        self,
        image: Image.Image,
        compression: int,
        min_size: int = 2,
        max_depth: int = 12,
        workers: int = 1,
    ) -> None:
        """Initialize compression settings and validate arguments."""
        if not 0 <= compression <= 100:
            raise ValueError("compression must be between 0 and 100")
        if min_size < 1:
            raise ValueError("min_size must be positive")
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative")
        if workers < 1:
            raise ValueError("workers must be positive")
        self.image = image.convert("RGB")
        self.compression = compression
        self.min_size = min_size
        self.max_depth = max_depth
        self.workers = workers
        self.root: Optional[ImageNode] = None

    @property
    def threshold(self) -> float:
        """Return the allowed mean color error for a node."""
        return self.compression * 64 / 100

    def build(self) -> ImageNode:
        """Build and return the image quadtree."""
        self.root = self._build_node((0, 0, *self.image.size), 0)
        return self.root

    def compress(self) -> Image.Image:
        """Return an image reconstructed from quadtree leaf colors."""
        root = self.root or self.build()
        result = Image.new("RGB", self.image.size)
        draw = ImageDraw.Draw(result)
        for node in self._leaves(root):
            draw.rectangle(node.box, fill=node.color)
        return result

    def with_boundaries(self, color: tuple[int, int, int] = (255, 0, 0)) -> Image.Image:
        """Return the compressed image with all quadtree boundaries drawn."""
        root = self.root or self.build()
        result = self.compress()
        draw = ImageDraw.Draw(result)
        for node in self._leaves(root):
            self._draw_box_outline(draw, node.box, color)
        return result

    def animation_frames(
        self,
        show_boundaries: bool = True,
        boundary_color: Color = (255, 0, 0),
    ) -> list[Image.Image]:
        """Return images showing progressively deeper compression levels."""
        root = self.root or self.build()
        levels = max((self._depth(node) for node in self._nodes(root)), default=0)
        return [
            self._render_at_depth(
                root,
                level,
                show_boundaries=show_boundaries,
                boundary_color=boundary_color,
            )
            for level in range(levels + 1)
        ]

    def _draw_box_outline(
        self,
        draw: ImageDraw.ImageDraw,
        box: tuple[int, int, int, int],
        color: Color,
    ) -> None:
        left, top, right, bottom = box
        width = min(3, max(1, min(right - left, bottom - top) // 2))
        draw.rectangle(box, outline=color, width=width)

    def _build_node(
        self, box: tuple[int, int, int, int], depth: int
    ) -> ImageNode:
        color, error = self._statistics(box)
        left, top, right, bottom = box
        width, height = right - left, bottom - top
        if (
            depth >= self.max_depth
            or width <= self.min_size
            or height <= self.min_size
            or error <= self.threshold
        ):
            return ImageNode(box, color)
        mid_x, mid_y = left + width // 2, top + height // 2
        boxes = tuple(
            candidate
            for candidate in (
                (left, top, mid_x, mid_y),
                (mid_x, top, right, mid_y),
                (left, mid_y, mid_x, bottom),
                (mid_x, mid_y, right, bottom),
            )
            if candidate[2] > candidate[0] and candidate[3] > candidate[1]
        )
        if depth == 0 and self.workers > 1 and len(boxes) > 1:
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                children = tuple(
                    executor.map(
                        lambda child_box: self._build_node(child_box, depth + 1),
                        boxes,
                    )
                )
        else:
            children = tuple(self._build_node(child_box, depth + 1) for child_box in boxes)
        return ImageNode(box, color, children)

    def _statistics(self, box: tuple[int, int, int, int]) -> tuple[Color, float]:
        pixels = list(self.image.crop(box).getdata())
        count = len(pixels)
        color = tuple(sum(pixel[index] for pixel in pixels) // count for index in range(3))
        error = sum(
            sum(abs(pixel[index] - color[index]) for index in range(3)) / 3
            for pixel in pixels
        ) / count
        return color, error

    def _leaves(self, node: ImageNode) -> Iterable[ImageNode]:
        if node.is_leaf:
            yield node
            return
        for child in node.children or ():
            yield from self._leaves(child)

    def _nodes(self, node: ImageNode) -> Iterable[ImageNode]:
        yield node
        for child in node.children or ():
            yield from self._nodes(child)

    def _depth(self, node: ImageNode) -> int:
        if node.is_leaf:
            return 0
        return 1 + max(self._depth(child) for child in node.children or ())

    def _render_at_depth(
        self,
        root: ImageNode,
        depth: int,
        show_boundaries: bool = True,
        boundary_color: Color = (255, 0, 0),
    ) -> Image.Image:
        result = Image.new("RGB", self.image.size)
        draw = ImageDraw.Draw(result)

        def render(node: ImageNode, remaining: int) -> None:
            if remaining == 0 or node.is_leaf:
                draw.rectangle(node.box, fill=node.color)
                if show_boundaries:
                    self._draw_box_outline(draw, node.box, boundary_color)
                return
            for child in node.children or ():
                render(child, remaining - 1)

        render(root, depth)
        return result


def save_gif(frames: list[Image.Image], path: str, duration: int = 250) -> None:
    """Save animation frames as a looping GIF."""
    if not frames:
        raise ValueError("at least one frame is required")
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
    )