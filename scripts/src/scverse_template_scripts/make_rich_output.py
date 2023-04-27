from rich.console import Console
from rich.markdown import Markdown

dev_docs_url = "https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html"

message = f"""\
# Set-up online services

**Your repository is now ready.
However, to use all features of the template you will need to set up the following online services.**
Clicking on the links will take you to the respective sections of the developer documentation.
The developer documentation is also shipped as part of the template in docs/developer_docs.md.

1.  [pre-commit.ci][setup-pre-commit] to check for inconsistencies and to enforce a code style
2.  [readthedocs.org][setup-rtd] to build and host documentation
3.  [codecov][setup-codecov] to generate test coverage reports

All CI checks should pass, you are ready to start developing your new tool!

# Install the package

To run tests or build the documentation locally, you need to install your package and its dependencies.
You can do so with

```bash
pip install ".[test,dev,doc]"
```

# Customizations

Further instructions on using this template can be found in the [dev docs included in the project][dev-docs].

# Committment

We expect developers of scverse ecosystem packages to

-   [write unit tests][write-tests]
-   [provide documentation][write-docs], including tutorials where applicable
-   support users through github and the [scverse discourse][]

[dev-docs]: {dev_docs_url}
[setup-pre-commit]: {dev_docs_url}#pre-commit-checks
[setup-rtd]: {dev_docs_url}#documentation-on-readthedocs
[setup-codecov]: {dev_docs_url}#coverage-tests-with-codecov
[write-tests]: {dev_docs_url}#writing-tests
[write-docs]: {dev_docs_url}#writing-documentation
[scverse discourse]: https://discourse.scverse.org/
"""


def main() -> None:
    with open("report.txt", "w") as report_file:
        console = Console(
            file=report_file,
            width=72,
            force_terminal=True,
            color_system="standard",
        )
        console.print(Markdown(message))


if __name__ == "__main__":
    main()
