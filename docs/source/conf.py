# pylint: disable-all
# #!/usr/bin/env python
#
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
sys.setrecursionlimit(1500)

# -- Project information -----------------------------------------------------

# General information about the project.
project = "mesh3d"
copyright = "2022, CNES"
author = "Chloe Thenoz (Magellium), Lisa Vo Thanh (Magellium)"

# The full version, including alpha/beta/rc tags
from pkg_resources import get_distribution

try:
    version = get_distribution("mesh3d").version
    release = version
except Exception as error:
    print("WARNING: cannot find mesh3d version")
    version = "Unknown"
    release = version

# The master toctree document.
master_doc = "index"

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.ifconfig",  # add if config possibility in rst files
    "sphinx.ext.intersphinx",  # other projects automatic links to doc
    "sphinx.ext.mathjax",  # Add rst math capabilities with :math:
    "sphinx.ext.autodoc",  # apidoc automatic generation
    "sphinx.ext.viewcode",  # viewcode in automatic apidoc
    "sphinx.ext.napoleon",  # to read the numpy doc format
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Title
html_title = "Mesh 3D Documentation"
html_short_title = "Mesh 3D Documentation"

# Logo
# html_logo = "images/picto_transparent_mini.png"

# Favicon
# html_favicon = "images/favicon_noname.ico"

# Theme options
html_theme_options = {
    "logo_only": True,
    "navigation_depth": 3,
}

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ["css/my_custom.css"]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "letterpaper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    "preamble": "",
    # Latex figure (float) alignment
    "figure_align": "htbp",
}
numfig = True

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "mesh3d.tex",
        "Mesh 3D documentation",
        "TODO",
        "manual",
    ),
]
