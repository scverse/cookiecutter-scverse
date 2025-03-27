#!/bin/env python3
import shutil
from subprocess import run
from pathlib import Path

{% if not cookiecutter._render_devdocs %}
# Post processing
Path("docs/template_usage.md").unlink()
{% endif %}

# Skip directories marked for skipping
def skipped_dirs():
    for toplevel in Path().iterdir():
        if toplevel.name == ".git":
            continue
        if toplevel.name == "DELETE-ME":
            yield toplevel
        else:
            yield from toplevel.rglob("DELETE-ME")

for path in skipped_dirs():
    assert path.is_dir(), path
    shutil.rmtree(path)

# Insatll pre-commit
run("pre-commit install".split(), check=True)

# The following output was generated using rich
# The formatted output is included here directly, because I don't want
# rich as another dependency for initalizing the repo.
# Regenerate using `cd scripts; hatch run python -m scverse_template_scripts.make_rich_output`
print("""




┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        \x1b[1mSet-up online services\x1b[0m                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

\x1b[1mYour repository is now ready.\x1b[0m\x1b[1m \x1b[0m\x1b[1mHowever, to use all features of the \x1b[0m
\x1b[1mtemplate you will need to set up the following online services.\x1b[0m Clicking
on the links will take you to the respective sections of the developer
documentation. The developer documentation is also shipped as part of
the template in docs/developer_docs.md.

\x1b[1;33m 1 \x1b[0m\x1b]8;id=994867;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#pre-commit-checks\x1b\\\x1b[4;34mpre-commit.ci\x1b[0m\x1b]8;;\x1b\\ to check for inconsistencies and to enforce a code
\x1b[1;33m   \x1b[0mstyle
\x1b[1;33m 2 \x1b[0m\x1b]8;id=697682;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#documentation-on-readthedocs\x1b\\\x1b[4;34mreadthedocs.org\x1b[0m\x1b]8;;\x1b\\ to build and host documentation
\x1b[1;33m 3 \x1b[0m\x1b]8;id=723197;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#coverage-tests-with-codecov\x1b\\\x1b[4;34mcodecov\x1b[0m\x1b]8;;\x1b\\ to generate test coverage reports

All CI checks should pass, you are ready to start developing your new
tool!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          \x1b[1mLocal development\x1b[0m                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

To run tests or build the documentation locally, get familiar with \x1b]8;id=707150;https://hatch.pypa.io/latest/tutorials/environment/basic-usage/\x1b\\\x1b[4;34mhatch\x1b[0m\x1b]8;;\x1b\\
\x1b]8;id=707150;https://hatch.pypa.io/latest/tutorials/environment/basic-usage/\x1b\\\x1b[4;34menvironments\x1b[0m\x1b]8;;\x1b\\, and see \x1b[1;36;40m[tool.hatch.envs.*]\x1b[0m in \x1b[1;36;40mpyproject.toml\x1b[0m:

\x1b[40m                                                                        \x1b[0m
\x1b[40m \x1b[0m\x1b[97;40mhatch\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40mrun\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40mpre-commit\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40mrun\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40m--all-files\x1b[0m\x1b[97;40m  \x1b[0m\x1b[37;40m# tool.hatch.envs.default\x1b[0m\x1b[40m       \x1b[0m\x1b[40m \x1b[0m
\x1b[40m \x1b[0m\x1b[97;40mhatch\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40mtest\x1b[0m\x1b[97;40m                            \x1b[0m\x1b[37;40m# tool.hatch.envs.hatch-test\x1b[0m\x1b[40m    \x1b[0m\x1b[40m \x1b[0m
\x1b[40m \x1b[0m\x1b[97;40mhatch\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40mrun\x1b[0m\x1b[97;40m \x1b[0m\x1b[97;40mdocs:build\x1b[0m\x1b[97;40m                  \x1b[0m\x1b[37;40m# tool.hatch.envs.docs\x1b[0m\x1b[40m          \x1b[0m\x1b[40m \x1b[0m
\x1b[40m                                                                        \x1b[0m

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                            \x1b[1mCustomizations\x1b[0m                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Further instructions on using this template can be found in the \x1b]8;id=736137;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html\x1b\\\x1b[4;34mdev docs\x1b[0m\x1b]8;;\x1b\\
\x1b]8;id=736137;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html\x1b\\\x1b[4;34mincluded in the project\x1b[0m\x1b]8;;\x1b\\.

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                              \x1b[1mCommitment\x1b[0m                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

We expect developers of scverse ecosystem packages to

\x1b[1;33m • \x1b[0m\x1b]8;id=213267;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#writing-tests\x1b\\\x1b[4;34mwrite unit tests\x1b[0m\x1b]8;;\x1b\\
\x1b[1;33m • \x1b[0m\x1b]8;id=972096;https://cookiecutter-scverse-instance.readthedocs.io/en/latest/developer_docs.html#writing-documentation\x1b\\\x1b[4;34mprovide documentation\x1b[0m\x1b]8;;\x1b\\, including tutorials where applicable
\x1b[1;33m • \x1b[0msupport users through github and the \x1b]8;id=997067;https://discourse.scverse.org/\x1b\\\x1b[4;34mscverse discourse\x1b[0m\x1b]8;;\x1b\\

""")
