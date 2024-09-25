# {{ cookiecutter.project_name }}

[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}/test.yaml?branch=main
[badge-docs]: https://img.shields.io/readthedocs/{{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Getting started

Please refer to the [documentation][]. In particular, the [API documentation][].

## Installation

You need to have Python 3.10 or newer installed on your system. If you don't have
Python installed, we recommend installing [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge).

There are several alternative options to install {{ cookiecutter.project_name }}:

<!--
1) Install the latest release of `{{ cookiecutter.project_name }}` from [PyPI][]:

```bash
pip install {{ cookiecutter.project_name }}
```
-->

1. Install the latest development version:

```bash
pip install git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}.git@main
```

## Release notes

See the [changelog][].

## Contact

For questions and help requests, you can reach out in the [scverse discourse][].
If you found a bug, please use the [issue tracker][].

## Citation

> t.b.a

[scverse discourse]: https://discourse.scverse.org/
[issue tracker]: https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}/issues
[tests]: https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.github_repo }}/actions/workflows/test.yml
[documentation]: https://{{ cookiecutter.project_name }}.readthedocs.io
[changelog]: https://{{ cookiecutter.project_name }}.readthedocs.io/en/latest/changelog.html
[api documentation]: https://{{ cookiecutter.project_name }}.readthedocs.io/en/latest/api.html
[pypi]: https://pypi.org/project/{{ cookiecutter.project_name }}
