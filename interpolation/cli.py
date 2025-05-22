"""Command-line interface for image interpolation tool."""

from __future__ import annotations

import click
from PIL import Image

from interpolation.interpolation import resize_image


@click.group()
def cli() -> None:
    """Command-line interface group for image interpolation operations.

    This CLI provides commands for performing various image interpolation operations.
    """
    pass


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
@click.option("--width", type=int, help="Target width in pixels", required=True)
@click.option("--height", type=int, help="Target height in pixels", required=True)
@click.option(
    "--algorithm",
    type=click.Choice(["bilinear"]),
    default="bilinear",
    show_default=True,
)
def resize(input_path: str, output_path: str, width: int, height: int, algorithm: str) -> None:
    """Resizes an image to specified dimensions using interpolation.

    Args:
        input_path: Path to the input image file.
        output_path: Path where the resized image will be saved.
        width: Target width in pixels (must be positive).
        height: Target height in pixels (must be positive).
        algorithm: Interpolation algorithm to use (currently only 'bilinear' supported).

    Raises:
        click.BadParameter: If width or height are not positive integers.
        IOError: If there are issues reading the input file or writing the output file.

    Example:
        $ interpolation resize input.jpg output.jpg --width 800 --height 600

    """
    if width <= 0 or height <= 0:
        raise click.BadParameter("Width and height must be positive integers")

    with Image.open(input_path) as img:
        result = resize_image(img, y_size=width, x_size=height, algorithm=algorithm)
        result.save(output_path)
    click.echo(f"Saved to {output_path}")


def main() -> None:
    """Entry point for the command-line interface.

    This function serves as the main entry point when the package is run as a script.
    It initializes and runs the Click CLI interface.

    Example:
        $ interpolation --help

    """
    cli(prog_name="interpolation")
