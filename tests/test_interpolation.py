import pytest
import numpy as np
from PIL import Image
from interpolation.interpolation import RectangularGrid, BilinearInterpolator, resize_image

# Tests for RectangularGrid class
@pytest.fixture
def sample_grid():
    points = (np.array([0, 1, 2]), np.array([0, 1, 2]))  # 3x3 grid
    values = np.array([[1.0, 2.0, 3.0], 
                      [4.0, 5.0, 6.0], 
                      [7.0, 8.0, 9.0]])
    return RectangularGrid(points, values)

def test_rectangular_grid_init():
    points = (np.array([0, 1]), np.array([0, 1]))
    values = np.array([[1.0, 2.0], [3.0, 4.0]])
    grid = RectangularGrid(points, values)
    assert grid.shape == (2, 2)
    
    with pytest.raises(ValueError):
        RectangularGrid(points, np.array([1, 2, 3]))  # Wrong shape

def test_get_value(sample_grid):
    assert sample_grid.get_value(0, 0) == 1.0
    assert sample_grid.get_value(1, 1) == 5.0
    with pytest.raises(ValueError):
        sample_grid.get_value(5, 5)  # Out of bounds

def test_from_image():
    img = Image.new('L', (2, 2))
    img.putdata([1, 2, 3, 4])
    grid = RectangularGrid.from_image(img)
    assert grid.shape == (2, 2)
    assert grid.get_value(0, 0) == 1

def test_to_image(sample_grid):
    img = sample_grid.to_image()
    assert isinstance(img, Image.Image)
    assert img.size == (3, 3)

def test_empty_grid_to_image():
    grid = RectangularGrid((np.ones(3), np.ones(3)))
    with pytest.raises(ValueError):
        img = grid.to_image()

# Tests for BilinearInterpolator
def test_interpolator_init(sample_grid):
    interpolator = BilinearInterpolator(sample_grid)
    assert interpolator.src_grid == sample_grid

@pytest.mark.parametrize("y,x,expected", [
    (0, 0, 1.0),    # Exact point
    (0.5, 0.5, 3.0), # Center
    (1, 1, 5.0),     # Exact point
    (0.5, 0, 2.5),   # Vertical middle
    (0, 0.5, 1.5)    # Horizontal middle
])
def test_interpolation(sample_grid, y, x, expected):
    interpolator = BilinearInterpolator(sample_grid)
    target = RectangularGrid((np.array([y]), np.array([x])))
    result = interpolator.interpolate(target)
    assert np.isclose(result[0, 0], expected, rtol=1e-5)

def test_find_bounding_cell(sample_grid):
    interpolator = BilinearInterpolator(sample_grid)
    assert interpolator._find_bounding_cell(0.5, 0.5) == (0, 0, 1, 1)
    with pytest.raises(ValueError):
        interpolator._find_bounding_cell(5, 5)  # Out of bounds

# Tests for resize_image
def test_resize_image():
    img = Image.new('L', (4, 4))
    img.putdata(range(16))
    
    # Test downscaling
    small = resize_image(img, 2, 2)
    assert small.size == (2, 2)
    
    # Test upscaling
    large = resize_image(img, 8, 8)
    assert large.size == (8, 8)
    
    # Test invalid algorithm
    with pytest.raises(NotImplementedError):
        resize_image(img, 2, 2, 'invalid')

# Edge cases
def test_edge_cases():
    # Single point grid
    points = (np.array([0]), np.array([0]))
    values = np.array([[1.0]])
    grid = RectangularGrid(points, values)
    interpolator = BilinearInterpolator(grid)
    result = interpolator.interpolate(RectangularGrid((np.array([0]), np.array([0]))))
    assert result[0, 0] == 1.0
    
    # Empty grid
    with pytest.raises(ValueError):
        RectangularGrid((np.array([]), np.array([])))

