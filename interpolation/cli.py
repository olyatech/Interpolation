import click
from PIL import Image
from interpolation.interpolation import resize_image 

@click.group()
def cli():
    """Images interpolation instrument"""
    pass

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option('--width', type=int, help='Target width in pixels')
@click.option('--height', type=int, help='Target height in pixels')
@click.option('--algorithm', type=click.Choice(['bilinear']), default='bilinear', show_default=True)
def resize(input_path, output_path, width, height, algorithm):
    """Change image size using interpolation"""
    try:
        with Image.open(input_path) as img:
            result = resize_image(img, y_size=width, x_size=height, algorithm=algorithm)
            result.save(output_path)
        click.echo(f"Saved to {output_path}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

def main():
    cli(prog_name="interpolation")