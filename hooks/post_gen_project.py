#!/bin/env python
from subprocess import run

# Update pre commit hooks
run("pre-commit autoupdate -c .pre-commit-config.yaml".split(), check=True)
run("pre-commit install".split(), check=True)

# The following output was generated using rich
# The formatted output is included here directly, because I don't want
# rich as another dependency for initalizing the repo.
# See .make_rich_output.py for more details.
print("""




╔══════════════════════════════════════════════════════════════════════╗
║                        [1mSet-up online services[0m                        ║
╚══════════════════════════════════════════════════════════════════════╝

[1mYour repository is now ready. However, to use all features of the [0m
[1mtemplate you will need to set up the following online services.[0m Clicking
on the links will take you to the respective sections of the developer
documentation. The developer documentation is also shipped as part of
the template in docs/developer_docs.md.

[1;33m 1 [0m]8;id=633754;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#pre-commit-checks\[94mpre-commit.ci[0m]8;;\ to check for inconsistencies and to enforce a code
[1;33m   [0mstyle
[1;33m 2 [0m]8;id=858259;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#documentation-on-readthedocs\[94mreadthedocs.org[0m]8;;\ to build and host documentation
[1;33m 3 [0m]8;id=497293;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#coverage-tests-with-codecov\[94mcodecov[0m]8;;\ to generate test coverage reports

All CI checks should pass, you are ready to start developing your new
tool!

╔══════════════════════════════════════════════════════════════════════╗
║                         [1mInstall the package[0m                          ║
╚══════════════════════════════════════════════════════════════════════╝

To run tests or build the documentation locally, you need to install
your package and its dependencies. You can do so with

[97;40mpip[0m[97;40m [0m[97;40minstall[0m[97;40m [0m[93;40m".[test,dev,doc]"[0m[40m                                           [0m

╔══════════════════════════════════════════════════════════════════════╗
║                            [1mCustomizations[0m                            ║
╚══════════════════════════════════════════════════════════════════════╝

Further instructions on using this template can be found in the ]8;id=447180;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html\[94mdev docs[0m]8;;\
]8;id=447180;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html\[94mincluded in the project[0m]8;;\.

╔══════════════════════════════════════════════════════════════════════╗
║                             [1mCommittment[0m                              ║
╚══════════════════════════════════════════════════════════════════════╝

We expect developers of scverse ecosystem packages to

[1;33m • [0m]8;id=169559;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#writing-tests\[94mwrite unit tests[0m]8;;\
[1;33m • [0m]8;id=20647;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#writing-documentation\[94mprovide documentation[0m]8;;\, including tutorials where applicable
[1;33m • [0msupport users through github and the ]8;id=496112;https://discourse.scverse.org/\[94mscverse discourse[0m]8;;\

""")
