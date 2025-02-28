# Scverse Cookiecutter Template

[![Test][badge-test]][link-test]
[![Powered by NumFOCUS][badge-numfocus]][link-numfocus]

The purpose of this template is to get you started quickly building a best-practice python library for a [scverse][] ecosystem package.
Ecosystem packages are independent software libraries that interact with scverse core packages and depend on [anndata][] and [mudata][] data structures.

Please check out the

- [example repo](https://github.com/scverse/cookiecutter-scverse-instance) and the
- [example documentation](https://cookiecutter-scverse-instance.readthedocs.io/en/latest/)

that are automatically generated and kept in sync with this template.

[//]: # "numfocus-fiscal-sponsor-attribution"

This template is part of the scverse® project ([website](https://scverse.org), [governance](https://scverse.org/about/roles)) and is fiscally sponsored by [NumFOCUS](https://numfocus.org/).
Please consider making a tax-deductible [donation](https://numfocus.org/donate-to-scverse) to help the project pay for developer time, professional services, travel, workshops, and a variety of other needs.

<a href="https://numfocus.org/project/scverse">
  <img
    src="https://raw.githubusercontent.com/numfocus/templates/master/images/numfocus-logo.png"
    width="200"
  >
</a>

[badge-test]: https://github.com/scverse/cookiecutter-scverse/actions/workflows/test.yaml/badge.svg
[link-test]: https://github.com/scverse/cookiecutter-scverse/actions/workflows/test.yaml
[badge-numfocus]: https://img.shields.io/badge/powered%20by-NumFOCUS-orange.svg?style=flat&colorA=E1523D&colorB=007D8A
[link-numfocus]: http://numfocus.org

## Features

- automated testing with [pytest][]
- continuous integration using GitHub actions.
- documentation hosted by [readthedocs][]
- coverage tests with [codecov][]
- [pre-commit][] checks for code style and consistency
- tutorials with [myst-nb][] and jupyter notebooks
- issue templates for better bug reports and feature requests
- [bump2version][] for managing releases

## Getting started

In this section we will show you how to set-up your own repository from this template
and how to customize it for your needs.

### Install dependencies

You need `git >=2.28` and `python >=3.10`. In addition you need to install the following Python dependencies:

```bash
pip install cruft pre-commit
```

### Create the project

We are using [cruft](https://github.com/cruft/cruft) to initialize the project from the template. Cruft
is fully compatible with [cookiecutter](https://github.com/cookiecutter/cookiecutter), but enables automatic
updates to your project whenever a new template version is released.

To create the project, run the following command and follow the prompts:

```bash
cruft create https://github.com/scverse/cookiecutter-scverse
```

This will create a git repository generated from the template.
Now `cd` into the newly created directory and make the initial commit!
Don't forget to create a repository on GitHub and upload your project.

### Set up online services

Your repository is now ready. However, to use all features of the template you will need to set up the following
online services. Clicking on the links will take you to the respective sections of the developer documentation.
The developer documentation is also shipped as part of the template in `docs/template_usage.md`.

1.  [pre-commit.ci][setup-pre-commit] to check for inconsistencies and to enforce a code style
2.  [readthedocs.org][setup-rtd] to build and host documentation
3.  [codecov][setup-codecov] to generate test coverage reports

All CI checks should pass, you are ready to start developing your new tool!

### Customizations

Further instructions on using this template can be found in the [dev docs included in the project](https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html).

### Committment

We expect developers of scverse ecosystem packages to

- [write unit tests][write-tests]
- [provide documentation][write-docs], including tutorials where applicable
- support users through github and the [scverse discourse][]

## Changelog

See the [release page][].

## Releasing a new template version

To release a new version of the template, create a new release on the GitHub [release page][].
Choose a tag name of the format `vX.X.X` that adheres to [semantic versioning](https://semver.org/).

Note that when creating a new release, changes will be propagated to packages using this template.

## Citation

You can cite the scverse publication as follows:

> **The scverse project provides a computational ecosystem for single-cell omics data analysis**
>
> Isaac Virshup, Danila Bredikhin, Lukas Heumos, Giovanni Palla, Gregor Sturm, Adam Gayoso, Ilia Kats, Mikaela Koutrouli, Scverse Community, Bonnie Berger, Dana Pe’er, Aviv Regev, Sarah A. Teichmann, Francesca Finotello, F. Alexander Wolf, Nir Yosef, Oliver Stegle & Fabian J. Theis
>
> _Nat Biotechnol._ 2022 Apr 10. doi: [10.1038/s41587-023-01733-8](https://doi.org/10.1038/s41587-023-01733-8).

<!-- links -->

[setup-pre-commit]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html#pre-commit-checks
[setup-rtd]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html#documentation-on-readthedocs
[setup-codecov]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html#coverage-tests-with-codecov
[write-tests]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html#writing-tests
[write-docs]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html#writing-documentation
[readthedocs]: https://readthedocs.org/
[myst-nb]: https://myst-nb.readthedocs.io/
[pre-commit]: https://pre-commit.com/
[bump2version]: https://github.com/c4urself/bump2version/
[scverse]: https://scverse.org/
[anndata]: https://anndata.readthedocs.io/en/latest/
[mudata]: https://muon.readthedocs.io/en/latest/notebooks/quickstart_mudata.html
[codecov]: https://about.codecov.io/
[scverse discourse]: https://discourse.scverse.org/
[pytest]: https://docs.pytest.org
[release page]: https://github.com/scverse/cookiecutter-scverse/releases
