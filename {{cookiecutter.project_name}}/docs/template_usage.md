# Using this template

Welcome to the developer guidelines! This document is split into two parts:

1. The [repository setup](#setting-up-the-repository).
   This section is relevant primarily for the repository maintainer and shows how to connect continuous integration services and documents initial set-up of the repository.
2. The [contributor guide](contributing.md#contributing-guide).
   It contains information relevant to all developers who want to make a contribution.

## Setting up the repository

### First commit

If you are reading this, you should have just completed the repository creation with:

```bash
cruft create https://github.com/scverse/cookiecutter-scverse
```

and you should have

```
cd {{cookiecutter.project_name}}
```

into the new project directory.
Now that you have created a new repository locally, the first step is to push it to GitHub.
To do this, you have to create a **new repository** on GitHub.
You can follow the instructions directly on [github quickstart guide][].
Since `cruft` already populated the local repository of your project with all the necessary files,
we suggest to _NOT_ initialize the repository with a `README.md` file or `.gitignore`, because you might encounter git conflicts on your first push.

:::{note}
If you are looking at this document in the [cookiecutter-scverse-instance][] repository documentation,
throughout this document the name of the project is `cookiecutter-scverse-instance`.
Otherwise it should be replaced by your new project name: `{{cookiecutter.project_name}}`.
:::

Now that your new project repository has been created on GitHub at `https://github.com/{{cookiecutter.github_user}}/{{cookiecutter.project_name}}`,
you can push your first commit to GitHub:

Assuming you are in `/your/path/to/{{cookiecutter.project_name}}`.
Add all files and commit.

```bash
# stage all files of your new repo
git add --all
# commit
git commit -m "first commit"
```

You'll notice that the command `git commit` installed a bunch of packages and triggered their execution: those are [pre-commit][]!
To read more about what they are and what they do, you can go to the related section [Pre-commit checks](#pre-commit-checks) in this document.

```bash
git add -u # update all tracked file
git commit -m "first commit"
```

:::

Now that all the files of the newly created project have been committed, go ahead with the remaining steps:

```bash
# update the `origin` of your local repo with the remote GitHub link
git remote add origin https://github.com/{{cookiecutter.github_user}}/{{cookiecutter.project_name}}.git
# rename the default branch to main
git branch -M main
# push all your files to remote
git push -u origin main
```

Your project should be now available at `https://github.com/{{cookiecutter.github_user}}/{{cookiecutter.project_name}}`.
While the repository at this point can be directly used, there are few remaining steps that needs to be done in order to achieve full functionality.

[github quickstart guide]: https://docs.github.com/en/get-started/quickstart/create-a-repo?tool=webui
[cookiecutter-scverse-instance]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html

### The pyproject.toml file

Modern Python package management uses a `pyproject.toml` that was first introduced in [PEP 518](https://peps.python.org/pep-0518/).
This file contains build system requirements and information, which are used by pip to build the package, and tool configurations.
For more details please have a look at [pip's description of the pyproject.toml file](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/).

#### Important metadata fields

The `[project]` section in the `pyproject.toml` file defines several important metadata fields that might require editing.
For example, the `name`, `description`, `authors` fields could need updates as the project evolves.
Especially, the `version` field needs to be adapted if newer versions of the package are to be released.
See {ref}`vcs-based-versioning` for more details.

#### Dependency management

Package dependencies can be added to the `dependencies` of the `[project]` section.
You can constrain versions using any of `>=`, `>`, `<`, `<=`, `==`, `!=`, and `~=`.
A common example would be `twine>=4.0.2` which requires `twine` to be installed with at least version `4.0.2` or greater.
As another example, if there is a known buggy version, you could exclude it like `numpy >=3.0, !=3.0.5`.

Further optional dependencies are defined in the `[project.optional-dependencies]` section such as dependencies only for tests (`test`).
All dependencies listed in such optional dependency groups can then be installed by specifying them like: `pip install <package-name>[test]`.

#### Tool configurations

The `pyproject.toml` file also serves as single configuration file for many tools such as many {ref}`pre-commit`.
For example, the line length for auto-formatting can be configured as follows:

```toml
[tool.ruff]
line-length = 120
```

### Coverage tests with _Codecov_

Coverage tells what fraction of the code is "covered" by unit tests, thereby encouraging contributors to [write tests](contributing.md#writing-tests).
To enable coverage checks, head over to [codecov][] and sign in with your GitHub account.
You'll find more information in "getting started" section of the [codecov docs][].

In the `Actions` tab of your projects' GitHub repository, you can see that the workflows are failing due to the **Upload coverage** step.
The error message in the workflow should display something like:

```
...
    Retrying 5/5 in 2s..
    {'detail': ErrorDetail(string='Could not find a repository, try using repo upload token', code='not_found')}
Error: 404 Client Error: Not Found for url:
...
```

While [codecov docs][] has a very extensive documentation on how to get started,
_if_ you are using the default settings of this template we can assume that you are using [codecov][] in a GitHub action workflow and hence you can make use of the [codecov bot][].

To set it up, simply go to the [codecov app][] page and follow the instructions to activate it for your repository.
Once the activation is completed, go back to the `Actions` tab and re-run the failing workflows.

The workflows should now succeed, and you will be able to find the code coverage at this link:
`https://app.codecov.io/gh/{{cookiecutter.github_user}}/{{cookiecutter.project_name}}`.
You might have to wait a couple of minutes and the coverage of this repository should be ~60%.

If your repository is private, you will have to specify an additional token in the repository secrets.
In brief, you need to:

1. Generate a Codecov Token by clicking _setup repo_ in the codecov dashboard.
    - If you have already set up codecov in the repository by following the previous steps, you can directly go to the codecov repo webpage.
2. Go to _Settings_ and copy **only** the token `_______-____-...`.
3. Go to _Settings_ of your newly created repository on GitHub.
4. Go to _Security > Secrets > Actions_.
5. Create new repository secret with name `CODECOV_TOKEN` and paste the token generated by codecov.
6. Paste these additional lines in `/.github/workflows.test.yaml` under the **Upload coverage** step:
    ```bash
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
          token: {% raw %}${{ secrets.CODECOV_TOKEN }}{% endraw %}
    ```
7. Go back to GitHub `Actions` page an re-run previously failed jobs.

[codecov]: https://about.codecov.io/sign-up/
[codecov docs]: https://docs.codecov.com/docs
[codecov bot]: https://docs.codecov.com/docs/team-bot
[codecov app]: https://github.com/apps/codecov

### Documentation on _readthedocs_

We recommend using [readthedocs.org][] (RTD) to build and host the documentation for your project.
To enable readthedocs, head over to [their website][readthedocs.org] and sign in with your GitHub account.
On the RTD dashboard choose "Import a Project" and follow the instructions to add your repository.

- Make sure to choose the correct name of the default branch.
  On GitHub, the name of the default branch should be `main`.
- We recommend enabling documentation builds for pull requests (PRs).
  This ensures that a PR doesn't introduce changes that break the documentation.
  To do so, got to `Admin -> Advanced Settings`, check the `Build pull requests for this projects` option, and click `Save`.
  For more information, please refer to the [official RTD documentation][rtd-prs].
- If you find the RTD builds are failing, you can disable the `fail_on_warning` option in `.readthedocs.yaml`.

If your project is private, there are ways to enable docs rendering on [readthedocs.org][] but it is more cumbersome and requires a different RTD subscription.
See a guide [here](https://docs.readthedocs.io/en/stable/guides/importing-private-repositories.html).

[readthedocs.org]: https://readthedocs.org/
[rtd-prs]: https://docs.readthedocs.io/en/stable/pull-requests.html

(github-actions)=

### Github Actions

[GitHub Actions][] is a continous integration (CI)/continous development (CD) automation tool that enables workflows for building, testing, and deploying code directly from a GitHub repository.
It uses YAML-based configuration files to define jobs and steps, which can be triggered by events like pushes, pull requests, or scheduled runs.
This project comes with several pre-configured workflows that can be found in the `.github/workflows` folder:

1. **Build workflow**: Checks that your package builds correctly by creating distribution packages and validating them with [twine][].
   This helps catch packaging issues early.

2. **Test workflow**: Runs your test suite on multiple Python versions and operating systems to ensure cross-platform compatibility.
   It automatically runs when you push to the main branch or create a pull request.

3. **Release workflow**: Automatically publishes your package to PyPI when you create a new release on GitHub.
   This workflow uses trusted publishing for secure deployment.

To check the status of these workflows, go to the "Actions" tab in your GitHub repository.
There you can see the execution history, logs, and (re-)trigger workflows manually if needed.

[Github Actions]: https://github.com/features/actions
[twine]: https://github.com/pypa/twine

### Automating PyPI released using GitHub actions

#### Configuring the Github workflow

Tags adhering to `"*.*.*"` that are pushed to the `main` branch will trigger the release Github workflow that automatically builds and uploads the Python package to [PyPI][].

For this to work, you'll need to setup GitHub as a [trusted publisher][] on PyPI.
To set this up, login to [PyPI][], and proceed depending on whether you already have your project on there or not:
- If yes, navigate to the project. In the left sidebar, choose "Publishing", then proceed to add the repository details.
- If not, go to your [PyPI publishing settings][] and fill out the “Add a new pending publisher” form.

The "Workflow name" needs to bet set to `release.yaml`.
In most cases, you can leave the "Environment name" empty.
For more details, please refer to the official [PyPI guide for setting up trusted publishing][pypi-trusted-publishing-guide].

[pypi]: https://pypi.org/
[pypi-trusted-publishing-guide]: https://docs.pypi.org/trusted-publishers/adding-a-publisher/

(pre-commit)=

### Pre-commit checks

[Pre-commit][] checks are fast programs that check code for errors, inconsistencies and code styles, before the code is committed.

This template uses a number of pre-commit checks.
In this section we'll detail what is used, where they're defined, and how to modify these checks.

[pre-commit]: https://pre-commit.com/

#### Pre-commit CI

We recommend setting up [pre-commit.ci][] to enforce consistency checks on every commit and pull-request.

To do so, head over to [pre-commit.ci][] and click "Sign In With GitHub".
Follow the instructions to enable pre-commit.ci for your account or your organization.
You may choose to enable the service for an entire organization or on a per-repository basis.

Once authorized, pre-commit.ci should automatically be activated.

[pre-commit.ci]: https://pre-commit.ci/

#### Overview of pre-commit hooks used by the template

The following pre-commit hooks are for code style and format:

- [biome](https://biomejs.dev/):
  code formatter for non-Python files (e.g. JSON).
- [ruff][] formatting (`ruff-format`) which implements all rules of the also widely used [Black formatter](https://github.com/psf/black)
- [ruff][] based checks:
    - [isort](https://beta.ruff.rs/docs/rules/#isort-i) (rule category: `I`):
      sort module imports into sections and types.
    - [pydocstyle](https://beta.ruff.rs/docs/rules/#pydocstyle-d) (rule category: `D`):
      pydocstyle extension of flake8.
    - [flake8-tidy-imports](https://beta.ruff.rs/docs/rules/#flake8-tidy-imports-tid) (rule category: `TID`):
      tidy module imports.
    - [flake8-comprehensions](https://beta.ruff.rs/docs/rules/#flake8-comprehensions-c4) (rule category: `C4`):
      write better list/set/dict comprehensions.
    - [pyupgrade](https://beta.ruff.rs/docs/rules/#pyupgrade-up) (rule category: `UP`):
      upgrade syntax for newer versions of the language.

The following pre-commit hooks are for errors and inconsistencies:

- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks): generic pre-commit hooks for text files.
    - **detect-private-key**: checks for the existence of private keys.
    - **check-ast**: check whether files parse as valid python.
    - **end-of-file-fixer**: check files end in a newline and only a newline.
    - **mixed-line-ending**: checks mixed line ending.
    - **trailing-whitespace**: trims trailing whitespace.
    - **check-case-conflict**: check files that would conflict with case-insensitive file systems.
    - **forbid-to-commit**: Make sure that `*.rej` files cannot be commited.
      These files are created by the [automated template sync](#automated-template-sync)
      if there's a merge conflict and need to be addressed manually.
- [ruff][] based checks:
    - [pyflakes](https://beta.ruff.rs/docs/rules/#pyflakes-f) (rule category: `F`):
      various checks for errors.
    - [pycodestyle](https://beta.ruff.rs/docs/rules/#pycodestyle-e-w) (rule category: `E`, `W`):
      various checks for errors.
    - [flake8-bugbear](https://beta.ruff.rs/docs/rules/#flake8-bugbear-b) (rule category: `B`):
      find possible bugs and design issues in program.
    - [flake8-blind-except](https://beta.ruff.rs/docs/rules/#flake8-blind-except-ble) (rule category: `BLE`):
      checks for blind, catch-all `except` statements.
    - [Ruff-specific rules](https://beta.ruff.rs/docs/rules/#ruff-specific-rules-ruf) (rule category: `RUF`):
        - `RUF100`: remove unneccesary `# noqa` comments ()

#### How to add or remove pre-commit checks

The [pre-commit checks](#pre-commit-checks) check for both correctness and stylistic errors.
In some cases it might overshoot and you may have good reasons to ignore certain warnings.
This section shows you where these checks are defined, and how to enable/ disable them.

##### pre-commit

You can add or remove pre-commit checks by simply deleting relevant lines in the `.pre-commit-config.yaml` file under the repository root.
Some pre-commit checks have additional options that can be specified either in the `pyproject.toml` (for [ruff][]) or tool-specific config files,
such as `biome.jsonc` for [biome][].

##### Ruff

This template configures `ruff` through the `[tool.ruff]` entry in the `pyproject.toml`.
For further information `ruff` configuration, see [the docs][ruff-config].

Ruff assigns code to the rules it checks (e.g. `E401`) and groups them under a rule category (e.g. `E`).
Rule categories are selectively enabled by including them under the `select` key:

```toml
[tool.ruff]
# ...

select = [
    "F",  # Errors detected by Pyflakes
    "E",  # Error detected by Pycodestyle
    "W",  # Warning detected by Pycodestyle
    "I",  # isort
    # ...
]
```

The `ignore` entry is used to disable specific rules for the entire project.
Add the rule code(s) you want to ignore and don't forget to add a comment explaining why.
You can find a long list of checks that this template disables by default sitting there already.

```toml
ignore = [
    # ...
    # __magic__ methods are often self-explanatory, allow missing docstrings
    "D105",
    # ...
]
```

Checks can be ignored per-file (or glob pattern) with `[tool.ruff.per-file-ignores]`.

```toml
[tool.ruff.per-file-ignores]
"docs/*" = ["I"]
"tests/*" = ["D"]
"*/__init__.py" = ["F401"]
```

To ignore a specific rule on a per-case basis, you can add a `# noqa: <rule>[, <rule>, …]` comment to the offending line.
Specify the rule code(s) to ignore, with e.g. `# noqa: E731`.
Check the [Ruff guide][ruff-error-suppression] for reference.

```{note}
The `RUF100` check will remove rule codes that are no longer necessary from `noqa` comments.
If you want to add a code that comes from a tool other than Ruff,
add it to Ruff’s [`external = [...]`][ruff-external] setting to prevent `RUF100` from removing it.
```

[ruff]: https://docs.astral.sh/ruff/
[ruff-error-suppression]: https://docs.astral.sh/ruff/linter/#error-suppression
[ruff-config]: https://docs.astral.sh/ruff/configuration/
[ruff-external]: https://docs.astral.sh/ruff/settings/#external

### API design

Scverse ecosystem packages should operate on [AnnData][], [MuData][], and/or [SpatialData][] data structures and typically use an API
as originally [introduced by scanpy][scanpy-api] with the following submodules:

- `pp` for preprocessing
- `tl` for tools (that, compared to `pp` generate interpretable output, often associated with a corresponding plotting function)
- `pl` for plotting functions

You may add additional submodules as appropriate.
While we encourage to follow a scanpy-like API for ecosystem packages,
there may also be good reasons to choose a different approach, e.g. using an object-oriented API.

[anndata]: https://github.com/scverse/anndata
[mudata]: https://github.com/scverse/mudata
[spatialdata]: https://github.com/scverse/spatialdata

[scanpy-api]: https://scanpy.readthedocs.io/en/stable/usage-principles.html

(vcs-based-versioning)=

### Using VCS-based versioning

By default, the template uses hard-coded version numbers that are set in `pyproject.toml`.
If you prefer to have your project automatically infer version numbers from git tags,
it is straightforward to switch to vcs-based versioning using [hatch-vcs][].

In `pyproject.toml` add the following changes, and you are good to go!

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -1,11 +1,11 @@
 [build-system]
 build-backend = "hatchling.build"
-requires = ["hatchling"]
+requires = ["hatchling", "hatch-vcs"]


 [project]
 name = "{{ cookiecutter.project_name }}"
-version = "0.3.1dev"
+dynamic = ["version"]

@@ -60,6 +60,9 @@
+[tool.hatch.version]
+source = "vcs"
+
 [tool.coverage.run]
 source = ["{{ cookiecutter.project_name }}"]
 omit = [
```

Don't forget to update the [Making a release section](contributing.md#publishing-a-release) in this document accordingly, after you are done!

[hatch-vcs]: https://pypi.org/project/hatch-vcs/

### Automated template sync

Automated template sync is enabled by default.
This means that every night, a GitHub action runs [cruft][] to check if a new version of the `scverse-cookiecutter` template got released.
If there are any new changes, a pull request proposing these changes is created automatically.
This helps keeping the repository up-to-date with the latest coding standards.

It may happen that a template sync results in a merge conflict.
If this is the case a `*.ref` file with the diff is created.
You need to manually address these changes and remove the `.rej` file when you are done.
The pull request can only be merged after all `*.rej` files have been removed.

:::{tip}
The following hints may be useful to work with the template sync:

- GitHub automatically disables scheduled actions if there has been not activity to the repository for 60 days.
  You can re-enable or manually trigger the sync by navigating to `Actions` -> `Sync Template` in your GitHub repository.
- If you want to ignore certain files from the template update,
  you can add them to the `[tool.cruft]` section in the `pyproject.toml` file in the root of your repository.
  More details are described in the [cruft documentation][cruft-update-project].
- To disable the sync entirely, simply remove the file `.github/workflows/sync.yaml`.

:::

[cruft]: https://cruft.github.io/cruft/
[cruft-update-project]: https://cruft.github.io/cruft/#updating-a-project

## Moving forward

You have successfully set up your project and are ready to start.
For everything else related to documentation, code style, testing and publishing your project to pypi, please refer to the [contributing docs](contributing.md#contributing-guide).

## Migrate existing projects to using this template

You can also update existing projects to make use of this template to benefit from the latest-greatest tooling and automated template updates.
This requires some manual work though.
Here's one way how to do it:

1. Let's assume your repository is checked out to `$REPO`
2. Clone your repository a second time to `${REPO}_cookiecutterized`
3. Initialize an empty repository from this cookiecutter template:

    ```bash
    mkdir template && cd template
    cruft create https://github.com/scverse/cookiecutter-scverse
    ```

4. remove everything from the existing repo

    ```bash
    cd ${REPO}_cookiecutterized
    git switch -c cookiecutterize
    git rm -r "*"
    git add -A
    git commit -m "clean repo"
    ```

5. move template over from generated folder

    ```bash
    # move everything, including hidden folders, excluding `.git`.
    rsync -av --exclude='.git' ../template/$REPO ./
    git add -A
    git commit -m "init from template"
    ```

6. Migrate your project: Move over files from `$REPO` to `${REPO}_cookiecutterized`.
   Omit files that are not needed anymore and manually merge files where required.

7. Commit your changes.
   Merge the `cookiecutterize` branch into the main branch, e.g. by making a pull request.
