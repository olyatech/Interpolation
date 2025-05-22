API Reference
=============

.. currentmodule:: interpolation.interpolation

This section provides an overview of the ``interpolation`` module functionality.

Overview
---------------------

Module contains BilinearInterpolation class designed to work with GridLike objects. Also there is 
a RectangularGrid class derived from GridLike and implementing a regular rectangular grid.

Detailed Descriptions
---------------------

BilinearInterpolation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose:**  
Provide Bilinear Interpolation from source grid (GridLike object) to any destination grid (GridLike object)

**Init:**

- **target_grid:** target grid to interpolate values for.

**Methods**
- **interpolate(self, target_grid: GridLike) -> np.ndarray:** performs interpolation.

**Example:**

.. code-block:: python

    import numpy as np
    from interpolation.interpolation import RectangularGrid

    src_points = (np.array([0, 1, 2]), np.array([0, 1, 2]))  # 3x3 grid
    src_values = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    src_grid = RectangularGrid(points, values)

    dest_points = (np.array([0, 1]), np.array([0, 1]))
    dest_grid = RectangularGrid(dest_points)
    dest_grid.values = src_grid.interpolate(dest_grid)


GridLike
~~~~~~~~~~~~~~~~~~~~

**Purpose:**  
Abstract class with key requirements to work with BilinearInterpolation

**Methods:**

- **get_value(self, y: float, x: float) -> float**: Return value in (y, x) point from grid.

- **points(self) -> Tuple[np.ndarray, np.ndarray]**: Get grid points as a tuple of (y_coords, x_coords) arrays.

- **shape(self) -> Tuple[int, int]**: Get grid dimensions as (height, width).


**Returns:**  
Interpolated value(s) at the specified coordinates.


RectangularGrid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose:**  
Implementation of rectangular regular grid

**Methods:**
- **__init__(self, points: Tuple[np.ndarray, np.ndarray], values: Optional[np.ndarray] = None) -> None**: Init rectangular grid by grid and values.

- **points(self) -> Tuple[np.ndarray, np.ndarray]:** Get grid points as a tuple of (y_coords, x_coords) arrays.

- **shape(self) -> Tuple[int, int]:** Get grid dimensions as (height, width).

- **from_image(cls, image: Image.Image) -> Self:** Create grid from image.

- **to_image(self) -> Image.Image:** Convert grid to PIL.Image.

- **get_value(self, y: float, x: float) -> float:** Return value in (y, x) point from grid.

- **resize_image(image: Image.Image, y_size: int, x_size: int, algorithm: str = "bilinear") -> Image.Image:** Resize image to given shape.


**Example:**

.. code-block:: python

    import numpy as np
    from interpolation.interpolation import RectangularGrid

    points = (np.array([0, 1, 2]), np.array([0, 1, 2]))  # 3x3 grid
    values = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    grid = RectangularGrid(points, values)


