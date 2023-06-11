"""
hin._decorators
===============
"""
from __future__ import annotations

import functools as _functools
import inspect as _inspect
import os as _os
import typing as _t
from datetime import datetime as _datetime
from glob import glob as _glob
from os import environ as _e
from pathlib import Path as _Path
from types import TracebackType as _TracebackType

import git as _git
from rich.console import Console as _Console

from ._actions import Hist as _Hist
from ._config import Config as _Config

_Command = _t.Callable[..., _t.Optional[str]]


def config(func: _Command) -> _Command:
    """Instantiate config object.

    Decorated function will be passed the `Config` object as an
    argument.

    :param func: Function to wrap.
    :return: Wrapped function.
    """

    @_functools.wraps(func)
    def _wrapper(*args: _t.Any, **kwargs: _t.Any) -> None:
        func(_Config(), *args, **kwargs)

    return _wrapper


def hist(func: _Command) -> _Command:
    """Instantiate history object.

    Decorated function will be passed the `Hist` object as an argument.

    :param func: Function to wrap.
    :return: Wrapped function.
    """

    @_functools.wraps(func)
    def _wrapper(*args: _t.Any, **kwargs: _t.Any) -> None:
        func(_Hist(), *args, **kwargs)

    return _wrapper


def console(func: _Command) -> _Command:
    """Instantiate console object.

    Decorated function will be passed the `Hist` object as an argument.

    :param func: Function to wrap.
    :return: Wrapped function.
    """

    @_functools.wraps(func)
    def _wrapper(*args: _t.Any, **kwargs: _t.Any) -> None:
        out = _Console(soft_wrap=bool(_e.get("HIN_DEBUG") == "1"))
        func(out, *args, **kwargs)

    return _wrapper


def repository(func: _Command) -> _Command:
    """Instantiate dotfile repository object.

    Decorated function will be passed the `Repo` object as an argument,
    bound to the dotfile repository.

    If no dotfile repository exists then create one, and make an initial
    commit containing the first revision of the dotfiles.ini file and
    the dotfiles.json file.

    Stash all staged files prior to invoking the wrapped function, and
    pop the stash if there is one.

    :param func: Function to wrap.
    :return: Wrapped function.
    """

    class _Stash:
        def __init__(self, git: _git.Git) -> None:
            self._git = git
            self._stashed = False
            output = self._git.stash()
            if "No local changes to save" not in output:
                self._stashed = True

        def __enter__(self) -> _Stash:  # pylint: disable=undefined-variable
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: _TracebackType,
        ) -> None:
            if self._stashed:
                self._git.stash("pop")

    @_functools.wraps(func)
    @console
    @hist
    @config
    def _wrapper(
        config_: _Config,
        hist_: _Hist,
        out: _Console,
        *args: _t.Any,
        **kwargs: _t.Any,
    ) -> None:
        author = _git.Actor(_e["GIT_AUTHOR_NAME"], _e["GIT_AUTHOR_EMAIL"])
        path = _Path(_e["DOTFILES"])
        try:
            repo = _git.Repo(path)
        except (_git.InvalidGitRepositoryError, _git.NoSuchPathError):
            path.mkdir(exist_ok=True, parents=True)
            repo = _git.Repo.init(path)
            config_.path.touch()
            hist_.path.touch()
            repo.git.add(path)
            repo.index.commit("Initial commit", author=author)

        with _Stash(repo.git):
            if "repo" in _inspect.getfullargspec(func).args:
                kwargs["repo"] = repo

            message = func(*args, **kwargs)
            if message is not None:
                repo.git.add(path)
                commit = repo.index.commit(message, author=author)
                out.print(f"committed {commit.hexsha[:7]}")

    return _wrapper


def _oprint(out: _Console, string: str, quiet: bool = False) -> None:
    if not quiet:
        out.print(string)


def install(quiet: bool = False) -> _t.Callable[[_Command], _Command]:
    """Install a dotfile repo.

    :param quiet: Silence output.
    :return: Wrapped function.
    """

    class _Install:
        def __init__(self, out: _Console) -> None:
            self._out = out

        def __enter__(self) -> _Install:  # pylint: disable=undefined-variable
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: _TracebackType,
        ) -> None:
            # make sure config is read if function updates it
            config_ = _Config()
            for dotfile in config_.values():
                if dotfile.key.path.exists() and not (
                    dotfile.key.path.is_symlink()
                    and _os.readlink(dotfile.key.path)
                    == str(dotfile.value.path)
                ):
                    _oprint(
                        self._out,
                        f"[yellow bold]backed up[/yellow bold]"
                        f" {dotfile.key.path}\n",
                        quiet,
                    )
                    _os.rename(
                        dotfile.key.path,
                        dotfile.key.path.parent
                        / "{}.{}".format(
                            dotfile.key.path.name,
                            _datetime.now().strftime("%Y%m%d%H%M%S"),
                        ),
                    )
                while True:
                    try:
                        _os.symlink(dotfile.value.path, dotfile.key.path)
                        _oprint(
                            self._out,
                            f"[green bold]installed [/green bold]"
                            f" {dotfile.key.path}",
                            quiet,
                        )
                        break
                    except FileExistsError:
                        dotfile.key.path.unlink()
                    except FileNotFoundError:
                        dotfile.key.path.parent.mkdir(parents=True)

            # has a different result to just being part of first loop
            for dotfile in config_.values():
                assert (
                    dotfile.key.path.is_symlink() and dotfile.key.path.exists()
                ), f"{dotfile.key.path} failed"

    def _decorator(func: _Command) -> _Command:
        @_functools.wraps(func)
        @console
        def _wrapper(out: _Console, *args: _t.Any, **kwargs: _t.Any) -> None:
            with _Install(out):
                func(*args, **kwargs)

        return _wrapper

    return _decorator


def uninstall(quiet: bool = False) -> _t.Callable[[_Command], _Command]:
    """Uninstall a dotfile repo.

    :param quiet: Silence output.
    :return: Wrapped function.
    """

    def _decorator(func: _Command) -> _Command:
        @_functools.wraps(func)
        @console
        @config
        def _wrapper(
            config_: _Config, out: _Console, *args: _t.Any, **kwargs: _t.Any
        ) -> None:
            _oprint(out, "removed the following dotfiles:", quiet)
            for value in config_.values():
                if value.key.path.is_symlink():
                    _oprint(out, f"\t{value.key.path}", quiet)
                    value.key.path.unlink()

                for path in list(
                    _Path(i) for i in _glob(f"{value.key.path}.*")
                ):
                    _os.rename(path, value.key.path)

            func(*args, **kwargs)

        return _wrapper

    return _decorator
