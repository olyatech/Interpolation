"""Command-line interface for image interpolation tool."""

from __future__ import annotations

import click
from PIL import Image

from interpolation.interpolation import resize_image


@click.group()
def cli() -> None:
    """Interpolation instrument for images."""
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
    """Change image size using interpolation."""
    if width <= 0 or height <= 0:
        raise click.BadParameter("Width and height must be positive integers")

    with Image.open(input_path) as img:
        result = resize_image(img, y_size=width, x_size=height, algorithm=algorithm)
        result.save(output_path)
    click.echo(f"Saved to {output_path}")


def main() -> None:
    """Entry point for the CLI application."""
    cli(prog_name="interpolation")
