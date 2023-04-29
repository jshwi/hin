"""
tests.conftest
==============
"""
# pylint: disable=too-many-arguments
from __future__ import annotations

import typing as t
from pathlib import Path

import pytest
from click.testing import CliRunner, Result

from . import APPDIRS_SYSTEM, DOTFILES, SHARE, Command, FixtureMakeTree


@pytest.fixture(name="environment", autouse=True)
def fixture_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prepare environment for testing.

    :param tmp_path: Create and return temporary directory for testing.
    :param monkeypatch: Mock patch environment and attributes.
    """
    home = tmp_path / "home" / "user"
    home.mkdir(parents=True)
    monkeypatch.setattr(APPDIRS_SYSTEM, "linux")  # set test os
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USER_DATA_DIR", str(home / ".local" / SHARE))
    monkeypatch.setenv("DOTFILES", str(home / DOTFILES))
    monkeypatch.setenv("HIN_DEBUG", "1")
    monkeypatch.chdir(home)
    (home / ".gitconfig").write_text(
        "[user]\nname = user\nemail = user@email.com\n"
    )


@pytest.fixture(name="make_tree")
def fixture_make_tree() -> FixtureMakeTree:
    """Recursively create directory tree from dict mapping.

    :return: Function for using this fixture.
    """

    def _make_tree(obj: dict[t.Any, t.Any], root: Path | None = None) -> None:
        path = root or Path.cwd()
        path.mkdir(exist_ok=True, parents=True)
        for key, value in obj.items():
            fullpath = path / key
            if isinstance(value, dict):
                fullpath.mkdir(exist_ok=True, parents=True)
                _make_tree(value, fullpath)
            else:
                fullpath.write_text(str(value))

    return _make_tree


@pytest.fixture(name="cli")
def fixture_cli() -> t.Callable[..., Result]:
    """Cli runner for testing.

    :return: Function for using this fixture.
    """

    runner = CliRunner()

    def _cli(*commands: Command, catch_exceptions: bool = False) -> Result:
        mut_commands = list(commands)
        command = mut_commands.pop(0)
        result = runner.invoke(
            command[0],  # type: ignore
            [str(i) for i in command[1]],
            catch_exceptions=catch_exceptions,
        )
        for command in mut_commands:
            result = runner.invoke(
                command[0],  # type: ignore
                [str(i) for i in command[1]],
                catch_exceptions=catch_exceptions,
            )

        return result

    return _cli
