# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../'))

project = 'interpolation'
copyright = '2025, Olga Terekhova (olyatech)'
author = 'Olga Terekhova (olyatech)'
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    "myst_parser",
    "sphinx_autodoc2",
    "sphinx_click",
    "matplotlib.sphinxext.plot_directive",
    "sphinx_copybutton",
    "sphinx-book-theme",
]


templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "book"
html_title = "Interpolation"

html_static_path = ['_static', 'images']
intersphinx_mapping = {'python': ('https://docs.python.org/3/', None)}

myst_enable_extensions = ["colon_fence"]


