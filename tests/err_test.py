"""
tests._test
===========
"""
# pylint: disable=too-many-arguments
from __future__ import annotations

import os

import hin as d

from . import ADD, ALREADY_ADDED, LINK, P1, P2, P3, FixtureCli, FixtureMakeTree


def test_adding_of_already_added(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test error raised when adding an already added symlink.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P1.src: P1.contents}})
    result = cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst]),
        (d.main, [ADD, P2.dst]),
        catch_exceptions=True,
    )
    assert isinstance(result.exception, TypeError)
    assert ALREADY_ADDED in str(result.exc_info)


def test_adding_of_already_added_link(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test error raised when adding an already added linked symlink.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P1.src: P1.contents}})
    result = cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst]),
        catch_exceptions=True,
    )
    assert isinstance(result.exception, TypeError)
    assert ALREADY_ADDED in str(result.exc_info)


def test_adding_of_dangling_symlink(cli: FixtureCli) -> None:
    """Test error raised when adding a dangling symlink.

    :param cli: Cli runner for testing.
    """
    os.symlink(P1.dst, P2.dst)
    result = cli((d.main, [ADD, P2.dst]), catch_exceptions=True)
    assert isinstance(result.exception, FileNotFoundError)
    assert "dangling symlink" in str(result.exc_info)


def test_add_nested_symlink(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test error raised when adding not ValueError.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: {P3.src: P3.contents}}})
    result = cli(
        (d.main, [ADD, P1.dst / P2.src / P3.src]),
        (d.main, [ADD, P1.dst / P2.src / P3.src]),
        catch_exceptions=True,
    )
    assert isinstance(result.exception, TypeError)
    assert ALREADY_ADDED in str(result.exc_info)


def test_child_does_not_exist(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test linking to non-existing child.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    result = cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P3.src, (P1.dst / P3.src).absolute()]),
        catch_exceptions=True,
    )
    assert "link not related to a symlink" in str(result.exception)
    assert "or parent of a symlink in dotfile repo" in str(result.exception)


def test_no_debug_err(cli: FixtureCli) -> None:
    """Get coverage on error message as debug turned on for tests.

    :param cli: Cli runner for testing.
    """
    os.environ["HIN_DEBUG"] = "0"
    result = cli((d.main, [ADD, P1.dst]), catch_exceptions=True)
    assert isinstance(result.exception, FileNotFoundError)
