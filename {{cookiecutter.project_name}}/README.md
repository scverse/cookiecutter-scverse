# {{ cookiecutter.project_name }}

[![Tests][badge-tests]][link-tests]
[![Documentation][badge-docs]][link-docs]

[badge-tests]: https://img.shields.io/github/workflow/status/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}/Test/main
[link-tests]: {{ cookiecutter.project_repo }}/actions/workflows/test.yml
[badge-docs]: https://img.shields.io/readthedocs/{{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Getting started

Please refer to the [documentation][link-docs]. In particular, the

-   [API documentation][link-api].

## Installation

You need to have Python 3.8 or newer installed on your system. If you don't have
Python installed, we recommend installing `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`\_.

There are several alternative options to install {{ cookiecutter.project_name }}:

<!--
1) Install the latest release of `{{ cookiecutter.project_name }}` from `PyPI <https://pypi.org/project/{{ cookiecutter.project_name }}/>`_:

```bash
pip install {{ cookiecutter.project_name }}
```
-->

1. Install the latest development version:

```bash
pip install git+https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}.git@main
```

## Release notes

See the [changelog][changelog].

## Contact

For questions and help requests, you can reach out in the [scverse discourse][scverse-discourse].
If you found a bug, please use the [issue tracker][issue-tracker].

## Citation

> t.b.a

[scverse-discourse]: https://discourse.scverse.org/

[issue-tracker]: https://github.com/{{ cookiecutter.github_user }}/{{ cookiecutter.project_name }}/issues
[changelog]: https://{{ cookiecutter.project_name }}.readthedocs.io/latest/changelog.html
[link-docs]: https://{{ cookiecutter.project_name }}.readthedocs.io
[link-api]: https://{{ cookiecutter.project_name }}.readthedocs.io/latest/api.html
