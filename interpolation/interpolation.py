"""Image interpolation utilities using bilinear interpolation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self, Tuple

import numpy as np
from PIL import Image


class GridLike(ABC):
    """Parent class for every class implementing grid."""

    @abstractmethod
    def get_value(self, y: float, x: float) -> float:
        """Return value in (y, x) point from grid.

        :param y: y coord.
        :param x: x coord.
        :return: value in (y, x) point.
        """
        pass


class BilinearInterpolator:
    """Bilinear interpolation at rectangular regular grid."""

    def __init__(self, src_grid: GridLike) -> None:
        """Init interpolator with grid object.

        :param src_grid: source grid, should have get_value(y: float, x: float) -> float method.
        """
        self.src_grid = src_grid

    def interpolate(self, target_grid: GridLike) -> np.ndarray:
        """Perform bilinear interpolation for given grid.

        :param target_grid: target grid to interpolate values for.
        :return: values array for target grid.
        """
        values = np.zeros(shape=target_grid.shape)

        for (iy, y) in enumerate(target_grid.points[0]):
            for (ix, x) in enumerate(target_grid.points[1]):
                # Find bounding cell for point on src grid
                left, down, right, up = self._find_bounding_cell(y, x)

                # Get values at bounding cell vertexes
                q11 = self.src_grid.get_value(down, left)
                q12 = self.src_grid.get_value(up, left)
                q21 = self.src_grid.get_value(down, right)
                q22 = self.src_grid.get_value(up, right)

                # Bilinear interpolation
                if right == left and up == down: # point matches with src grid point
                    values[iy, ix] = self.src_grid.get_value(y, x)

                elif right == left: # point lies on the grid line
                    values[iy, ix] = (q11 * (up - y) + q12 * (y - down)) / (up - down)

                elif up == down: # point lies on the grid line
                    values[iy, ix] = (q11 * (right - x) + q21 * (x - left)) / (right - left)

                else: # point is strictly inside of the bounding cell
                    values[iy, ix] = (q11 * (right - x) * (up - y) +
                                      q21 * (x - left) * (up - y) +
                                      q12 * (right - x) * (y - down) +
                                      q22 * (x - left) * (y - down)) / ((right - left) * (up - down))

        return values

    def _find_bounding_cell(self, y: float, x: float) -> Tuple[float, float, float, float]:
        """Find bounding cell for point (y,x).

        :return: (x0, y0, x1, y1) - coords of rectangle vertexes.
        :raises ValueError: point out of grid bounds.
        """
        if not ((self.src_grid.points[1][0] <= x <= self.src_grid.points[1][-1] and
                 self.src_grid.points[0][0] <= y <= self.src_grid.points[0][-1])):
            raise ValueError(f"Point is out of grid bounds, required:"
                             f"\n{self.src_grid.points[1][0]} <= {x} <= {self.src_grid.points[1][-1]}"
                             f"\n{self.src_grid.points[0][0]} <= {y} <= {self.src_grid.points[0][-1]}")

        left_bound = np.searchsorted(self.src_grid.points[1], x) - 1
        down_bound = np.searchsorted(self.src_grid.points[0], y) - 1

        return (
            self.src_grid.points[1][left_bound], self.src_grid.points[0][down_bound],
            self.src_grid.points[1][left_bound + 1], self.src_grid.points[0][down_bound + 1]
        )


class RectangularGrid(GridLike):
    """Rectangular regular grid."""

    def __init__(self, points: Tuple[np.array, np.array], values: np.ndarray = None) -> None:
        """Init rectangular grid by grid and values.

        :param nodes: The points defining the regular grid in 2 dimensions. The points in each dimension
                      (i.e. every elements of the points tuple) must be strictly ascending.
        :param values: The data on the regular grid.
        """
        self.points = points
        self.shape = (len(points[0]), len(points[1]))

        if self.shape[0] == 0 or self.shape[1] == 0:
            raise ValueError(f"Empty grid with shape ({self.shape[0]}, {self.shape[1]})")

        self.values = values
        if values is not None:
            # Check shape match
            if values.shape != self.shape:
                raise ValueError(f"Values and grid shape mismatch ({values.shape} != {self.shape})")

    @classmethod
    def from_image(cls, image: Image.Image) -> Self:
        """Create grid from image."""
        img_array = np.array(image)
        height, width = img_array.shape[:2]

        x_coords = np.arange(width)
        y_coords = np.arange(height)

        return cls((y_coords, x_coords), img_array)

    def to_image(self) -> Image.Image:
        """Convert grid to Image."""
        if self.values is None:
            raise ValueError("Grid has no values to convert to image")

        return Image.fromarray(self.values.astype('uint8'))

    def get_value(self, y: float, x: float) -> float:
        """Return value in (y, x) point from grid.

        :param y: y coord.
        :param x: x coord.
        :return: value in (y, x) point.
        """
        iy = np.searchsorted(self.points[0], y)
        ix = np.searchsorted(self.points[1], x)

        # Check if the point is on grid and return value
        if ix < len(self.points[1]) and iy < len(self.points[0]):
            if self.points[1][ix] == x and self.points[0][iy] == y:
                return self.values[iy, ix]

        raise ValueError(f"Point ({y}, {x}) not found in grid nodes")

def resize_image(image: Image.Image, y_size: int, x_size: int, algorithm: str = 'bilinear') -> Image.Image:
    """Resize image to given shape."""
    src_width, src_height = image.size

    # Create a grid from image
    src_grid = RectangularGrid.from_image(image)

    # Grid for resized image
    y_grid = np.arange(0, src_height - 1, (src_height - 1) / y_size)
    x_grid = np.arange(0, src_width - 1, (src_width - 1) / x_size)

    # Interpolate values for new grid
    if algorithm == 'bilinear':
        interpolator = BilinearInterpolator(src_grid)
        res_grid = RectangularGrid(points=(y_grid, x_grid))
        res_grid.values = interpolator.interpolate(res_grid)
    else:
        raise NotImplementedError("unknown interpolation algorithm")

    # Convert to image
    resized_img = res_grid.to_image()

    return resized_img
