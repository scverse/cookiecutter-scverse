# Scverse Cookiecutter Template

The purpose of this template is to get you started quickly building a best-practice python library for a [scverse][] ecosystem package.
Ecosystem packages are independent software libraries that interact with scverse core packages and depend on [anndata][] and [mudata][] data structures.

## Features

-   continuous integration using GitHub actions.
-   [pre-commit][] checks
-   tutorials built with [nbsphinx][]
-   documentation hosted by [readthedocs][]
-   [flit][] as build system
-   [bump2version][]

## Usage

```bash
cookiecutter
```

[flit]: https://flit.pypa.io/en/latest/
[readthedocs]: https://readthedocs.org/
[nbsphinx]: https://github.com/spatialaudio/nbsphinx
[pre-commit]: https://pre-commit.com/
[bump2version]: https://github.com/c4urself/bump2version/
[scverse]: https://scverse.org/
[anndata]: https://anndata.readthedocs.io/en/latest/
[mudata]: https://muon.readthedocs.io/en/latest/notebooks/quickstart_mudata.html
