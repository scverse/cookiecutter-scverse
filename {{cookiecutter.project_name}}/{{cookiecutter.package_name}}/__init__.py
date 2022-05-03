from importlib.metadata import version

from . import pp, tl, pl

__all__ = ["pp", "tl", "pl"]

__version__ = version("{{ cookiecutter.project_name }}")
