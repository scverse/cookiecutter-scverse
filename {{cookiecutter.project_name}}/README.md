# {{ cookiecutter.project_name }}

[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}/test.yaml?branch=main
[badge-docs]: https://app.readthedocs.org/projects/{{ cookiecutter.project_name }}/badge/

{{ cookiecutter.project_description }}

## Getting started

Please refer to the [documentation][],
in particular, the [API documentation][].

## Installation

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

1. Install the latest development version

   ```bash
   # (or `uv add`)
   pip install git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}.git
   ```

## Release notes

See the [changelog][].

## Contact

For questions and help requests, you can reach out in the [scverse discourse][].
If you found a bug, please use the [issue tracker][].

## Citation

> t.b.a

[uv]: https://github.com/astral-sh/uv
[scverse discourse]: https://discourse.scverse.org/
[issue tracker]: https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}/issues
[tests]: https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}/actions/workflows/test.yaml
[documentation]: https://{{ cookiecutter.project_name }}.readthedocs.io
[changelog]: https://{{ cookiecutter.project_name }}.readthedocs.io/page/changelog.html
[api documentation]: https://{{ cookiecutter.project_name }}.readthedocs.io/page/api.html
[pypi]: https://pypi.org/project/{{ cookiecutter.project_name }}
[venv]: https://docs.python.org/3/tutorial/venv.html
