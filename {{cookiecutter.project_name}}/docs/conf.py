# Configuration file for the Sphinx documentation builder.
# `scverse_doc` sets the theme and shared defaults, see https://scverse-doc.readthedocs.io
# For the full list of options, see https://www.sphinx-doc.org/page/usage/configuration.html

import re
from datetime import datetime
from importlib.metadata import metadata

from scverse_doc.config import DEFAULTS

# NOTE: If you installed your project in editable mode, this might be stale.
#       If this is the case, reinstall it to refresh the metadata
info = metadata("{{cookiecutter.project_name}}")
project = info["Name"]
author = info["Author"]
copyright = f"{datetime.now():%Y}, {author}."
version = release = info["Version"]
urls = dict(pu.split(", ") for pu in info.get_all("Project-URL"))
source_repository = urls["Source"]
requires_python = info["Requires-Python"]
min_python = m[1] if (m := re.fullmatch(r">=\s*([\d.]+)", requires_python)) else None

extensions = [
    "scverse_doc",
    "scverse_misc.sphinx_ext",
    "sphinxcontrib.bibtex",
    "sphinx_autodoc_typehints",
    "IPython.sphinxext.ipython_console_highlighting",
]

myst_enable_extensions = [*DEFAULTS.myst_enable_extensions, "substitution"]
myst_substitutions = {
    # used in installation.md, so the stated Python requirement follows `requires-python` in pyproject.toml
    "python_requirement": f"Python {min_python} or newer" if min_python else f"Python {requires_python}",
}

bibtex_bibfiles = ["references.bib"]
typehints_defaults = "braces"
always_use_bars_union = True  # use `|` instead of `Union` in types even when building with Python ≤3.14

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

xref_overrides = {
    # If building the documentation fails because a type annotation links to a private path
    # (e.g. `igraph._igraph.GraphBase`), map it to the documented name here.
    # For a missing link that can’t be fixed this way, add it to `nitpick_ignore` instead.
    #     "igraph._igraph.GraphBase": "igraph.GraphBase",
}
