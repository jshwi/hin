"""
hin._remove
===========
"""
from rich.console import Console as _Console

from . import _decorators
from ._actions import Move as _Move
from ._config import Config as _Config
from ._file import Entry as _Entry
from ._gitignore import Gitignore as _Gitignore


@_decorators.console
@_decorators.config
@_decorators.repository
def remove(config: _Config, out: _Console, file: str) -> str:
    """Remove FILE from version control.

    All links that point to the file, and any links to those links,
    will be removed.

    If the dotfile is not a link to another dotfile then the checked in
    file or directory will be moved back to its original location in its
    place.

    Changes will be committed.

    \f

    :param config: Dotfiles ini.
    :param out: Console object.
    :param file: Path to dotfile.
    :return: Git commit message.
    """
    matrix = config[file]
    config.remove_links(matrix)
    if isinstance(matrix, _Entry):
        if matrix.value.path.is_dir():
            _Gitignore(matrix.value.path).remove()

        _Move(matrix).undo()

    out.print(f"removed {matrix.key.path} from dotfiles")
    return f"remove {file}"
