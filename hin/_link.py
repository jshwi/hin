"""
hin._link
=========
"""
from rich.console import Console as _Console

from . import _decorators
from ._config import Config as _Config
from ._file import Custom as _Custom
from ._gitignore import unignore as _unignore


@_decorators.console
@_decorators.config
@_decorators.repository
def link_(config: _Config, out: _Console, link: str, target: str) -> str:
    """Create a new LINK from TARGET.

    Create a symlink to an existing linked dotfile, reproducible with a
    dotfile installation. This is useful for shared configs.

    This will fail if the target is not a dotfile symlink or a child of
    a dotfile symlink.

    The target needs to be a link to a checked in file or dir, or a
    versioned descendant of a linked dir. Any other files or dirs cannot
    be installed, and the state reproduced, on a clean system.

    Changes will be committed.

    \f

    :param config: Dotfiles config.
    :param out: Console object.
    :param link: Source of symlink.
    :param target: Destination of symlink.
    :return: Git commit message.
    """
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
