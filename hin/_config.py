"""
hin._config
===========
"""
import os as _os
import typing as _t
from os import environ as _e
from pathlib import Path as _Path

from configobj import ConfigObj as _ConfigObj

from ._file import Matrix as _Matrix
from ._file import matrix as _matrix


class Config(_t.Dict[str, _Matrix]):
    """Dotfiles config object.

    Stores a mapping of dotfiles and their respective pointers.
    """

    def __init__(self) -> None:
        self._path = _Path(_e["DOTFILES"]) / "dotfiles.ini"
        self._obj = _ConfigObj(str(self._path))
        super().__init__({k: _matrix(k, v) for k, v in self._obj.items()})

    @property
    def path(self) -> _Path:
        """Path to config file."""
        return self._path

    @staticmethod
    def _key_proxy(item: str) -> str:
        item = str(_Path.home() / _os.path.expandvars(item))
        if _e["USER_DATA_DIR"] in item:
            return item.replace(f"{_e['USER_DATA_DIR']}/", "$USER_DATA_DIR/")

        return item.replace(f"{_Path.home()}/", "$HOME/")

    def __getitem__(self, item) -> _Matrix:
        return super().__getitem__(self._key_proxy(item))

    def write(self) -> None:
        """Write updated content to ini file."""
        self._obj.update({k: str(v.value) for k, v in self.items()})
        self._obj.write()

    def add(self, matrix: _Matrix) -> None:
        """Add and write dotfile to config.

        :param matrix: Dotfile object.
        """
        self[str(matrix.key)] = matrix
        self.write()

    def remove(self, matrix: _Matrix) -> None:
        """Remove and write dotfile from config.

        :param matrix: Dotfile object.
        """
        del self._obj[self._key_proxy(str(matrix.key))]
        del self[self._key_proxy(str(matrix.key))]
        self.write()

    def remove_links(self, matrix: _Matrix) -> None:
        """Remove links pointing to other matrix.

        :param matrix: Matrix object.
        """
        self.remove(matrix)
        for value in dict(self).values():
            if value.is_linked_to(matrix):
                self.remove_links(value)
