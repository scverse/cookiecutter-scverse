# Developer documentation

Welcome to the developer guidelines! This document is split into two parts:

-   A section about the repository setup. It describes how the build system and automated checks work
-   A contributor guide. It contains all information relevant to developers who want to make a contribution.

## Repository set-up

### Documentation on _readthedocs_

-   make sure to enable PR builds

### Tutorials with _nbsphinx_

### Coverage tests with _Codecov_

To enable coverage checks, head over to [codecov][] and the "getting started" instructions on the [codecov setup][].
You can directly login with your GitHub account to Codecov.

In short, you need to:

1. Go to the _Settings_ of your newly created repository on github.
2. Go to _Security > Secrets > Actions_.
3. Create new repository secret with Name **CODECOV_TOKEN** and Value alphanumeric sequence.
4. Go back to Github Actions page an re-run previously failed jobs.

### Pre-commit checks

[Pre-commit](https://pre-commit.com/) checks are fast programs that
check code for errors, inconsistencies and code styles, before the code
is committed. This is a brief documentation of pre-commits checks
pre-sets in the scverse-template.

The following pre-commit checks for code style and format.

-   [black](https://black.readthedocs.io/en/stable/): standard code
    formatter in Python.
-   [autopep8](https://github.com/hhatto/autopep8): code formatter to
    conform to [PEP8](https://peps.python.org/pep-0008/) style guide.
-   [isort](https://pycqa.github.io/isort/): sort module imports into
    sections and types.
-   [prettier](https://prettier.io/docs/en/index.html): standard code
    formatter for non-Python files (e.g. YAML).
-   [blacken-docs](https://github.com/asottile/blacken-docs): black on
    python code in docs.

The following pre-commit checks for errors, inconsistencies and typing.

-   [flake8](https://flake8.pycqa.org/en/latest/): standard check for errors in Python files.
    -   [flake8-tidy-imports](https://github.com/adamchainz/flake8-tidy-imports):
        tidy module imports.
    -   [flake8-docstrings](https://github.com/PyCQA/flake8-docstrings):
        pydocstyle extension of flake8.
    -   [flake8-rst-docstrings](https://github.com/peterjc/e8-rst-docstrings):
        extension of `flake8-docstrings` for `rst` docs.
    -   [flake8-comprehensions](https://github.com/adamchainz/e8-comprehensions):
        write better list/set/dict comprehensions.
    -   [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear):
        find possible bugs and design issues in program.
    -   [flake8-blind-except](https://github.com/elijahandrews/flake8-blind-except):
        checks for blind, catch-all `except` statements.
-   [yesqa](https://github.com/asottile/yesqa):
    remove unneccesary `# noqa` comments, follows additional dependencies listed above.
-   [autoflake](https://github.com/PyCQA/autoflake):
    remove unused imports and variables.
-   [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks): generic pre-commit hooks.
    -   **detect-private-key**: checks for the existence of private keys.
    -   **check-ast**: check whether files parse as valid python.
    -   **end-of-file-fixer**:check files end in a newline and only a newline.
    -   **mixed-line-ending**: checks mixed line ending.
    -   **trailing-whitespace**: trims trailing whitespace.
    -   **check-case-conflict**: check files that would conflict with case-insensitive file systems.
-   [pyupgrade](https://github.com/asottile/pyupgrade):
    upgrade syntax for newer versions of the language.

#### Notes on pre-commit checks

-   **flake8**: to ignore errors, you can add a comment `# noqa` to the offending line.
    You can also specify the error id to ignore with e.g. `# noqa: E731`.
    Check [flake8 guide](https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html) for reference.
-   You can add or remove pre-commit checks by simply deleting relevant lines in the `.pre-commit-config.yaml` file.
    Some pre-commit checks have additional options that can be specified either in the `pyproject.toml` or pre-commit
    specific config files, such as `.prettierrc.yml` for **prettier** and `.flake8` for **flake8**.

### Customize linting

### Template sync with _cookietemple_

TODO

## Contributing guide

Scanpy provides extensive [developer documentation][scanpy developer guide], most of which applies to this repo, too.
This document will not reproduce the entire content from there. Instead, it aims at summarizing the most important
information to get you started on contributing.

### Getting set-up

We assume that you are already familiar with git and with making pull requests on GitHub. If not, please refer
to the [scanpy developer guide][].

### Making a release

<!-- Links -->

[scanpy developer guide]: https://scanpy.readthedocs.io/en/latest/dev/index.html
[codecov]: https://about.codecov.io/
[codecov setup]: https://docs.codecov.com/docs
