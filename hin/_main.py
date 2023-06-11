"""
hin._main
=========
"""
# pylint: disable=no-value-for-parameter
from __future__ import annotations

import getpass as _getpass
import socket as _socket
import sys as _sys
import typing as _t
from os import environ as _e
from pathlib import Path as _Path

import appdirs as _appdirs
import click as _click
import git as _git
from click_help_colors import HelpColorsGroup as _HelpColorsGroup
from rich.console import Console as _Console

from . import _decorators
from ._add import add as _add
from ._clone import clone as _clone
from ._commit import commit as _commit
from ._file import Entry as _Entry
from ._link import link_ as _link
from ._list import list_ as _list
from ._push import push as _push
from ._remove import remove as _remove
from ._status import status as _status
from ._undo import undo as _undo
from ._version import __version__

_NAME = __name__.split(".", maxsplit=1)[0]


def _help_option(func: _t.Callable[..., _t.Optional[str]]):
    return _click.help_option("-h", "--help")(func)


@_click.group(
    cls=_HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="cyan",
)
@_help_option
@_click.version_option(
    __version__, "-v", "--version", message="%(prog)s version %(version)s"
)
def cli() -> None:
    """Dotfile manager."""
    # parse git variables ahead of time in case .gitconfig is a
    # dotfile
    user = _getpass.getuser()
    email = f"{user}@{_socket.gethostname()}"
    gitconfig = _git.GitConfigParser()
    user_data_dir = _appdirs.user_data_dir()
    dotfiles = str(_Path(user_data_dir) / _NAME)
    _e["USER_DATA_DIR"] = user_data_dir
    _e["DOTFILES"] = _e.get("DOTFILES", dotfiles)
    _e["GIT_AUTHOR_NAME"] = str(gitconfig.get_value("user", "name", user))
    _e["GIT_AUTHOR_EMAIL"] = str(gitconfig.get_value("user", "email", email))
    # simplify error output when not debugging
    if _e.get("HIN_DEBUG", None) != "1":
        err = _Console(soft_wrap=False, stderr=True)
        _sys.excepthook = lambda x, y, _: err.print(
            f"[red bold]{x.__name__}[/red bold]: {y}"
        )


@cli.command("install")
@_help_option
@_decorators.install()
def __install() -> None:
    """Install a dotfile repository.

    Repository needs to contain a dotfiles.ini file consisting of
    symlink to dotfile key-value pairs. The config will be parsed and
    all checked in files symlinked, relative to the home directory.

    Any files that share a name with a versioned file will be backed up
    and timestamped with the time of the installation.

    Any dangling symlinks that exist are removed if they share a name
    with a versioned dotfile.
    """


@cli.command("uninstall")
@_help_option
@_decorators.uninstall()
def __uninstall() -> None:
    """Uninstall a dotfile repository.

    This will remove all symlinks pointing to the dotfile repository.
    """


@cli.command("add", help=_add.__doc__)
@_click.argument("file")
@_help_option
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
def __add(file: str) -> None:
    entry = _Entry.new(file)
    is_link = False
    original_link = entry.key.relpath
    if entry.key.path.is_symlink():
        is_link = True
        original_link = entry.linksrc.key.path

    _add(file)
    if is_link:
        _Path(file).unlink()
        _link(link=file, target=original_link)


@cli.command("link", help=_link.__doc__)
@_help_option
@_click.argument("link")
@_click.argument("target")
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
def __link(link: str, target: str) -> None:
    try:
        _link(link, target)
    except ValueError:
        _add(target)
        _link(link, target)


@cli.command("remove", help=_remove.__doc__)
@_help_option
@_click.argument("file")
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
def __remove(file: str) -> None:
    _remove(file)


@cli.command("undo", help=_undo.__doc__)
@_help_option
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
def __undo() -> None:
    _undo()


@cli.command("clone", help=_clone.__doc__)
@_click.argument("url")
@_click.option("-b", "--branch", help="Branch to clone (default: master).")
@_help_option
def __clone(url: str, branch: str | None) -> None:
    _clone(url, branch)


@cli.command("push", help=_push.__doc__)
@_help_option
@_click.option("-r", "--remote", help="set remote upstream")
def __push(remote: str | None) -> None:
    _push(remote)


@cli.command("status", help=_status.__doc__)
@_help_option
@_click.option("-f", "--file", help="specific dotfile to check")
def __status(file: str | None) -> None:
    _status(file)


@cli.command("commit", help=_commit.__doc__)
@_help_option
@_click.argument("file")
def __commit(file: str) -> None:
    _commit(file)


@cli.command("list", help=_list.__doc__)
@_help_option
def __list_() -> None:
    _list()


# run git in dotfiles repo
# hin low level utility command used primarily for debugging
@cli.command(
    "git",
    context_settings={"ignore_unknown_options": True, "help_option_names": []},
    hidden=True,
)
@_click.argument("subcommand")
@_click.argument("args", nargs=-1, type=_click.UNPROCESSED)
@_decorators.console
def __git(
    out: _Console, subcommand: str, *args: _t.Any, **kwargs: _t.Any
) -> None:
    out.print(
        getattr(_git.Repo(_e["DOTFILES"]).git, subcommand)(*args, **kwargs)
    )
