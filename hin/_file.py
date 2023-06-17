"""
hin._file
=========
"""
from __future__ import annotations

import hashlib as _hashlib
import os as _os
import re as _re
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from datetime import datetime as _datetime
from os import environ as _e
from pathlib import Path as _Path


class _File(_ABC):
    def __init__(self, value: str | _Path) -> None:
        self._str = _os.path.expandvars(value)

    @property
    @_abstractmethod
    def root(self) -> _Path:
        """Root bounds essential to storing and retrieving file."""

    @property
    def relpath(self) -> _Path:
        """Path of file relative to its parent."""
        return _Path(self._str.replace(f"{self.root}/", ""))

    @property
    def path(self) -> _Path:
        """Full path to the file."""
        return self.root / self.relpath


class _Symlink(_File):
    def __init__(self, value: str | _Path) -> None:
        super().__init__(value)
        self._str = str(_Path.home() / _Path(_os.path.expandvars(value)))

    def __repr__(self) -> str:
        return f"${self.env}/{self.relpath}"

    @property
    def env(self) -> str:
        """Environment variable to save link under."""
        return "HOME"

    @property
    def root(self) -> _Path:
        return _Path(_e[self.env])


class _UserDataSymlink(_Symlink):
    @property
    def env(self) -> str:
        return "USER_DATA_DIR"


class _Dotfile(_File):
    def __repr__(self) -> str:
        return f"$DOTFILES/{self.relpath}"

    @property
    def root(self) -> _Path:
        return _Path(_e["DOTFILES"])

    @property
    def relpath(self) -> _Path:
        return _Path(_re.sub(r"^\.", "", str(super().relpath)))


class Matrix(_ABC):
    """File matrix and metadata.

    :param key: Pointer for this matrix.
    :param value: Actual file or directory for this matrix.
    """

    def __init__(self, key: str | _Path, value: str | _Path) -> None:
        self._key = (
            _UserDataSymlink(key)
            if _e["USER_DATA_DIR"]
            in str(_Path.home() / _Path(_os.path.expandvars(key)))
            else _Symlink(key)
        )
        self._value: _File = _Dotfile(value)

    @property
    def key(self) -> _Symlink:
        """The symlink pointing to this matrix."""
        return self._key

    @property
    def value(self) -> _File:
        """Path to the actual file or directory."""
        return self._value

    def is_child_of(self, other: Matrix) -> bool:
        """Check whether this is a child of a file matrix.

        :param other: Matrix to check against.
        :return: Boolean for whether this is the child of a matrix.
        """
        return (str(self.key.path).startswith(str(other.key.path))) or (
            str(self.value.path).startswith(str(other.key.path))
        )

    def is_linked_to(self, other: Matrix) -> bool:
        """Check whether this is linked a matrix instance.

        :param other: Matrix to check against.
        :return: Boolean for whether this is the child of a matrix.
        """
        return self.value.relpath == other.key.relpath

    @property
    def realsrc(self) -> Entry:
        """Location of the real source link in the repo."""
        return Entry(self.key.relpath, self.value.relpath)

    @property
    def linksrc(self) -> Entry:
        """Get a link object representing existing symlink."""
        value = _Path(_os.readlink(self.key.path))
        if not value.exists():
            raise FileNotFoundError(
                f"{value.absolute()} is a dangling symlink"
            )

        return Entry.new(value)

    def child(self, entry: Matrix) -> Entry:
        """Return child matrix from existing entry.

        :param entry: Existing parent of child.
        :return: New child `Entry` object.
        """
        relpath = _Path(_re.sub(r"^\.", "", str(entry.key.relpath)))
        if len(relpath.parts) > 1:
            while relpath.parts[0] != self.value.path.name:
                relpath = _Path(*entry.key.relpath.parts[1:])

        return Entry(entry.value.path, self.value.path.parent / relpath)


class Entry(Matrix):
    """Dotfile value and metadata."""

    @classmethod
    def new(cls, value: str | _Path) -> Entry:
        """Instantiate a new entry from pointer information.

        :param value: Source to construct the dotfile from.
        :return: New entry object.
        """
        return cls(value, _Path(value).name)

    @property
    def timestamped(self) -> Entry:
        """A timestamped `Entry` object."""
        return Entry(
            self.key.path,
            self.value.path.parent
            / "{}.{}".format(
                self.value.path.name,
                _hashlib.new(  # type: ignore
                    "md5",
                    _datetime.now().strftime("%Y%m%d%H%M%S").encode("utf-8"),
                    usedforsecurity=False,
                ).hexdigest(),
            ),
        )


class Custom(Matrix):
    """Link value and metadata.

    :param key: Pointer to this custom link.
    :param value: Actual custom link.
    """

    def __init__(self, key: str | _Path, value: str | _Path) -> None:
        super().__init__(key, value)
        self._value = _Symlink(value)


def matrix(key: str, value: str) -> Matrix:
    """Initialize a `Matrix` object.

    :param key: Config key representing the symlink.
    :param value: Config value representing the value of the symlink.
    :return: Instantiated `Matrix` object.
    """
    if value.startswith("$DOTFILES"):
        return Entry(key, value)

    return Custom(key, value)
