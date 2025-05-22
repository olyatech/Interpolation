"""Image interpolation utilities using bilinear interpolation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Self, Tuple

import numpy as np
from PIL import Image


class GridLike(ABC):
    """Abstract base class for grid-like data structures.

    This class defines the interface that all grid implementations must follow.
    """

    @abstractmethod
    def get_value(self, y: float, x: float) -> float:
        """Return the value at the given (y, x) coordinates in the grid.

        Args:
            y: The y-coordinate (vertical position).
            x: The x-coordinate (horizontal position).

        Returns:
            The value at the specified coordinates.

        Raises:
            NotImplementedError: If the method is not implemented by subclass.

        """
        raise NotImplementedError("get_value should be implemented")

    @property
    @abstractmethod
    def points(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns the grid points as coordinate arrays.

        Returns:
            A tuple containing (y_coordinates, x_coordinates) as numpy arrays.

        Raises:
            NotImplementedError: If the method is not implemented by subclass.

        """
        raise NotImplementedError("points should be implemented")

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """Returns the dimensions of the grid.

        Returns:
            A tuple of (height, width) representing grid dimensions.

        Raises:
            NotImplementedError: If the method is not implemented by subclass.

        """
        raise NotImplementedError("shape should be implemented")
    
    @property
    @abstractmethod
    def find_bounding_cell(self, y: float, x: float) -> Tuple[float, float, float, float]:
        """Find the bounding cell for a given point (y, x).

        Args:
            y: The y-coordinate of the point.
            x: The x-coordinate of the point.

        Returns:
            A tuple (x0, y0, x1, y1) representing the coordinates of the bounding rectangle vertices.

        Raises:
            ValueError: If the point is outside the grid bounds.

        """


class BilinearInterpolator:
    """Performs bilinear interpolation on a regular rectangular grid.

    Attributes:
        src_grid: The source grid to interpolate from.

    Example:
        >>> import numpy as np
        >>> from interpolation.interpolation import RectangularGrid, BilinearInterpolator
        >>> 
        >>> src_points = (np.array([0, 1, 2]), np.array([0, 1, 2]))  # 3x3 grid
        >>> src_values = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        >>> src_grid = RectangularGrid(points, values)
        >>> interpolator = BilinearInterpolator(src_grid)
        >>> 
        >>> dest_points = (np.array([0, 1]), np.array([0, 1]))
        >>> dest_grid = RectangularGrid(dest_points)
        >>> dest_grid.values = interpolator.interpolate(dest_grid)

    """

    def __init__(self, src_grid: GridLike) -> None:
        """Initialize the interpolator with a source grid.

        Args:
            src_grid: The source grid implementing the GridLike interface.

        """
        self.src_grid = src_grid

    def interpolate(self, target_grid: GridLike) -> np.ndarray:
        """Perform bilinear interpolation to estimate values at target grid points.

        Args:
            target_grid: The target grid to interpolate values for.

        Returns:
            A numpy array containing interpolated values for the target grid.

        """
        values = np.zeros(shape=target_grid.shape)

        for iy, y in enumerate(target_grid.points[0]):
            for ix, x in enumerate(target_grid.points[1]):
                # Find bounding cell for point on src grid
                left, down, right, up = self.src_grid.find_bounding_cell(y, x)

                # Get values at bounding cell vertexes
                q11 = self.src_grid.get_value(down, left)
                q12 = self.src_grid.get_value(up, left)
                q21 = self.src_grid.get_value(down, right)
                q22 = self.src_grid.get_value(up, right)

                # Bilinear interpolation
                if right == left and up == down:  # point matches with src grid point
                    values[iy, ix] = self.src_grid.get_value(y, x)

                elif right == left:  # point lies on the grid line
                    values[iy, ix] = (q11 * (up - y) + q12 * (y - down)) / (up - down)

                elif up == down:  # point lies on the grid line
                    values[iy, ix] = (q11 * (right - x) + q21 * (x - left)) / (right - left)

                else:  # point is strictly inside of the bounding cell
                    values[iy, ix] = (
                        q11 * (right - x) * (up - y)
                        + q21 * (x - left) * (up - y)
                        + q12 * (right - x) * (y - down)
                        + q22 * (x - left) * (y - down)
                    ) / ((right - left) * (up - down))

        return values


