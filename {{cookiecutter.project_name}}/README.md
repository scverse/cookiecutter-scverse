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

<!-- TODO  - replace dev version with PyPI version once released

```bash
uv add {{ cookiecutter.project_name }}
```

-->

```bash
uv add git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}.git
```

For more info about prerequisites, and alternative ways to install `{{ cookiecutter.project_name }}`,
see the [installation][] section in the docs.

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
[installation]: https://{{ cookiecutter.project_name }}.readthedocs.io/page/installation.html
[changelog]: https://{{ cookiecutter.project_name }}.readthedocs.io/page/changelog.html
[api documentation]: https://{{ cookiecutter.project_name }}.readthedocs.io/page/api.html
[pypi]: https://pypi.org/project/{{ cookiecutter.project_name }}
[venv]: https://docs.python.org/3/tutorial/venv.html
