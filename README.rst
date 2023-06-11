hin
======
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License
.. image:: https://img.shields.io/pypi/v/hin
    :target: https://pypi.org/project/hin/
    :alt: PyPI
.. image:: https://github.com/jshwi/hin/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/jshwi/hin/actions/workflows/build.yaml
    :alt: Build
.. image:: https://github.com/jshwi/hin/actions/workflows/codeql-analysis.yml/badge.svg
    :target: https://github.com/jshwi/hin/actions/workflows/codeql-analysis.yml
    :alt: CodeQL
.. image:: https://results.pre-commit.ci/badge/github/jshwi/hin/master.svg
   :target: https://results.pre-commit.ci/latest/github/jshwi/hin/master
   :alt: pre-commit.ci status
.. image:: https://codecov.io/gh/jshwi/hin/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jshwi/hin
    :alt: codecov.io
.. image:: https://readthedocs.org/projects/hin/badge/?version=latest
    :target: https://hin.readthedocs.io/en/latest/?badge=latest
    :alt: readthedocs.org
.. image:: https://img.shields.io/badge/python-3.8-blue.svg
    :target: https://www.python.org/downloads/release/python-380
    :alt: python3.8
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Black
.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/
    :alt: isort
.. image:: https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg
    :target: https://github.com/PyCQA/docformatter
    :alt: docformatter
.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
    :target: https://github.com/PyCQA/pylint
    :alt: pylint
.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security Status
.. image:: https://snyk.io/test/github/jshwi/hin/badge.svg
    :target: https://snyk.io/test/github/jshwi/hin/badge.svg
    :alt: Known Vulnerabilities
.. image:: https://snyk.io/advisor/python/hin/badge.svg
    :target: https://snyk.io/advisor/python/hin
    :alt: hin

Dotfile manager
---------------

.. code-block:: shell

    Usage: hin [OPTIONS] COMMAND [ARGS]...

      Dotfile manager.

    Options:
      -h, --help     Show this message and exit.
      -v, --version  Show the version and exit.

    Commands:
      add        Add new FILE to version control.
      clone      Clone a dotfile repository from a URL.
      commit     Commit changes to FILE.
      install    Install a dotfile repository.
      link       Create a new LINK from TARGET.
      list       List all versioned dotfiles.
      push       Push changes to remote.
      remove     Remove FILE from version control.
      status     Check version status.
      undo       Revert previous commit and actions.
      uninstall  Uninstall a dotfile repository.