class RectangularGrid(GridLike):
    """Implementation of a regular rectangular grid.

    Attributes:
        _points: Tuple of (y_coords, x_coords) numpy arrays.
        _shape: Tuple of (height, width) representing grid dimensions.
        values: Optional numpy array containing grid values.

    Example:
        >>> import numpy as np
        >>> from interpolation.interpolation import RectangularGrid
        >>> 
        >>> points = (np.array([0, 1, 2]), np.array([0, 1, 2]))  # 3x3 grid
        >>> values = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        >>> grid = RectangularGrid(points, values)

    """

    def __init__(self, points: Tuple[np.ndarray, np.ndarray], values: Optional[np.ndarray] = None) -> None:
        """Initialize the rectangular grid.

        Args:
            points: A tuple of (y_coords, x_coords) numpy arrays defining the grid.
                   Each array must be strictly ascending.
            values: Optional numpy array containing data on the grid.

        Raises:
            ValueError: If grid is empty or values shape doesn't match grid shape.

        """
        self._points = points
        self._shape = (len(points[0]), len(points[1]))

        if self._shape[0] == 0 or self._shape[1] == 0:
            raise ValueError(f"Empty grid with shape ({self._shape[0]}, {self._shape[1]})")

        self.values = values
        if values is not None:
            if values.shape != self._shape:
                raise ValueError(f"Values and grid shape mismatch ({values.shape} != {self._shape})")

    @property
    def points(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns the grid points as coordinate arrays.

        Returns:
            A tuple containing (y_coordinates, x_coordinates) as numpy arrays.

        """
        return self._points

    @property
    def shape(self) -> Tuple[int, int]:
        """Returns the dimensions of the grid.

        Returns:
            A tuple of (height, width) representing grid dimensions.

        """
        return self._shape

    @classmethod
    def from_image(cls, image: Image.Image) -> Self:
        """Create a grid from a PIL Image.

        Args:
            image: The input image to create grid from.

        Returns:
            A RectangularGrid instance representing the image.

        """
        img_array = np.array(image)
        height, width = img_array.shape[:2]

        x_coords = np.arange(width)
        y_coords = np.arange(height)

        return cls((y_coords, x_coords), img_array)

    def to_image(self) -> Image.Image:
        """Convert the grid to a PIL Image.

        Returns:
            A PIL Image created from the grid values.

        Raises:
            ValueError: If the grid has no values to convert.

        """
        if self.values is None:
            raise ValueError("Grid has no values to convert to image")

        return Image.fromarray(self.values.astype("uint8"))

    def get_value(self, y: float, x: float) -> float:
        """Return the value at the given (y, x) coordinates in the grid.

        Args:
            y: The y-coordinate (vertical position).
            x: The x-coordinate (horizontal position).

        Returns:
            The value at the specified coordinates.

        Raises:
            ValueError: If the grid has no values or the point is not found in grid nodes.

        """
        if self.values is None:
            raise ValueError("Trying to get value from grid with empty values")

        iy = np.searchsorted(self._points[0], y)
        ix = np.searchsorted(self._points[1], x)

        # Check if the point is on grid and return value
        if ix < len(self._points[1]) and iy < len(self._points[0]):
            if self._points[1][ix] == x and self._points[0][iy] == y:
                return self.values[iy, ix]

        raise ValueError(f"Point ({y}, {x}) not found in grid nodes")
    
    def find_bounding_cell(self, y: float, x: float) -> Tuple[float, float, float, float]:
        """Find the bounding cell for a given point (y, x).

        Args:
            y: The y-coordinate of the point.
            x: The x-coordinate of the point.

        Returns:
            A tuple (x0, y0, x1, y1) representing the coordinates of the bounding rectangle vertices.

        Raises:
            ValueError: If the point is outside the grid bounds.

        """
        if not (
            self._points[1][0] <= x <= self._points[1][-1]
            and self._points[0][0] <= y <= self._points[0][-1]
        ):
            raise ValueError(
                f"Point is out of grid bounds, required:"
                f"\n{self._points[1][0]} <= {x} <= {self._points[1][-1]}"
                f"\n{self._points[0][0]} <= {y} <= {self._points[0][-1]}"
            )

        left_bound = np.searchsorted(self._points[1], x) - 1
        down_bound = np.searchsorted(self._points[0], y) - 1

        return (
            self._points[1][left_bound],
            self._points[0][down_bound],
            self._points[1][left_bound + 1],
            self._points[0][down_bound + 1],
        )


def resize_image(image: Image.Image, y_size: int, x_size: int, algorithm: str = "bilinear") -> Image.Image:
    """Resizes an image to the specified dimensions using interpolation.

    Args:
        image: The input image to resize.
        y_size: The target height in pixels.
        x_size: The target width in pixels.
        algorithm: The interpolation algorithm to use (currently only "bilinear" supported).

    Returns:
        The resized image.

    Raises:
        NotImplementedError: If an unsupported interpolation algorithm is specified.

    """
    src_width, src_height = image.size

    # Create a grid from image
    src_grid = RectangularGrid.from_image(image)

    # Grid for resized image
    y_grid = np.arange(0, src_height - 1, (src_height - 1) / y_size)
    x_grid = np.arange(0, src_width - 1, (src_width - 1) / x_size)

    # Interpolate values for new grid
    if algorithm == "bilinear":
        interpolator = BilinearInterpolator(src_grid)
        res_grid = RectangularGrid(points=(y_grid, x_grid))
        res_grid.values = interpolator.interpolate(res_grid)
    else:
        raise NotImplementedError("unknown interpolation algorithm")

    # Convert to image
    resized_img = res_grid.to_image()

    return resized_img
