# Interpolation

This repository contains realization of algorithms from paper [1]. Project was created as the part of python course in IITP RAS. I follow python tooling guide [2].

## Installation and usage

I use pyenv+poetry btw. To get the module follow this commands:
```shell

    git clone https://github.com/olyatech/Interpolation.git

    cd Interpolation

    curl -sSL https://install.python-poetry.org | python3 - && poetry --version

    poetry config virtualenvs.in-project true

    cd Interpolation

    poetry install

```

## Functionality

Module in named `interpolation` and is stored in `/interpolation` folder. It provides a class `RegularGrid`and classes that implement interpolation algorithms. 

A description of the currently implemented algorithms is contained in the section "Implemented algorithms".

Also you can run script that resizes images. Use `poetry run resize`. Usage:
```
Usage: resize [OPTIONS] INPUT_PATH OUTPUT_PATH

  Change image size using interpolation

Options:
  --width INTEGER         Target width in pixels
  --height INTEGER        Target height in pixels
  --algorithm [bilinear]  [default: bilinear]
  --help                  Show this message and exit.
```


## Implemented algorithms

- Bilinear interpolation. Obvious [link](https://en.wikipedia.org/wiki/Bilinear_interpolation) to find more information about algorithm


## References:

[1] A. Adam, D. Pavlidis, J.R. Percival, P. Salinas, Z. Xie, F. Fang, C.C. Pain, A.H. Muggeridge, M.D. Jackson,
Higher-order conservative interpolation between control-volume meshes: Application to advection and multiphase flow problems with dynamic mesh adaptivity,
Journal of Computational Physics,
Volume 321,
2016.

[2] https://cjolowicz.github.io/posts/