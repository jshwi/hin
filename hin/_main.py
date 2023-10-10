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
from ._actions import Move as _Move
from ._add import add as _add
from ._config import Config as _Config
from ._file import Custom as _Custom
from ._file import Entry as _Entry
from ._gitignore import Gitignore as _Gitignore
from ._link import link_ as _link
from ._status import status as _status
from ._undo import undo as _undo
from ._version import __version__


class Object(_t.TypedDict):
    """Dict-like class container."""

    config: _Config
    console: _Console


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
@_click.pass_context
def cli(ctx: _click.Context) -> None:
    """Dotfile manager.

    \f

    :param ctx: Context object.
    """
    # parse git variables ahead of time in case .gitconfig is a
    # dotfile
    user = _getpass.getuser()
    email = f"{user}@{_socket.gethostname()}"
    gitconfig = _git.GitConfigParser()
    user_data_dir = _appdirs.user_data_dir()
    dotfiles = str(_Path(user_data_dir) / __package__)
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

    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "config": _Config(),
            "console": _Console(soft_wrap=bool(_e.get("HIN_DEBUG") == "1")),
        }
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


@cli.command("remove")
@_help_option
@_click.argument("file")
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
@_click.pass_obj
@_decorators.repository
def __remove(obj: Object, file: str) -> str:
    """Remove FILE from version control.

    All links that point to the file, and any links to those links, will
    be removed.

    If the dotfile is not a link to another dotfile then the checked in
    file or directory will be moved back to its original location in its
    place.

    Changes will be committed.
    """
    matrix = obj["config"][file]
    obj["config"].remove_links(matrix)
    if isinstance(matrix, _Entry):
        if matrix.value.path.is_dir():
            _Gitignore(matrix.value.path).remove()

        _Move(matrix).undo()

    obj["console"].print(f"removed {matrix.key.path} from dotfiles")
    return f"remove {file}"


@cli.command("undo", help=_undo.__doc__)
@_help_option
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
def __undo() -> None:
    _undo()


@cli.command("clone")
@_click.argument("url")
@_click.option("-b", "--branch", help="Branch to clone (default: master).")
@_help_option
@_click.pass_obj
def __clone(obj: Object, url: str, branch: str | None) -> None:
    """Clone a dotfile repository from a URL."""
    kwargs = {}
    if branch is not None:
        kwargs["branch"] = branch

    path = _Path(_e["DOTFILES"])
    obj["console"].print(f"cloning '{url.split('/')[-1]}' into {path}")
    _git.Repo.clone_from(url, path, **kwargs)  # type: ignore
    obj["console"].print("[green bold]cloned dotfile repo[/green bold]")


@cli.command("push")
@_help_option
@_click.option("-r", "--remote", help="set remote upstream")
@_click.pass_obj
@_decorators.repository
def __push(obj: Object, remote: str | None, repo: _git.Repo) -> None:
    """Push changes to remote."""
    origin = "origin"
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
            repo.git.remote() == origin
            and repo.git.remote("get-url", origin) == remote
        ):
            try:
                repo.git.remote("remove", origin)
            except _git.GitCommandError:
                pass

            repo.git.remote("add", origin, remote)

    try:
        if "Your branch is up to date with" in repo.git.status():
            obj["console"].print("no changes to push to remote")
        else:
            repo.git.push(origin, "master", set_upstream=True)
            obj["console"].print(
                "[green bold]changes pushed to remote[/green bold]"
            )
    except _git.GitCommandError as err:
        if "'origin' does not appear to be a git repository" in str(err):
            raise RuntimeError(
                "'origin' does not appear to be a git repository\n"
                "try running `hin push --remote=<REMOTE>` to set origin"
                " upstream"
            ) from err

        raise err


@cli.command("status", help=_status.__doc__)
@_help_option
@_click.option("-f", "--file", help="specific dotfile to check")
def __status(file: str | None) -> None:
    _status(file)


@cli.command("commit")
@_help_option
@_click.argument("file")
@_click.pass_obj
@_decorators.repository
def __commit(obj: Object, file: str, repo: _git.Repo) -> str | None:
    """Commit changes to FILE.

    \f

    Restore item chosen to commit as `repository` decorator stashes, and
    then commits changes, made within wrapped function before popping
    the stash.
    """
    try:
        entry = _Entry.new(file)
        # add commit message here because key changes if `entry` is a
        # child of an existing dotfile
        commit_message = f"update {entry.key.relpath}"
        for existing in obj["config"].values():
            if entry.is_child_of(existing):
                entry = existing.child(existing)

        repo.git.restore("--source", "stash@{0}", "--", entry.value.path)
        if repo.git.diff("HEAD", "--", entry.value.path):
            repo.git.add(entry.value.path)
            return commit_message

    except _git.GitCommandError:
        pass

    obj["console"].print("nothing to commit")
    return None


@cli.command("list")
@_help_option
@_click.pass_obj
def __list_(obj: Object) -> None:
    """List all versioned dotfiles."""
    for matrix in obj["config"].values():
        kind = "[green bold]+[/green bold]"
        value = str(matrix.key.path)
        if isinstance(matrix, _Custom):
            kind = "[cyan bold]=[/cyan bold]"
            value += f" -> {matrix.value.path}"

        obj["console"].print(kind, value)


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
