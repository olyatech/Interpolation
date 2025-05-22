import numpy as np
from typing import List, Tuple, Dict

class BilinearInterpolator:
    """
    Bilinear interpolation at rectangular regular grid
    """
    def __init__(self, src_grid):
        """
        Init interpolator
        
        :param src_grid: source grid, should have get_value(x,y) method
        """
        self.src_grid = src_grid
    
    def interpolate(self, target_grid):
        """
        Performs bilinear interpolation for given grid
    
        :param target_grid: target grid to interpolate values for
        :return: values array for target grid
        """
        values = np.zeros(shape=target_grid.shape)
        
        for i, (x, y) in enumerate(self.target_grid.nodes):
            # Find bounding cell for point on src grid
            left, down, right, up = self._find_bounding_cell(x, y)
            
            # Get values at bounding cell vertexes
            q11 = self.src_grid.get_value(left, down)
            q12 = self.src_grid.get_value(left, up)
            q21 = self.src_grid.get_value(right, down)
            q22 = self.src_grid.get_value(right, up)
            
            # Bilinear interpolation
            if right == left and up == down: # point matches with src grid point
                values[i] = self.src_grid.get_value(x, y)

            elif right == left: # point lies on the grid line
                values[i] = (q11 * (up - y) + q12 * (y - down)) / (up - down)
            
            elif up == down: # point lies on the grid line
                values[i] = (q11 * (right - x) + q21 * (x - left)) / (right - left)

            else: # point is strictly inside of the bounding cell
                values[i] = (q11 * (right - x) * (up - y) +
                             q21 * (x - left) * (up - y) +
                             q12 * (right - x) * (y - down) +
                             q22 * (x - left) * (y - down)) / ((right - left) * (up - down))

        return values
    
    def find_bounding_cell(self, x: float, y: float) -> Tuple[float, float, float, float]:
        """
        Finds bounding cell for point (y,x)
        :return: (x0, y0, x1, y1) - coords of rectangle vertexes
        :raises ValueError: point out of grid bounds
        """
        if not ((self._x_coords[0] <= x <= self._x_coords[-1] and 
                 self._y_coords[0] <= y <= self._y_coords[-1])):
            raise ValueError("Point is out of grid bounds")
        
        left_bound = np.searchsorted(self.src_grid.points[0], x) - 1
        down_bound = np.searchsorted(self.src_grid.points[1], y) - 1
        
        return (
            self._x_coords[left_bound], self._y_coords[down_bound],
            self._x_coords[left_bound + 1], self._y_coords[down_bound + 1]
        )


class RectangularGrid:
    """
    Прямоугольная сетка для билинейной интерполяции
    Поддерживает регулярные сетки
    """
    
    def __init__(self, points: Tuple[np.array], values: np.ndarray = None):
        """
        :param nodes: The points defining the regular grid in 2 dimensions. The points in each 
                      dimension (i.e. every elements of the points tuple) must be strictly ascending.
        :param values: The data on the regular grid. 
        """
        self.points = points
        self.shape = (len(points[0]), len(points[1]))

        self.values = values
        if values is not None:
            # Check shape match
            if values.shape != self.shape:
                raise ValueError(f"Values and grid shape mismatch ({values.shape} != {self.shape})")
    
    def get_value(self, x: float, y: float) -> float:
        """
        Returns value in (y, x) point from grid
        :param y: y coord
        :param x: x coord
        :return: value in (y, x) point
        """
        iy = np.searchsorted(self.points[0], y)
        ix = np.searchsorted(self.points[1], x)
        
        # Check if the point is on grid and return value
        if ix < len(self._x_coords) and iy < len(self._y_coords):
            if self.points[1, ix] == x and self.points[0, iy] == y:
                return self.values[iy, ix]
            
        raise ValueError(f"Point ({y}, {x}) not found in grid nodes")

