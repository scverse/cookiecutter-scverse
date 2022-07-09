# Scverse Cookiecutter Template

TODO: badges

The purpose of this template is to get you started quickly building a best-practice python library for a [scverse][] ecosystem package.
Ecosystem packages are independent software libraries that interact with scverse core packages and depend on [anndata][] and [mudata][] data structures.

TODO: link to instance repo

## Features

-   continuous integration using GitHub actions.
-   [pre-commit][] checks
-   tutorials built with [nbsphinx][]
-   documentation hosted by [readthedocs][]
-   [flit][] as build system
-   issue templates
-   [bump2version][]

TODO complete list and explain what the features are doing

## Getting started

In this section we will show you how to set-up your own repository from this template
and how to customize it for your needs.

### Install dependencies

You need `git >=2.38` and `python >=3.8`. In addition you need to install the following Python dependencies:

```bash
pip install cookiecutter pre-commit
```

### Create the project

Now create the project and follow the prompts:

```bash
cookiecutter https://github.com/scverse/cookiecutter-scverse
```

This will create a git repository with a filed out template in it.
Now `cd` into the newly created directory and make the initial commit!
Don't forget to create a repository on GitHub and upload your project.

### Set up online services

Your repository is now ready. However, to use all features of the template you will need to set up the following
online services. Clicking on the links will take you to the respective sections of the developer documentation.
The developer documentation is also shipped as part of the template in `docs/developer_docs.md`.

1.  [pre-commit.ci][setup-pre-commit] to check for inconsistencies and to enforce a code style
2.  [readthedocs.org][setup-rtd] to build and host documentation
3.  [codecov][setup-codecov] to generate test coverage reports

### Write tests

TODO

All CI checks should pass, you are ready to start developing your new tool!

### Customizations

Further instructions on using this template can be found in the contributing guide included in the project.

### Committment

We expect developers of ecosystem packages to

-   write unit tests
-   provide documentation, including tutorials where applicable
-   support users through github and the [scverse discourse][]

<!-- links -->

[flit]: https://flit.pypa.io/en/latest/
[readthedocs]: https://readthedocs.org/
[nbsphinx]: https://github.com/spatialaudio/nbsphinx
[pre-commit]: https://pre-commit.com/
[bump2version]: https://github.com/c4urself/bump2version/
[scverse]: https://scverse.org/
[anndata]: https://anndata.readthedocs.io/en/latest/
[mudata]: https://muon.readthedocs.io/en/latest/notebooks/quickstart_mudata.html
[codecov]: https://about.codecov.io/
[scverse discourse]: https://discourse.scverse.org/
