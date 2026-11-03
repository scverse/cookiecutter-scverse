# Installation

You need to have Python 3.12 or newer installed on your system.
If you don't have Python installed, we recommend installing [uv][].

We recommend managing dependencies in project-specific virtual environments to avoid dependency conflicts.
This is most convenient using package managers such as [uv][].
Choose from the options below to install {{ cookiecutter.project_name }}:

<!--
1. Add the latest release of `{{ cookiecutter.project_name }}` from [PyPI][] to your `uv` project:

   ```bash
   uv add {{ cookiecutter.project_name }}
   ```

1. Install the latest release into a [standard virtual environment][venv]:

   ```bash
   (after activating your venv)
   pip install {{ cookiecutter.project_name }}
   ```

-->

1. Install the latest development version:

   ```bash
   pip install git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}.git  # (or `uv add`)
   ```

To work on {{ cookiecutter.project_name }} itself, see {doc}`contributing`.

[uv]: https://github.com/astral-sh/uv
[pypi]: https://pypi.org/project/{{ cookiecutter.project_name }}
[venv]: https://docs.python.org/3/tutorial/venv.html
