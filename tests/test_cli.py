"""Tests for CLI for interpolation module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
from click.testing import CliRunner, Result
from PIL import Image

from interpolation.cli import cli, main


@pytest.fixture
def runner() -> CliRunner:
    """Create CliRunner."""
    return CliRunner()


@pytest.fixture
def mock_image() -> MagicMock:
    """Create mock image using fixture."""
    img = MagicMock(spec=Image.Image)
    img.size = (100, 100)
    return img


def test_cli_group(runner: CliRunner) -> None:
    """Test that CLI group shows help."""
    result: Result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Interpolation instrument for images" in result.output
    assert "resize" in result.output


def test_resize_command_success(runner: CliRunner, mock_image: MagicMock, tmp_path: Path) -> None:
    """Test successful image resize."""
    output_path: Path = tmp_path / "output.png"

    with (
        patch("PIL.Image.open", return_value=mock_image),
        patch("interpolation.cli.resize_image", return_value=mock_image) as mock_resize,
    ):
        input_path: Path = tmp_path / "input.png"
        img: Image.Image = Image.new("RGB", (50, 50), color="red")
        img.save(input_path)

        result: Result = runner.invoke(
            cli,
            [
                "resize",
                str(input_path),
                str(output_path),
                "--width=100",
                "--height=100",
            ],
        )

        mock_resize.assert_called_once_with(ANY, y_size=100, x_size=100, algorithm="bilinear")
        assert "Saved to" in result.output
        assert result.exit_code == 0


def test_resize_command_missing_args(runner: CliRunner) -> None:
    """Test missing required arguments."""
    result: Result = runner.invoke(cli, ["resize"])
    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_resize_command_image_open_error(runner: CliRunner, tmp_path: Path) -> None:
    """Test error when opening non-existent image."""
    output_path: Path = tmp_path / "output.png"

    result: Result = runner.invoke(cli, ["resize", "nonexistent.png", str(output_path)])

    assert result.exit_code == 2
    assert "Invalid value for 'INPUT_PATH'" in result.output


def test_resize_command_missing_width_height(runner: CliRunner, tmp_path: Path) -> None:
    """Test that Click raises error when width or height is missing."""
    input_path: Path = tmp_path / "input.png"
    output_path: Path = tmp_path / "output.png"

    img: Image.Image = Image.new("RGB", (50, 50), color="red")
    img.save(input_path)

    result: Result = runner.invoke(cli, ["resize", str(input_path), str(output_path)])
    assert result.exit_code == 2


def test_resize_command_negative_dimensions(runner: CliRunner, tmp_path: Path) -> None:
    """Test that Click raises BadParameter for negative dimensions."""
    input_path: Path = tmp_path / "input.png"
    output_path: Path = tmp_path / "output.png"

    img: Image.Image = Image.new("RGB", (50, 50), color="red")
    img.save(input_path)

    result: Result = runner.invoke(
        cli,
        ["resize", str(input_path), str(output_path), "--width=-100", "--height=100"],
    )
    assert result.exit_code == 2
    assert "Width and height must be positive integers" in result.output


def test_main_function() -> None:
    """Test main entry point."""
    with patch("interpolation.cli.cli") as mock_cli:
        main()
        mock_cli.assert_called_once_with(prog_name="interpolation")


def test_resize_command_default_algorithm(runner: CliRunner, mock_image: MagicMock, tmp_path: Path) -> None:
    """Test default algorithm is used."""
    input_path: Path = tmp_path / "input.png"
    output_path: Path = tmp_path / "output.png"

    img: Image.Image = Image.new("RGB", (80, 80), color="green")
    img.save(input_path)

    with (
        patch("PIL.Image.open", return_value=mock_image),
        patch("interpolation.cli.resize_image") as mock_resize,
    ):
        result: Result = runner.invoke(
            cli,
            [
                "resize",
                str(input_path),
                str(output_path),
                "--height=100",
                "--width=100",
            ],
        )

        mock_resize.assert_called_once_with(ANY, y_size=100, x_size=100, algorithm="bilinear")
        assert result.exit_code == 0


def test_resize_command_original_dimensions(runner: CliRunner, mock_image: MagicMock, tmp_path: Path) -> None:
    """Test original dimensions are used when none specified."""
    input_path: Path = tmp_path / "input.png"
    output_path: Path = tmp_path / "output.png"

    img: Image.Image = Image.new("RGB", (200, 200), color="white")
    img.save(input_path)

    with (
        patch("PIL.Image.open", return_value=mock_image) as mock_open,
        patch("interpolation.cli.resize_image") as mock_resize,
    ):
        mock_open.return_value.size = (200, 200)

        result: Result = runner.invoke(
            cli,
            [
                "resize",
                str(input_path),
                str(output_path),
                "--width=200",
                "--height=200",
            ],
        )

        mock_resize.assert_called_once_with(ANY, y_size=200, x_size=200, algorithm="bilinear")
        assert result.exit_code == 0
