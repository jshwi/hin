"""
hin._add
========
"""
from pathlib import Path as _Path

from rich.console import Console as _Console

from . import _decorators
from ._actions import Move as _Move
from ._config import Config as _Config
from ._file import Entry as _Entry
from ._gitignore import Gitignore as _Gitignore
from ._gitignore import unignore as _unignore


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


@_decorators.console
@_decorators.config
@_decorators.repository
def add(config: _Config, out: _Console, file: str) -> str:
    """Add new FILE to version control.

    If the file is a symlink not related to the dotfile repo
    then the source of the symlink will be added. The original path will
    be symlinked to the versioned file.

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

    \f

    :param config: Config object.
    :param out: Console object.
    :param file: Dotfile to add.
    :return: Git commit message.
    """
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
    return f"add {entry.key.path.relative_to(_Path.home())}"
