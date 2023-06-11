"""
hin._clone
==========
"""
from __future__ import annotations

from os import environ as _e
from pathlib import Path as _Path

import git as _git
from rich.console import Console as _Console

from . import _decorators


@_decorators.console
def clone(out: _Console, url: str, branch: str | None) -> None:
    """Clone a dotfile repository from a URL.

    \f

    :param out: Console object.
    :param url: Remote URL.
    :param branch: Branch to clone.
    """
    kwargs = {}
    if branch is not None:
        kwargs["branch"] = branch

    path = _Path(_e["DOTFILES"])
    out.print(f"cloning '{url.split('/')[-1]}' into {path}")
    _git.Repo.clone_from(url, path, **kwargs)  # type: ignore
    out.print("[green bold]cloned dotfile repo[/green bold]")
