# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_bootstrap_theme
sys.path.insert(0, os.path.abspath('sphinxext'))


# -- Project information -----------------------------------------------------

project = 'atmospy'
import time
copyright = '2021-{}, QuantAQ, Inc.'.format(time.strftime("%Y"))
author = 'QuantAQ'

# The full version, including alpha/beta/rc tags
sys.path.insert(0, os.path.abspath(os.path.pardir))
import atmospy
release = atmospy.__version__
version = atmospy.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'matplotlib.sphinxext.plot_directive',
    'numpydoc',
    'sphinx_issues'
]

issues_github_path = "quant-aq/atmospy"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autosummary_generate = True
numpydoc_show_class_members = False

plot_include_source = True
plot_formats = [("png", 90)]
plot_html_show_formats = False
plot_html_show_source_link = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'bootstrap'

html_theme_options = {
    'source_link_position': 'footer',
    'bootswatch_theme': "paper",
    "navbar_title": " ",
    'navbar_sidebarrel': False,
    'bootstrap_version': "3",
    'nosidebar': True,
    'body_max_width': "100%",
    'navbar_links': [
        ("Gallery", "examples/index"),
        ("Tutorial", "tutorial"),
        ("API", "api")
    ],
}

html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']