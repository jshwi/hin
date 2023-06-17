"""
hin._push
=========
"""
from __future__ import annotations

import git as _git
from rich.console import Console as _Console

from . import _decorators

_ORIGIN = "origin"


@_decorators.console
@_decorators.repository
def push(out: _Console, remote: str | None, repo: _git.Repo) -> None:
    """Push changes to remote.

    \f

    :param out: Console object.
    :param remote: Remote URL.
    :param repo: Git repository type.
    """
    if remote is not None:
        # only add if no remote has been added yet
        # if you re-add the remote you get the following:
        #
        #     $ git status
        #     On branch master
        #     nothing to commit, working tree clean
        #
        # instead of:
        #
        #     $ git status
        #     On branch master
        #     Your branch is up to date with 'origin/master'
        #
        #     nothing to commit, working tree clean
        #
        # "Your branch is up to date with" is the unambiguous string to
        # look for to confirm that there is nothing to push
        if not (
            repo.git.remote() == _ORIGIN
            and repo.git.remote("get-url", _ORIGIN) == remote
        ):
            try:
                repo.git.remote("remove", _ORIGIN)
            except _git.GitCommandError:
                pass

            repo.git.remote("add", _ORIGIN, remote)

    try:
        if "Your branch is up to date with" in repo.git.status():
            out.print("no changes to push to remote")
        else:
            repo.git.push(_ORIGIN, "master", set_upstream=True)
            out.print("[green bold]changes pushed to remote[/green bold]")
    except _git.GitCommandError as err:
        if "'origin' does not appear to be a git repository" in str(err):
            raise RuntimeError(
                "'origin' does not appear to be a git repository\n"
                "try running `hin push --remote=<REMOTE>` to set origin"
                " upstream"
            ) from err

        raise err
