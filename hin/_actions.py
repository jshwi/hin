"""
hin._actions
============
"""
from __future__ import annotations

import json as _json
import shutil as _shutil
import typing as _t
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from os import environ as _e
from pathlib import Path as _Path

import git as _git

from ._file import Entry as _Entry
from ._file import Matrix as _Matrix


class _ActionDict(_t.TypedDict):
    action: str
    path: str
    other_path: str
    undo: bool


class Hist(_t.Dict[str, _t.List[_ActionDict]]):
    """History object.

    Dict like object which can serialise and write an `_Action` subclass
    as JSON, and read an `_Action` subclass back into an object.
    """

    _do = "do"
    _undo = "undo"

    def __init__(self) -> None:
        self._actions = {i.__name__: i for i in _Action.__subclasses__()}
        self._path = _Path(_e["DOTFILES"]) / "dotfiles.json"
        if self.path.exists():
            try:
                super().__init__(
                    _json.loads(self._path.read_text(encoding="utf-8"))
                )
            except _json.JSONDecodeError:
                pass

    @property
    def path(self) -> _Path:
        """Path to history file."""
        return self._path

    def add(
        self, commit: str, instance: _Action, func: _t.Callable[..., None]
    ) -> None:
        """Write a new `ActionDict` object to JSON.

        :param commit: The commit to add to.
        :param instance: Action object.
        :param func: Action function.
        """
        self[commit] = self.get(commit, [])
        self[commit].append(
            _ActionDict(
                action=instance.__class__.__name__,
                path=str(instance.entry.value),
                other_path=str(instance.entry.key),
                undo=func.__name__ == self._undo,
            )
        )
        self._path.write_text(_json.dumps(self, indent=2), encoding="utf-8")

    def run(self, commit: str) -> None:
        """Run undo for commit.

        Construct inverse methods from the classes that performed
        previous actions.

        :param commit: The commit to run from.
        """
        for obj in reversed(self[commit]):
            entry = _Entry(obj["other_path"], obj["path"])
            action = self._actions[obj["action"]](entry)  # type: ignore
            getattr(action, self._do if obj["undo"] else self._undo)()


class _Action(_ABC):
    def __init__(self, entry: _Entry) -> None:
        self._entry = entry
        self._commit = _git.Repo(_e["DOTFILES"]).head.commit.hexsha[:7]
        self._hist = Hist()

    @property
    def entry(self) -> _Matrix:
        """Associated `Matrix` object."""
        return self._entry

    @_abstractmethod
    def _do(self) -> None:
        """Do action."""

    @_abstractmethod
    def _undo(self) -> None:
        """Undo action."""

    def do(self) -> None:
        """Do action and record."""
        self._do()
        self._hist.add(self._commit, self, self.do)

    def undo(self) -> None:
        """Undo action and record."""
        self._undo()
        self._hist.add(self._commit, self, self.undo)


class Move(_Action):
    """Move a file or directory."""

    def _do(self) -> None:
        _shutil.move(str(self.entry.key.path), self.entry.value.path)

    def _undo(self) -> None:
        _shutil.move(str(self.entry.value.path), self.entry.key.path)
