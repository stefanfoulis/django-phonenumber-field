# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import pathlib
import sys

current_dir = pathlib.Path(__file__).parent
# Find current settings module for doctests.
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "ext"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "django-phonenumber-field"
copyright = "2022, django-phonenumber-field"
author = "Stefan Foulis"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "phonenumber_field_docs",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = []

# -- Options for extensions --------------------------------------------------

intersphinx_mapping = {
    "django": (
        "https://docs.djangoproject.com/en/dev/",
        "https://docs.djangoproject.com/en/dev/_objects/",
    ),
    "python": ("https://docs.python.org/3/", None),
}
