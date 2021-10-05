# Python Project Template

![Tests](https://github.com/digital-bauhaus/python-template/workflows/Tests/badge.svg)
![Code Style](https://github.com/digital-bauhaus/python-template/workflows/Code%20Style/badge.svg)

Python packaging can be confusing because there are [a][borini] [lot][yeaw]
[of][bernat] [different][smith] opinions and [loose standards][pep518].

This is a template for a Python project following all the current best
practices. Since there is not just one way to do those things in Python this
is also kind of opinionated but I tried to reduce this to a minimum.

This template is configured for Python versions 3.6 and above and should work on
Linux, macOS and Windows.

## Getting Started

To use this template for your project, do the following:

1. Update the `[tool.poetry]` section of the `pyproject.toml` with your and you
   package’s information.
2. If you want to use another license, change `COPYING` file and `license`
   section in `pyproject.toml`. You may consider changing the filename of
   `COPYING` if you do not want to use GPL according to the licence’s
   [guidelines][so-licences].
3. Rename `src/sample_package` to `src/$YOURPROJECT`.
4. Update `docs/index.rst` to match your package.
5. Enable GitHub Pages to make your documentation available.

## Poetry Quickstart

[Poetry](https://poetry.eustace.io/) is used to build the package. After
installing Poetry, you can install this package with:

    poetry install

Poetry handles all the dependencies and virtual environments for you. To run
your code from and in your virtual environment prepend `poetry run` to your
command. This applies to all the non-Make commands in this README.

By default, Poetry creates the virtual environments in it’s own directory.
Since a lot of other tools expect your virtual environments in the project
directory itself as `.venv`. To do that, add the following lines in
`poetry.toml`:

    [virtualenvs]
    in-project = true
    path = ".venv"

You can add dependencies with `poetry [-D] add $DEPENDENCY_NAME`, where `-D`
specifies development dependencies, e.g. libraries you need to build and
develop the code that don’t need to be shipped for end users. I advise you to
take a look at the [Poetry documentation][poetry documentation]


## Makefile

This repository also provides a Makefile for convenience. It contains the
following rules:

* `install` (default): Install the package with poetry
* `test`: This is probably the most useful rule for developing. It checks the
          linter and runs the tests with the current Python version. This will
          also run in the CI.
* `linters`: Run the linters. You can disable certain errors in
             [`pyproject.toml`](pyproject.toml) and the [`Makefile`](Makefile)
             itself. This will also run in the CI.
* `codeformat`: Format all source and test files with Black.
* `distribution`: Build the source distribution and wheel packages.
* `docs`: Build the documentation with Sphinx
* `docs-spelling`: Run a spell checker on the documentation. You can add your
                   own dictionary in `docs/spelling_wordlist.txt`.
* `clean`: Removes all the local build files. Note that this does not include
           anything in the virtual environment to prevent conflicts with your
           Poetry workflow.

I recommend using the make rules instead of running all the commands manually
since it's easy to forget something.

To adjust the Makefile to your project you have to change the `MODULE_NAME`. If
your source folder names differ from this template, this has to be changed in
`SOURCE_FOLERS` accordingly.

## GitHub Actions Workflows

CI should work out of the box with the provided configurations in
`.github/workflow`. The following workflows are provided

### Code Formatting

The `linter.yml` workflow checks the source code with [Black][black], flake8,
pylint and pydocstyle.

To format your contributions so that they will pass, run

    make codeformat

### Tests

The `test.yml` workflow will run the tests on the latest Ubuntu, macOS, and
Windows with Python 3.6, 3.7, and 3.8.

### Continuous Deployment

When you push commits tagged with tags that match "v\*.\*.\*", the source
distribution and the wheel package get uploaded to the releases page on GitHub.
This is configured in the `release.yml` workflow.

[borini]: https://stefanoborini.com/current-status-of-python-packaging/
[yeaw]: https://dan.yeaw.me/posts/python-packaging-with-poetry-and-briefcase/
[bernat]: https://www.bernat.tech/pep-517-and-python-packaging/
[smith]: https://medium.com/@grassfedcode/goodbye-virtual-environments-b9f8115bc2b6
[pep518]: https://www.python.org/dev/peps/pep-0518/
[poetry documentation]: https://python-poetry.org/docs/basic-usage/
[black]: https://github.com/python/black
[so-licences]: https://stackoverflow.com/a/5678716
