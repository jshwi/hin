"""
hin._main
=========
"""
# pylint: disable=no-value-for-parameter
from __future__ import annotations

import getpass as _getpass
import re as _re
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
from ._actions import Hist as _Hist
from ._actions import Move as _Move
from ._config import Config as _Config
from ._file import Custom as _Custom
from ._file import Entry as _Entry
from ._gitignore import Gitignore as _Gitignore
from ._gitignore import unignore as _unignore
from ._version import __version__


class Object(_t.TypedDict):
    """Dict-like class container."""

    config: _Config
    console: _Console
    hist: _Hist


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
            "hist": _Hist(),
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


def _add_dir(out: _Console, entry: _Entry, config: _Config) -> None:
    gitignore = _Gitignore(entry.value.path)
    gitignore.make()
    for existing in dict(config).values():
        if existing.is_child_of(entry) and isinstance(existing, _Entry):
            # move the child back under the new dotfile and remove
            # from config
            child = entry.child(existing)
            _Move(child).do()
            config.remove(existing)
            out.print(f"unlinked {existing.key.path}")
            out.print(f"committing {existing.key.path}")
            # ensure the child remains versioned by including it in
            # all .gitignore files back up to the parent
            _unignore(child.value.path, entry.value.path)


def _add_child(entry: _Entry, config: _Config) -> bool:
    for existing in dict(config).values():
        if entry.is_child_of(existing):
            # exclude this file from .gitignore
            child = existing.child(entry)
            _unignore(child.value.path, child.value.path.parent)
            return True

    return False


@_decorators.repository
def _add(config: _Config, out: _Console, file: str) -> str:
    entry = _Entry.new(file)
    if str(entry.key) in config:
        raise TypeError(f"{entry.key.path} already added")

    if entry.key.path.is_symlink():
        # the target is now the file that the symlink is pointing to
        entry = entry.linksrc

    if entry.value.path.exists():
        # ensure no overwriting of files
        entry = entry.timestamped

    try:
        _Move(entry).do()
        if entry.value.path.is_dir():
            # add .gitignore files and check for any children that might
            # already be versioned
            _add_dir(out, entry, config)

        config.add(entry)
    except FileNotFoundError as err:
        # if move fails then check whether a child can be resolved to a
        # link by checking the dotfile repository internally
        # if selection is a child of an existing dotfile then exclude it
        # from the .gitignore files and commit it
        if not _add_child(entry, config):
            # the selection simply does not exist
            raise err

    out.print(f"added {entry.key.path}")
    return f"add {entry.key.relpath}"


@_decorators.repository
def _link(config: _Config, out: _Console, link: str, target: str) -> str:
    custom = _Custom(link, target)
    if str(custom.key) in config:
        raise TypeError(f"{custom.key.path} already added")

    for existing in config.values():
        # exclude path to child file from the .gitignore file to be
        # committed so that the link is valid
        if custom.is_child_of(existing) and custom.realsrc.value.path.exists():
            _unignore(custom.realsrc.value.path, existing.realsrc.value.path)

        # custom link is not linked to or a descendent of the checked in
        # file
        elif not custom.is_linked_to(existing):
            continue

        config.add(custom)
        out.print(f"linked {custom.key.path} to {custom.value.path}")
        return f"add {custom.key.path.name}"

    raise ValueError(
        "link not related to a symlink or parent of a symlink in dotfile repo"
    )


@cli.command("add")
@_click.argument("file")
@_help_option
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
@_click.pass_obj
def __add(obj: Object, file: str) -> None:
    """Add new FILE to version control.

    If the file is a symlink not related to the dotfile repo then the
    source of the symlink will be added. The original path will be
    symlinked to the versioned file.

    If the source file is a child of an already added directory it will
    be added as part of the directory. If the source file is a child of
    a directory that has not been added it will be installed
    individually, with the parents recreated, if they do not already
    exist.

    If the source file is a directory then only the directory will be
    added, unless there are child files that have already been added, in
    which case they will be unlinked and added to version control under
    the source.

    Changes will be committed.
    """
    entry = _Entry.new(file)
    is_link = False
    original_link = entry.key.relpath
    if entry.key.path.is_symlink():
        is_link = True
        original_link = entry.linksrc.key.path

    config = obj["config"]
    console = obj["console"]
    _add(config, console, file)
    if is_link:
        _Path(file).unlink()
        _link(config, console, link=file, target=original_link)


@cli.command("link")
@_help_option
@_click.argument("link")
@_click.argument("target")
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
@_click.pass_obj
def __link(obj: Object, link: str, target: str) -> None:
    """Create a new LINK from TARGET.

    Create a symlink to an existing linked dotfile, reproducible with a
    dotfile installation. This is useful for shared configs.

    This will fail if the target is not a dotfile symlink or a child of
    a dotfile symlink.

    The target needs to be a link to a checked in file or dir, or a
    versioned descendant of a linked dir. Any other files or dirs cannot
    be installed, and the state reproduced, on a clean system.

    Changes will be committed.
    """
    config = obj["config"]
    console = obj["console"]
    try:
        _link(config, console, link, target)
    except ValueError:
        _add(config, console, target)
        _link(config, console, link, target)


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


@cli.command("undo")
@_help_option
@_decorators.uninstall(quiet=True)
@_decorators.install(quiet=True)
@_click.pass_obj
@_decorators.repository
def __undo(obj: Object, repo: _git.Repo) -> str | None:
    """Revert previous commit and actions."""
    revision = "HEAD"
    prev_revision = f"{revision}^"
    message = repo.git.log(revision, format="%B", max_count=1).strip()
    # check out dotfiles.ini to the previous commit
    repo.git.checkout(prev_revision, "--", obj["config"].path)
    commit = repo.git.rev_parse("--short", prev_revision)
    try:
        obj["hist"].run(commit)
        # check out .gitignore files to the previous commit
        for path in _Path(_e["DOTFILES"]).glob("**/.gitignore"):
            repo.git.checkout(prev_revision, "--", path)

    except KeyError:
        pass

    obj["console"].print(f"reverted to {commit}")
    return f'revert "{message}"'


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


@cli.command("status")
@_help_option
@_click.option("-f", "--file", help="specific dotfile to check")
@_click.pass_obj
@_decorators.repository
def __status(obj: Object, file: str | None, repo: _git.Repo) -> None:
    """Check version status.

    \f

    Restore item chosen to check status for as `repository` decorator
    isolates user made changes from dotfile manager changes.
    """
    value = _Path(_e["DOTFILES"])
    no_change_message = "no changes have been made to any dotfiles"
    if file is not None:
        entry = obj["config"][file]
        value = entry.value.path
        no_change_message = f"no changes have been made to {entry.key.path}"

    if repo.stashed:  # type: ignore
        repo.git.restore("--source", "stash@{0}", "--", value)
        output = repo.git.status(value)
        if "nothing to commit, working tree clean" not in output:
            _print_status(obj["console"], output, obj["config"])

        repo.git.reset(hard=True)
        return

    obj["console"].print(no_change_message)


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
