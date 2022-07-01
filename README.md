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

You need `git >=2.38` and `python >=3.8`. In addition you need to install the following python dependencies:

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

Further instructions on using this template can be found in the contributing guide included in the project. Build the docs by installing a development version of the package and running sphinx:

TODO: link to instance repo

```
pip install -e ".[dev,doc,test]"
cd docs
make html
open _build/html/index.html
```

### Codecov set up

Once the newly generated repository has been pushed to github, there is one last thing to do: set up code coverage with **codecov**.
To do this, head over to [codecov][] and the "getting started" instructions on the [codecov setup docs][]. You can directly login with your github account to codecov.

In short, you need to:

1. Go to the _Settings_ of your newly created repository on github.
2. Go to _Security > Secrets > Actions_.
3. Create new repository secret with Name **CODECOV_TOKEN** and Value alphanumeric sequence.
4. Go back to Github Actions page an re-run previously failed jobs.

All CI checks should pass, you are ready to start developing your new tool!

[flit]: https://flit.pypa.io/en/latest/
[readthedocs]: https://readthedocs.org/
[nbsphinx]: https://github.com/spatialaudio/nbsphinx
[pre-commit]: https://pre-commit.com/
[bump2version]: https://github.com/c4urself/bump2version/
[scverse]: https://scverse.org/
[anndata]: https://anndata.readthedocs.io/en/latest/
[mudata]: https://muon.readthedocs.io/en/latest/notebooks/quickstart_mudata.html
[codecov]: https://about.codecov.io/
[codecov setup]: https://docs.codecov.com/docs

TODO

-   API explanation
-   Requirements:

    -   We strongly encourage you to
        -   write tests
        -   adapt an scverse-like api (although other apis may make sense)
        -   embrace semantic versioning

-   Setting up RTD

    -   make sure to check PR builds

-   tutorials

    -   This repository is currently set-up for including jupyter notebooks in ipynb format _including outputs_.
        We are thinking about adding CI builds for tutorials in the future, but this can be challenging depending on the resource requiresments to build the tutorials. See the discussion at <> if you are interested in this feature.

-   installing the package with hatch
-   versioning

    -   by default, this package is set-up to use `hatch`'s bump version. You may switch to vcs-based versioning using
        the hatch-vcs pluging if you prefer.

-   template sync

    -   We use cookietemple to keep your package in sync with the template. A bot will make a pull request to your repository if we update the template. Like that you may benefit from new features or if we fix the build system.

-   Planned features

    -   centralized logging

-   customize linting
-   how to add tests

Take inspirations from the scanpy, scvi and muon developer guides!

TODO: write developer guide first, then docs of the template!
