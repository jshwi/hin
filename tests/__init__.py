"""
tests
=====

Test package for ``hin``.
"""
# pylint: disable=too-many-arguments
from __future__ import annotations

import typing as t
from pathlib import Path

from click.testing import Result
from templatest.utils import VarPrefix, VarSeq, VarSeqSuffix

FixtureCli = t.Callable[..., Result]

Command = t.Tuple[t.Callable[..., t.Any], t.Sequence[t.Any]]

DOTFILES = Path("dotfiles")
DOTFILESINI = Path("dotfiles.ini")
DOTFILESJSON = Path("dotfiles.json")
DATETIME = "2012-01-14 03:21:34"
TIMESTAMP = "20120114032134"
GITIGNORE = Path(".gitignore")
LIBRARY = "Library"
ALREADY_ADDED = "already added"
APPDIRS_SYSTEM = "appdirs.system"
GRANDPARENT = "grandparent"
PARENT = "parent"
SHARE = "share"
APPLICATION_SUPPORT = "Application Support"
UNINSTALL = "uninstall"
CODE = "Code"
INSTALL = "install"
REMOVE = "remove"
LINK = "link"
UNDO = "undo"
ADD = "add"
DARWIN = "darwin"
REMOTE = "remote"
PUSH = "push"
STATUS = "status"
COMMIT = "commit"
TIMESTAMP_HASH = "887a76a"
NOTHING_TO_COMMIT = "nothing to commit"

args = VarPrefix("--", "-")
changed = VarSeq("changed")


class FixtureMakeTree(t.Protocol):  # pylint: disable=too-few-public-methods
    """Type for ``fixture_make_tree``."""

    def __call__(
        self, obj: dict[t.Any, t.Any], root: Path | None = None
    ) -> None:
        """Type for ``fixture_make_tree``."""


class PathVals:
    """Path values.

    :param index: Sequence index.
    """

    def __init__(self, index: int) -> None:
        name = "file"
        self._index = index
        self._src = VarSeq(name)
        self._dst = VarSeq(f".{name}")
        self._contents = VarSeq("contents")
        self._backup = VarSeqSuffix(f".{name}", f".{TIMESTAMP}", "_")
        self._nested_backup = VarSeqSuffix(name, f".{TIMESTAMP}", "_")

    @property
    def src(self) -> Path:
        """File name."""
        return Path(self._src[self._index])

    @property
    def dst(self) -> Path:
        """Dotfile name."""
        return Path(self._dst[self._index])

    @property
    def contents(self) -> str:
        """File contents."""
        return self._contents[self._index]

    @property
    def backup(self) -> Path:
        """Backup name."""
        return Path(self._backup[self._index])

    @property
    def nested_backup(self) -> Path:
        """Nested backup name."""
        return Path(self._nested_backup[self._index])


P1 = PathVals(1)
P2 = PathVals(2)
P3 = PathVals(3)
P4 = PathVals(4)
