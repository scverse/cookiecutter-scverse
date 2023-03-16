# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from rich.console import Console
from rich.markdown import Markdown

# %% [markdown]
# Set up online services
#
# Your repository is now ready. However, to use all features of the template you will need to set up the following online services. Clicking on the links will take you to the respective sections of the developer documentation. The developer documentation is also shipped as part of the template in docs/developer_docs.md.
#
#     pre-commit.ci to check for inconsistencies and to enforce a code style
#     readthedocs.org to build and host documentation
#     codecov to generate test coverage reports
#
# All CI checks should pass, you are ready to start developing your new tool!
# Customizations
#
# Further instructions on using this template can be found in the dev docs included in the project.
# Committment
#
# We expect developers of scverse ecosystem packages to
#
#     write unit tests
#     provide documentation, including tutorials where applicable
#     support users through github and the scverse discourse
#

# %%
with open("/home/sturm/Downloads/report.txt", "wt") as report_file:
    console = Console(file=report_file, width=72, force_terminal=True, color_system="standard", )
    console.print(
        Markdown(
            """
# Set-up online services

**Your repository is now ready. However, to use all features of the template you will need to set up the following online services.**
Clicking on the links will take you to the respective sections of the developer documentation.
The developer documentation is also shipped as part of the template in docs/developer_docs.md.

1.  [pre-commit.ci][setup-pre-commit] to check for inconsistencies and to enforce a code style
2.  [readthedocs.org][setup-rtd] to build and host documentation
3.  [codecov][setup-codecov] to generate test coverage reports

All CI checks should pass, you are ready to start developing your new tool!

# Install the package

To run tests or build the documentation locally, you need to install your package and its dependencies. You can do so with

```bash
pip install ".[test,dev,doc]"
```

# Customizations

Further instructions on using this template can be found in the [dev docs included in the project](https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html).

# Committment

We expect developers of scverse ecosystem packages to

-   [write unit tests][write-tests]
-   [provide documentation][write-docs], including tutorials where applicable
-   support users through github and the [scverse discourse][]

[setup-pre-commit]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#pre-commit-checks
[setup-rtd]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#documentation-on-readthedocs
[setup-codecov]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#coverage-tests-with-codecov
[write-tests]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#writing-tests
[write-docs]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#writing-documentation
[scverse discourse]: https://discourse.scverse.org/

"""
        )
    )

# %%

# %%
