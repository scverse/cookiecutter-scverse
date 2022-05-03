from importlib.metadata import version

from . import pl, pp, tl  # noqa: F401

__version__ = version("{{ cookiecutter.project_name }}")
