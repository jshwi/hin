"""
hin._status
===========
"""
from __future__ import annotations

import re as _re
from os import environ as _e
from pathlib import Path as _Path

import git as _git
from rich.console import Console as _Console

from . import _decorators
from ._config import Config as _Config


class _PathRef:
    def __init__(self, string: str) -> None:
        self._kind = ""
        self._path = string
        words = string.split()
        if len(words) > 1:
            self._kind = words[0]
            self._path = words[1]

    @property
    def kind(self) -> str:
        """Type of change."""
        return self._kind

    @property
    def path(self) -> _Path:
        """Changed path."""
        return _Path(self._path)


def _print_paths(line: str, config: _Config) -> None:
    if line.startswith("\t"):
        path_ref = _PathRef(_re.sub(" +", " ", line).strip())
        for existing in config.values():
            if str(path_ref.path).startswith(str(existing.value.relpath)):
                print(
                    path_ref.kind,
                    existing.key.relpath
                    / str(_Path(*path_ref.path.parts[1:])),
                )


def _print_status(out: _Console, output: str, config: _Config) -> None:
    for line in output.splitlines():
        if _re.match(r"((\w+(?: \w+)*):)", line):
            out.print(f"[green bold]{line}[/green bold]")

        _print_paths(line, config)


@_decorators.console
@_decorators.config
@_decorators.repository
def status(
    config: _Config, out: _Console, file: str | None, repo: _git.Repo
) -> None:
    """Check version status.

    \f

    Restore item chosen to check status for as `repository` decorator
    isolates user made changes from dotfile manager changes.

    :param config: Dotfiles ini.
    :param out: Console object.
    :param file: Path to check status of.
    :param repo: Git repository type.
    """
    value = _Path(_e["DOTFILES"])
    no_change_message = "no changes have been made to any dotfiles"
    if file is not None:
        entry = config[file]
        value = entry.value.path
        no_change_message = f"no changes have been made to {entry.key.path}"

    try:
        repo.git.restore("--source", "stash@{0}", "--", value)
        output = repo.git.status(value)
        if "nothing to commit, working tree clean" not in output:
            _print_status(out, output, config)

        repo.git.reset(hard=True)
        return
    except _git.GitCommandError:
        pass

    out.print(no_change_message)
