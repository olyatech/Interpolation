import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, ANY
from interpolation.cli import cli, main
from PIL import Image
import numpy as np

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_image():
    """Фикстура для создания mock изображения"""
    img = MagicMock(spec=Image.Image)
    img.size = (100, 100)
    return img

def test_cli_group(runner):
    """Test that CLI group shows help"""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Interpolation instrument for images" in result.output
    assert "resize" in result.output  # Проверяем наличие команды

def test_resize_command_success(runner, mock_image, tmp_path):
    """Test successful image resize"""
    output_path = tmp_path / "output.png"
    
    with patch("PIL.Image.open", return_value=mock_image), \
         patch("interpolation.cli.resize_image", return_value=mock_image) as mock_resize:
        
        # Создаем временный входной файл
        input_path = tmp_path / "input.png"
        img = Image.new("RGB", (50, 50), color="red")
        img.save(input_path)
        
        result = runner.invoke(
            cli,
            ["resize", str(input_path), str(output_path), "--width=100", "--height=100"]
        )
        
        # Проверяем вызовы
        mock_resize.assert_called_once_with(
            ANY, y_size=100, x_size=100, algorithm="bilinear"
        )
        assert "Saved to" in result.output
        assert result.exit_code == 0

def test_resize_command_missing_args(runner):
    """Test missing required arguments"""
    result = runner.invoke(cli, ["resize"])
    assert result.exit_code == 2
    assert "Missing argument" in result.output

def test_resize_command_image_open_error(runner, tmp_path):
    """Test error when opening non-existent image"""
    output_path = tmp_path / "output.png"

    result = runner.invoke(
        cli,
        ["resize", "nonexistent.png", str(output_path)]
    )
    
    assert result.exit_code == 2  # Click возвращает 2 для ошибок валидации
    assert "Invalid value for 'INPUT_PATH'" in result.output

def test_resize_command_missing_width_height(runner, tmp_path):
    """Test that Click raises error when width or height is missing"""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    
    img = Image.new("RGB", (50, 50), color="red")
    img.save(input_path)
    
    result = runner.invoke(
        cli,
        ["resize", str(input_path), str(output_path)]
    )
    assert result.exit_code == 2  # Click code 2 for validation error

def test_resize_command_negative_dimensions(runner, tmp_path):
    """Test that Click raises BadParameter for negative dimensions"""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    
    img = Image.new("RGB", (50, 50), color="red")
    img.save(input_path)
    
    result = runner.invoke(
        cli,
        ["resize", str(input_path), str(output_path), "--width=-100", "--height=100"]
    )
    assert result.exit_code == 2
    assert "Width and height must be positive integers" in result.output

def test_main_function():
    """Test main entry point"""
    with patch("interpolation.cli.cli") as mock_cli:
        main()
        mock_cli.assert_called_once_with(prog_name="interpolation")

def test_resize_command_default_algorithm(runner, mock_image, tmp_path):
    """Test default algorithm is used"""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    
    img = Image.new("RGB", (80, 80), color="green")
    img.save(input_path)
    
    with patch("PIL.Image.open", return_value=mock_image) as mock_open, \
         patch("interpolation.cli.resize_image") as mock_resize:
        
        result = runner.invoke(
            cli,
            ["resize", str(input_path), str(output_path), "--height=80", "--width=80"]
        )
        
        # Проверяем, что алгоритм по умолчанию используется
        mock_resize.assert_called_once_with(
            ANY, y_size=80, x_size=80, algorithm="bilinear"
        )
        assert result.exit_code == 0

def test_resize_command_original_dimensions(runner, mock_image, tmp_path):
    """Test original dimensions are used when none specified"""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    
    img = Image.new("RGB", (200, 200), color="white")
    img.save(input_path)
    
    with patch("PIL.Image.open", return_value=mock_image) as mock_open, \
         patch("interpolation.cli.resize_image") as mock_resize:
        
        mock_open.return_value.size = (200, 200)  # Устанавливаем размер
        
        result = runner.invoke(
            cli,
            ["resize", str(input_path), str(output_path), "--width=200", "--height=200"]
        )
        
        # Проверяем, что используются оригинальные размеры
        mock_resize.assert_called_once_with(
            ANY, y_size=200, x_size=200, algorithm="bilinear"
        )
        assert result.exit_code == 0