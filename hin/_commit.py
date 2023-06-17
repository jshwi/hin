"""
hin._commit
===========
"""
from __future__ import annotations

import git as _git
from git import Repo as _Repo
from rich.console import Console as _Console

from . import _decorators
from ._config import Config as _Config
from ._file import Entry as _Entry


@_decorators.console
@_decorators.config
@_decorators.repository
def commit(
    config: _Config, out: _Console, file: str, repo: _Repo
) -> str | None:
    """Commit changes to FILE.

    \f

    Restore item chosen to commit as `repository` decorator stashes, and
    then commits changes, made within wrapped function before popping
    the stash.

    :param config: Dotfiles ini.
    :param out: Console object.
    :param file: Path to check status of.
    :param repo: Git repository type.
    :return: Git commit message.
    """
    try:
        entry = _Entry.new(file)
        for existing in config.values():
            if entry.is_child_of(existing):
                entry = existing.child(existing)

        repo.git.restore("--source", "stash@{0}", "--", entry.value.path)
        if repo.git.diff("HEAD", "--", entry.value.path):
            repo.git.add(entry.value.path)
            return f"update {entry.value.relpath}"

    except _git.GitCommandError:
        pass

    out.print("nothing to commit")
    return None
