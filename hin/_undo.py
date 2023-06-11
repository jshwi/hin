"""
hin._undo
=========
"""
from os import environ as _e
from pathlib import Path as _Path

import git as _git
from rich.console import Console as _Console

from . import _decorators
from ._actions import Hist as _Hist
from ._config import Config as _Config


@_decorators.console
@_decorators.hist
@_decorators.config
@_decorators.repository
def undo(config: _Config, hist: _Hist, out: _Console, repo: _git.Repo) -> str:
    """Revert previous commit and actions.

    \f

    :param config: Config object.
    :param hist: Hist json.
    :param out: Console object.
    :param repo: Git repository type.
    :return: Git commit message.
    """
    revision = "HEAD"
    prev_revision = f"{revision}^"
    message = repo.git.log(revision, format="%B", max_count=1).strip()
    # check out dotfiles.ini to the previous commit
    repo.git.checkout(prev_revision, "--", config.path)
    commit = repo.git.rev_parse("--short", prev_revision)
    try:
        hist.run(commit)
        # check out .gitignore files to the previous commit
        for path in _Path(_e["DOTFILES"]).glob("**/.gitignore"):
            repo.git.checkout(prev_revision, "--", path)

    except KeyError:
        pass

    out.print(f"reverted to {commit}")
    return f'revert "{message}"'
