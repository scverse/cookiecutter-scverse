pre-commit documentation
========================

`Pre-commit`_ checks are fast programs that check code for errors, inconsistencies and code styles, before the code is committed.
This is a brief documentation of pre-commits checks pre-sets in the scverse-template.

The following pre-commit checks for code style and format.

* black_: standard code formatter in Python.
* autopep8_: code formatter to conform to `PEP8`_ style guide.
* isort_: sort module imports into sections and types.
* prettier_: standard code formatter for non-Python files (e.g. YAML).
* blacken-docs_: black on python code in docs.

The following pre-commit checks for errors, inconsistencies and typing.

* flake8_: standard check for errors in Python files.
   * flake8-tidy-imports_: tidy module imports.
   * flake8-docstrings_: pydocstyle extension of flake8.
   * flake8-rst-docstrings_: extension of ``flake8-docstrings`` for ``rst`` docs.
   * flake8-comprehensions_: write better list/set/dict comprehensions.
   * flake8-bugbear_: find possible bugs and design issues in program.
   * flake8-blind-except_: checks for blind, catch-all ``except`` statements.
* yesqa_: remove unneccesary ``# noqa`` comments, follows additional dependencies listed above.
* autoflake_: remove unused imports and variables.
* pre-commit-hooks_: generic pre-commit hooks.
   * **detect-private-key**: checks for the existence of private keys.
   * **check-ast**: check whether files parse as valid python.
   * **check-added-large-files**: prevent giant files from being committed. accept ipynbs.
   * **end-of-file-fixer**:check files end in a newline and only a newline.
   * **mixed-line-ending**: checks mixed line ending.
   * **trailing-whitespace**: trims trailing whitespace.
   * **check-case-conflict**: check files that would conflict with case-insensitive file systems.
* pyupgrade_: upgrade syntax for newer versions of the language.

.. _pre-commit: https://pre-commit.com/
.. _mypy: http://www.mypy-lang.org/
.. _black: https://black.readthedocs.io/en/stable/
.. _autopep8: https://github.com/hhatto/autopep8
.. _pep8: https://peps.python.org/pep-0008/
.. _isort: https://pycqa.github.io/isort/
.. _prettier: https://prettier.io/docs/en/index.html
.. _blacken-docs: https://github.com/asottile/blacken-docs
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _flake8-tidy-imports: https://github.com/adamchainz/flake8-tidy-imports
.. _flake8-docstrings: https://github.com/PyCQA/flake8-docstrings
.. _flake8-rst-docstrings: https://github.com/peterjc/flake8-rst-docstrings
.. _flake8-comprehensions: https://github.com/adamchainz/flake8-comprehensions
.. _flake8-bugbear: https://github.com/PyCQA/flake8-bugbear
.. _flake8-blind-except: https://github.com/elijahandrews/flake8-blind-except
.. _yesqa: https://github.com/asottile/yesqa
.. _pre-commit-hooks: https://github.com/pre-commit/pre-commit-hooks
.. _autoflake: https://github.com/PyCQA/autoflake
.. _pyupgrade: https://github.com/asottile/pyupgrade
