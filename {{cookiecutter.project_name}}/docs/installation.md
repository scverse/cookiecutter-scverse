# Installation

{{ cookiecutter.project_name }} needs Python 3.12 or newer.
We recommend [uv][], which installs Python for you and keeps each project's dependencies in their own virtual environment.

<!--
## PyPI

Install the latest release from [PyPI][]:

:::::{tab-set}
::::{tab-item} uv
:sync: uv

```bash
uv add {{ cookiecutter.project_name }}
```

::::

::::{tab-item} Pip
:sync: pip

```bash
pip install {{ cookiecutter.project_name }}
```

::::
:::::

-->

## Development version

Install the latest development version from GitHub:

:::::{tab-set}
::::{tab-item} uv
:sync: uv

```bash
uv add git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}.git
```

::::

::::{tab-item} Pip
:sync: pip

```bash
pip install git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}.git
```

::::
:::::

To work on {{ cookiecutter.project_name }} itself, see {doc}`contributing`.

[uv]: https://docs.astral.sh/uv/
[pypi]: https://pypi.org/project/{{ cookiecutter.project_name }}
