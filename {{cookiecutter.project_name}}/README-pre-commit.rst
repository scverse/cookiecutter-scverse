pre-commit documentation
========================

`Pre-commit`_ checks are fast programs that check code for errors, inconsistencies and code styles, before the code is committed.
This is a brief documentation of pre-commits checks pre-sets in the scverse-template.

The following pre-commit checks for code style and format.

* `black`_: standard code formatter in Python.
* `autopep8`_: code formatter to conform to `PEP8`_ style guide.
* `isort`_: sort module imports into sections and types.
* `rstcheck`_: check syntax of reStructuredText.
* `blacken-docs`_: black on python code in docs.

The following pre-commit checks for errors, inconsistencies and typing.

* `flake8`_: standard check for errors in Python files.
   * `flake8-tidy-imports`_: tidy module imports.
   * `flake8-docstrings`_: pydocstyle extension of flake8.
   * `flake8-rst-docstrings`_: extension of ``flake8-docstrings`` for ``rst`` docs.
   * `flake8-comprehensions`_: write better list/set/dict comprehensions.
   * `flake8-bugbear`_: find possible bugs and design issues in program.
   * `flake8-blind-except`_: checks for blind, catch-all ``except`` statements.
   * `flake8-builtins`_: check for python builtins being used as variables or parameters.
   * `flake8-pytest-style`_: check common style/inconsistency issues with pytest-based tests.
   * `flake8-string-format`_: check strings and parameters using ``str.format``.
* `yesqa`_: remove unneccesary ``# noqa`` comments.
* `pyupgrade`: upgrade syntax for newer versions of the language.
* `pre-commit-hooks`_: generic pre-commit hooks.
* `autoflake`_: remove unused imports and variables.*

* `mypy`_: static type checker for Python.
   * silence errors add ``# ignore`` or ``# noqa[<error_id>]`` next to the offending line.
   * To silence errors add ``# noqa`` or ``# noqa[<error_id>]`` next to the offending line.

.. _pre-commit: https://pre-commit.com/
.. _mypy: http://www.mypy-lang.org/
.. _black: https://black.readthedocs.io/en/stable/
.. _autopep8: https://github.com/hhatto/autopep8
.. _pep8: https://peps.python.org/pep-0008/
.. _isort: https://pycqa.github.io/isort/
.. _pretty-format-yaml: https://github.com/macisamuele/language-formatters-pre-commit-hooks
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _flake8-tidy-imports: https://github.com/adamchainz/flake8-tidy-imports
.. _flake8-docstrings: https://github.com/PyCQA/flake8-docstrings
.. _flake8-rst-docstrings: https://github.com/peterjc/flake8-rst-docstrings
.. _flake8-comprehensions: https://github.com/adamchainz/flake8-comprehensions
.. _flake8-bugbear: https://github.com/PyCQA/flake8-bugbear
.. _flake8-blind-except: https://github.com/elijahandrews/flake8-blind-except
.. _flake8-builtins: https://github.com/gforcada/flake8-builtins
.. _flake8-pytest-style: https://pypi.org/project/flake8-pytest-style/
.. _flake8-string-format: https://pypi.org/project/flake8-string-format/

.. _yesqa: https://github.com/asottile/yesqa
.. _pre-commit-hooks: https://github.com/pre-commit/pre-commit-hooks
.. _autoflake: https://github.com/PyCQA/autoflake
.. _rstcheck: https://github.com/myint/rstcheck
.. _blacken-docs: https://github.com/asottile/blacken-docs
.. _doc8: https://github.com/PyCQA/doc8
