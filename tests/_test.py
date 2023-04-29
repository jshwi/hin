"""
tests._test
===========
"""
# pylint: disable=too-many-arguments,too-many-lines
from __future__ import annotations

import os
import shutil
import typing as t
from pathlib import Path

import git
import pytest
from freezegun import freeze_time

import hin as d

from . import (
    ADD,
    APPDIRS_SYSTEM,
    APPLICATION_SUPPORT,
    CODE,
    COMMIT,
    DARWIN,
    DATETIME,
    DOTFILES,
    DOTFILESINI,
    DOTFILESJSON,
    GITIGNORE,
    GRANDPARENT,
    INSTALL,
    LIBRARY,
    LINK,
    P1,
    P2,
    P3,
    P4,
    PARENT,
    PUSH,
    REMOTE,
    REMOVE,
    SHARE,
    STATUS,
    UNDO,
    UNINSTALL,
    Command,
    FixtureCli,
    FixtureMakeTree,
    args,
)


def test_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ``hin.__version__``.

    :param monkeypatch: Mock patch environment and attributes.
    """
    version = "0.1.0"
    monkeypatch.setattr("hin.__version__", version)
    assert d.__version__ == version


@pytest.mark.parametrize("base", ["HOME", "USER_DATA_DIR"])
@pytest.mark.parametrize(
    "tree,commands,add,expected_file,expected_pointer,expected_file_type",
    [
        (
            {P1.dst: P1.contents},
            lambda x: ((d.main, [ADD, x]),),
            P1.dst,
            P1.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]),),
            P1.dst / P2.src,
            P2.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]),),
            P1.dst,
            P1.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_dir(),
        ),
        (
            {P1.dst: {P2.src: {P3.src: P3.contents}}},
            lambda x: ((d.main, [ADD, x]),),
            P1.dst / P2.src,
            P2.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_dir(),
        ),
        (
            {P1.dst: P1.contents},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO])),
            P1.dst,
            P1.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO])),
            P1.dst / P2.src,
            P2.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO])),
            P1.dst,
            P1.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_dir(),
        ),
        (
            {P1.dst: {P2.src: {P3.src: P3.contents}}},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO])),
            P1.dst / P2.src,
            P2.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_dir(),
        ),
        (
            {P1.dst: P1.contents},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO]), (d.main, [UNDO])),
            P1.dst,
            P1.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO]), (d.main, [UNDO])),
            P1.dst / P2.src,
            P2.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO]), (d.main, [UNDO])),
            P1.dst,
            P1.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_dir(),
        ),
        (
            {P1.dst: {P2.src: {P3.src: P3.contents}}},
            lambda x: ((d.main, [ADD, x]), (d.main, [UNDO]), (d.main, [UNDO])),
            P1.dst / P2.src,
            P2.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_dir(),
        ),
        (
            {P1.dst: P1.contents},
            lambda x: ((d.main, [ADD, x]), (d.main, [REMOVE, x])),
            P1.dst,
            P1.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]), (d.main, [REMOVE, x])),
            P1.dst / P2.src,
            P2.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: ((d.main, [ADD, x]), (d.main, [REMOVE, x])),
            P1.dst,
            P1.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_dir(),
        ),
        (
            {P1.dst: {P2.src: {P3.src: P3.contents}}},
            lambda x: ((d.main, [ADD, x]), (d.main, [REMOVE, x])),
            P1.dst / P2.src,
            P2.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_dir(),
        ),
        (
            {P1.dst: P1.contents},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
            ),
            P1.dst,
            P1.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
            ),
            P1.dst / P2.src,
            P2.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
            ),
            P1.dst,
            P1.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_dir(),
        ),
        (
            {P1.dst: {P2.src: {P3.src: P3.contents}}},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
            ),
            P1.dst / P2.src,
            P2.src,
            lambda x: x.is_symlink(),
            lambda x: x.is_dir(),
        ),
        (
            {P1.dst: P1.contents},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
            P1.dst,
            P1.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
            P1.dst / P2.src,
            P2.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_file(),
        ),
        (
            {P1.dst: {P2.src: P2.contents}},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
            P1.dst,
            P1.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_dir(),
        ),
        (
            {P1.dst: {P2.src: {P3.src: P3.contents}}},
            lambda x: (
                (d.main, [ADD, x]),
                (d.main, [REMOVE, x]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
            P1.dst / P2.src,
            P2.src,
            lambda x: not x.is_symlink(),
            lambda x: not x.is_dir(),
        ),
    ],
    ids=[
        "add-single-file",
        "add-nested-single-file",
        "add-single-dir",
        "add-nested-single-dir",
        "add-undo-single-file",
        "add-undo-nested-single-file",
        "add-undo-single-dir",
        "add-undo-nested-single-dir",
        "add-undo-undo-single-file",
        "add-undo-undo-nested-single-file",
        "add-undo-undo-single-dir",
        "add-undo-undo-nested-single-dir",
        "remove-single-file",
        "remove-nested-single-file",
        "remove-single-dir",
        "remove-nested-single-dir",
        "remove-undo-single-file",
        "remove-undo-nested-single-file",
        "remove-undo-single-dir",
        "remove-undo-nested-single-dir",
        "remove-undo-undo-single-file",
        "remove-undo-undo-nested-single-file",
        "remove-undo-undo-single-dir",
        "remove-undo-undo-nested-single-dir",
    ],
)
def test_add_remove(
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
    tree: dict[str, t.Any],
    base: str,
    commands: t.Callable[[Path], t.Tuple[Command, ...]],
    add: Path,
    expected_file: Path,
    expected_pointer: t.Callable[[Path], bool],
    expected_file_type: t.Callable[[Path], bool],
) -> None:
    """Test adding of dotfiles.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param tree: Filesystem to create
    :param base: Environment variable for base dir of dotfile.
    :param commands: Commands to run.
    :param add: File to add.
    :param expected_file: File expected in dotfiles.
    :param expected_pointer: State the pointer should be in.
    :param expected_file_type: File type expected in dotfiles.
    """
    base_dir = Path(os.environ[base])
    make_tree({base_dir: tree})
    cli(*commands(base_dir / add))
    assert expected_pointer(base_dir / add)
    assert expected_file_type(DOTFILES / expected_file)


@pytest.mark.parametrize(
    "tree,add,commands",
    [
        (
            {P2.src: P1.contents},
            P2.src,
            lambda x, y: ((d.main, [ADD, x]), (d.main, [ADD, y])),
        ),
        (
            {P2.src: {P3.src: P1.contents}},
            P2.src / P3.src,
            lambda x, y: ((d.main, [ADD, x]), (d.main, [ADD, y])),
        ),
        (
            {P2.src: {P3.src: {P4.src: P4.contents}}},
            P2.src / P3.src / P4.src,
            lambda x, y: ((d.main, [ADD, x]), (d.main, [ADD, y])),
        ),
        (
            {P2.src: P1.contents},
            P2.src,
            lambda x, y: (
                (d.main, [ADD, x]),
                (d.main, [ADD, y]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
        ),
        (
            {P2.src: {P3.src: P1.contents}},
            P2.src / P3.src,
            lambda x, y: (
                (d.main, [ADD, x]),
                (d.main, [ADD, y]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
        ),
        (
            {P2.src: {P3.src: {P4.src: P4.contents}}},
            P2.src / P3.src / P4.src,
            lambda x, y: (
                (d.main, [ADD, x]),
                (d.main, [ADD, y]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
        ),
    ],
    ids=[
        PARENT,
        GRANDPARENT,
        "great-grandparent",
        "undo-parent",
        "undo-grandparent",
        "undo-great-grandparent",
    ],
)
def test_add_parent_of_existing_dotfile(
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
    tree: dict[str, t.Any],
    add: str,
    commands: t.Callable[[Path, Path], t.Tuple[Command, ...]],
) -> None:
    """Test adding of dotfiles that are nested in a new dotfile.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param tree: Filesystem to create.
    :param add: File to add.
    :param commands: Commands to run.
    """
    parent = P1.dst
    child = parent / add
    make_tree({P1.dst: tree})
    cli(*commands(child, parent))
    assert parent.is_symlink()
    assert child.is_file()
    assert not child.is_symlink()
    git.Repo(DOTFILES).git.ls_files(P1.src / add, error_unmatch=True)


@pytest.mark.parametrize(
    "tree,add",
    [
        ({P2.src: P1.contents}, P2.src),
        ({P2.src: {P3.src: P1.contents}}, P2.src / P3.src),
    ],
    ids=[PARENT, GRANDPARENT],
)
def test_add_parent_of_existing_non_versioned_dotfile(
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
    tree: dict[str, t.Any],
    add: str,
) -> None:
    """Test ignoring un-versioned files nested in a new dotfile.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param tree: Filesystem to create.
    :param add: File to add.
    """
    make_tree({P1.dst: tree})
    cli((d.main, [ADD, P1.dst]))
    assert P1.dst.is_symlink()
    assert (P1.dst / add).is_file()
    assert not git.Repo(DOTFILES).git.ls_files(P1.src / add)


@pytest.mark.parametrize(
    "tree,add,assertion",
    [
        (
            {P1.src: {P2.src: P2.contents}},
            P1.src / P2.src,
            not (P1.dst / GITIGNORE).is_file(),
        ),
        (
            {P1.src: {P2.src: {P3.src: P3.contents}}},
            P1.src / P2.src / P3.src,
            not (P1.dst / P2.src / GITIGNORE).is_file()
            and not (P1.dst / GITIGNORE).is_file(),
        ),
        (
            {P1.src: {P2.src: {P3.src: {P4.src: P4.contents}}}},
            P1.src / P2.src / P3.src / P4.src,
            not (P1.dst / GITIGNORE).is_file()
            and not (P1.dst / P2.src / GITIGNORE).is_file()
            and not (P1.dst / P2.src / P3.dst / GITIGNORE).is_file(),
        ),
    ],
    ids=[PARENT, GRANDPARENT, "great-grandparent"],
)
def test_add_parent_of_existing_dotfile_undo_no_keep_gitignore(
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
    tree: dict[str, t.Any],
    add: str,
    assertion: bool,
) -> None:
    """Test undoing of dotfiles that are nested in a new dotfile.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param tree: Filesystem to create.
    :param add: File to add.
    :param assertion: Condition to check for.
    """
    make_tree({P1.dst: tree})
    cli(
        (d.main, [ADD, P1.dst / add]),
        (d.main, [ADD, P1.dst]),
        (d.main, [UNDO]),
    )
    assert assertion


def test_add_dirty_working_tree(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test creation of dotfile with dirty working tree.

    Test tree stashed before commit and stash popped after.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli((d.main, [ADD, P1.dst]))
    make_tree({P3.src: P3.contents}, DOTFILES)
    git.Repo(DOTFILES).git.add(DOTFILES.absolute())
    cli((d.main, [ADD, P2.dst]))


def test_install(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test install.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree(
        {
            P1.dst: P1.contents,
            P2.dst: {P2.src: P2.contents},
            P3.dst: {P2.src: P2.contents},
            P4.dst: {P4.src: {P4.src: P4.contents}},
        }
    )
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [ADD, P2.dst / P2.src]),
        (d.main, [ADD, P3.dst]),
        (d.main, [ADD, P4.dst / P4.src]),
    )
    os.remove(P1.dst)
    shutil.rmtree(P2.dst)
    os.remove(P3.dst)
    shutil.rmtree(P4.dst)
    cli((d.main, [INSTALL]))
    repo = git.Repo(DOTFILES)
    assert P1.dst.is_symlink()
    assert (P2.dst / P2.src).is_symlink()
    assert P3.dst.is_symlink()
    assert (P4.dst / P4.src).is_symlink()
    assert not repo.git.diff()


@freeze_time(DATETIME)
def test_install_backup(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test backing up of files when running install.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli((d.main, [ADD, P1.dst]), (d.main, [ADD, P2.dst]))
    os.remove(P1.dst)
    os.remove(P2.dst)
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli((d.main, [INSTALL]))
    expected_1 = P1.backup.read_text(encoding="utf-8")
    expected_2 = P2.backup.read_text(encoding="utf-8")
    assert expected_1 == P1.contents
    assert expected_2 == P2.contents


def test_install_broken_links(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test install still works when broken symlinks exist.

    Test broken symlinks removed and install successful anyway.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli(
        (d.main, [ADD, P1.dst]), (d.main, [ADD, P2.dst]), (d.main, [UNINSTALL])
    )
    os.symlink(P4.src, P1.dst)
    os.symlink(P3.src, P2.dst)
    cli((d.main, [INSTALL]))
    assert P1.dst.is_symlink()
    assert P2.dst.is_symlink()


@pytest.mark.parametrize(
    "commands,link_condition,file_condition",
    [
        (
            (
                (d.main, [ADD, P1.dst]),
                (d.main, [LINK, P2.dst, P1.dst]),
                (d.main, [LINK, P3.dst, P2.dst]),
                (d.main, [LINK, P4.dst, P3.dst]),
                (d.main, [REMOVE, P1.dst]),
            ),
            lambda: not all(i.is_symlink() for i in (P2.dst, P3.dst, P4.dst)),
            lambda: not P1.dst.is_symlink(),
        ),
        (
            (
                (d.main, [ADD, P1.dst]),
                (d.main, [LINK, P2.dst, P1.dst]),
                (d.main, [LINK, P3.dst, P2.dst]),
                (d.main, [LINK, P4.dst, P3.dst]),
                (d.main, [REMOVE, P1.dst]),
                (d.main, [UNDO]),
            ),
            lambda: all(i.is_symlink() for i in (P2.dst, P3.dst, P4.dst)),
            P1.dst.is_symlink,
        ),
        (
            (
                (d.main, [ADD, P1.dst]),
                (d.main, [LINK, P2.dst, P1.dst]),
                (d.main, [LINK, P3.dst, P2.dst]),
                (d.main, [LINK, P4.dst, P3.dst]),
                (d.main, [REMOVE, P1.dst]),
                (d.main, [UNDO]),
                (d.main, [UNDO]),
            ),
            lambda: not all(i.is_symlink() for i in (P2.dst, P3.dst, P4.dst)),
            lambda: not P1.dst.is_symlink(),
        ),
    ],
    ids=[
        "remove-with-links-to",
        "undo-remove-with-links-to",
        "undo-undo-remove-with-links-to",
    ],
)
def test_remove_with_links_to(
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
    commands: t.Tuple[Command, ...],
    link_condition: t.Callable[..., bool],
    file_condition: t.Callable[..., bool],
) -> None:
    """Test removing of dotfile that has links to itself and so on..

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param commands: Commands to run.
    :param link_condition: Boolean condition for links.
    :param file_condition: Boolean condition for file.
    """
    make_tree({P1.dst: {P1.src: P1.contents}})
    cli(*commands)
    assert link_condition()
    assert file_condition()


def test_has_docs(cli: FixtureCli) -> None:
    """Test for commands that may be wrapped with a decorator.

    :param cli: Cli runner for testing.
    """
    assert all(
        len(i.split(" ")) > 1
        for i in cli((d.main, [args.help]))
        .stdout.split("Commands:")[-1]
        .strip()
        .splitlines()
    )


def test_link(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test adding of custom link.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: {P2.src: P2.dst}})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [ADD, P2.dst]),
        (d.main, [LINK, P3.dst, P1.dst]),
    )
    os.remove(DOTFILES / P2.src / GITIGNORE)
    repo = git.Repo(DOTFILES)
    repo.git.add(DOTFILES.absolute())
    repo.git.commit(message="add nested file")
    cli((d.main, [LINK, P4.dst, P2.dst / P2.src]))
    assert P3.dst.is_symlink()
    assert P4.dst.is_symlink()


def test_link_undo(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test adding of custom link and then undoing it.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P1.src: P1.contents}})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst]),
        (d.main, [UNDO]),
    )
    assert not P2.dst.is_symlink()


def test_unlink(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test unlinking a custom link.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P1.src: P1.contents}})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst]),
        (d.main, [REMOVE, P2.dst]),
    )
    assert not P2.dst.is_symlink()


def test_uninstall(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test uninstall.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [ADD, P2.dst]),
        (d.main, [INSTALL]),
        (d.main, [UNINSTALL]),
    )
    repo = git.Repo(DOTFILES)
    assert not P1.dst.is_symlink()
    assert not P2.dst.is_symlink()
    assert not repo.git.diff()


def test_uninstall_put_back(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test uninstall, and put back backup if it exists.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli((d.main, [ADD, P1.dst]), (d.main, [ADD, P2.dst]))
    os.remove(P1.dst)
    os.remove(P2.dst)
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents})
    cli((d.main, [INSTALL]), (d.main, [UNINSTALL]))
    assert P2.dst.is_file()
    assert P2.dst.is_file()


@pytest.mark.parametrize(
    "file",
    [DOTFILESINI, DOTFILESJSON],
    ids=[DOTFILESINI.name, DOTFILESJSON.name],
)
def test_files(cli: FixtureCli, make_tree: FixtureMakeTree, file: str) -> None:
    """Test content that should and should not be in `dotfiles.*`.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param file: File to check.
    """
    make_tree({P1.dst: {P1.src: P1.contents}})
    cli((d.main, [ADD, P1.dst]), (d.main, [LINK, P2.dst, P1.dst]))
    contents = (DOTFILES / file).read_text(encoding="utf-8")
    assert str(Path.cwd()) not in contents
    assert str(DOTFILES) not in contents
    assert "$DOTFILES" in contents


def test_clone(cli: FixtureCli) -> None:
    """Test cloning a dotfiles repo.

    :param cli: Cli runner for testing.
    """
    remote_path = Path.cwd() / ".." / REMOTE
    repo = git.Repo.init(remote_path)
    (remote_path / P1.src).touch()
    repo.git.add(remote_path)
    repo.git.commit(message="Initial commit")
    cli((d.main, ["clone", remote_path, args.branch, "master"]))
    assert DOTFILES.is_dir()


def test_link_child(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test adding of custom link that's not yet versioned but can be.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.dst}})
    cli((d.main, [ADD, P1.dst]))
    assert not git.Repo(DOTFILES).git.ls_files(P1.src / P2.src)
    cli((d.main, [LINK, P3.dst, P1.dst / P2.src]))
    assert P3.dst.is_symlink()
    git.Repo(DOTFILES).git.ls_files(P1.src / P2.src, error_unmatch=True)


def test_link_grandchild(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test adding of custom link that's not yet versioned but can be.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: {P3.src: {P4.src: P4.contents}}}})
    cli((d.main, [ADD, P1.dst]))
    assert not git.Repo(DOTFILES).git.ls_files(
        P1.src / P2.src / P3.src / P4.src
    )
    cli((d.main, [LINK, P3.dst, P1.dst / P2.src / P3.src / P4.src]))
    assert P3.dst.is_symlink()
    git.Repo(DOTFILES).git.ls_files(
        P1.src / P2.src / P3.src / P4.src, error_unmatch=True
    )


def test_remove_gitignore(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test .gitignore removed after running remove..

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    assert (P1.dst / GITIGNORE).is_file()
    cli((d.main, [REMOVE, P1.dst]))
    assert not (P1.dst / GITIGNORE).is_file()


def test_git(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Run git command.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    assert (
        "nothing to commit, working tree clean"
        in cli((d.main, ["git", STATUS])).stdout
    )


def test_gitignore_root(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test .gitignore not created at root.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P2.contents})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst]),
        (d.main, [LINK, P3.dst, P2.dst]),
        (d.main, [LINK, P4.dst, P3.dst]),
    )
    assert not (DOTFILES / GITIGNORE).is_file()


def test_gitignore_single_dir(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test .gitignore not created at root.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    assert (DOTFILES / P1.src / GITIGNORE).is_file()


def test_link_home_gitignore(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test .gitignore not created at root with combination of links.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P1.dst / P2.src]),
        (d.main, [LINK, P3.dst, P2.dst]),
    )
    assert not GITIGNORE.is_file()


def test_install_on_file(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test everything installed right after error.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P2.contents})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P2.dst, P2.dst]),
        catch_exceptions=True,
    )
    assert P1.dst.is_symlink()


def test_add_symlink_src(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test adding of symlink source.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents})
    os.symlink(P1.dst, P2.dst)
    cli((d.main, [ADD, P2.dst]))
    assert P1.dst.is_symlink()
    assert P2.dst.is_symlink()
    assert P1.contents in P2.dst.read_text(encoding="utf-8")


def test_add_json_if_no_exist(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test hin won't fail if core file removed.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents})
    cli((d.main, [ADD, P1.dst]))
    cli((d.main, [REMOVE, P1.dst]))
    dotfiles_json = DOTFILES / DOTFILESJSON
    os.remove(dotfiles_json)
    repo = git.Repo(DOTFILES)
    repo.git.add(".")
    repo.git.commit(message=REMOVE)
    cli((d.main, [ADD, P1.dst]))


@freeze_time(DATETIME)
def test_backup_nested(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test backups sent to right location.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst / P2.src]), (d.main, [UNINSTALL]))
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [INSTALL]))
    assert not P2.nested_backup.is_file()
    assert (P1.dst / P2.nested_backup).is_file()


def test_link_absolute(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test linking absolute path.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [LINK, P3.src, (P1.dst / P2.src).absolute()]),
    )


def test_link_to_link_linked_to_symlink(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """This combination fails now too.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli(
        (d.main, [ADD, P1.dst / P2.src]),
        (d.main, [LINK, P3.dst, (P1.dst / P2.src)]),
        (d.main, [ADD, P1.dst]),
    )


def test_add_duplicate_file_name(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test file not overwritten if there is one of the same name.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: {P1.dst: P2.contents}})
    cli((d.main, [ADD, P1.dst]), (d.main, [ADD, P2.dst / P1.dst]))
    assert P1.dst.read_text(encoding="utf-8") == P1.contents
    assert (P2.dst / P1.dst).read_text(encoding="utf-8") == P2.contents


def test_add_duplicate_dir_name(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test process does not error if dir exists with same name.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree(
        {
            P1.dst: {P1.dst: P1.contents},
            P2.dst: {P1.dst: {P1.dst: P2.contents}},
        }
    )
    cli((d.main, [ADD, P1.dst]), (d.main, [ADD, P2.dst / P1.dst]))
    assert (P1.dst / P1.dst).read_text(encoding="utf-8") == P1.contents
    assert (P2.dst / P1.dst / P1.dst).read_text(
        encoding="utf-8"
    ) == P2.contents


def test_add_duplicate_dir_name_of_file(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test process passes if dir exists with same name as file.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P2.dst: {P1.dst: P1.contents}, P1.dst: P2.contents})
    cli((d.main, [ADD, P1.dst]), (d.main, [ADD, P2.dst / P1.dst]))
    assert (P2.dst / P1.dst).read_text(encoding="utf-8") == P1.contents
    assert P1.dst.read_text(encoding="utf-8") == P2.contents


def test_add_duplicate_file_name_of_dir(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test process passes if file exists with same name as dir.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P2.dst: {P1.dst: P1.contents}, P1.dst: P2.contents})
    cli((d.main, [ADD, P2.dst / P1.dst]), (d.main, [ADD, P1.dst]))
    assert (P2.dst / P1.dst).read_text(encoding="utf-8") == P1.contents
    assert P1.dst.read_text(encoding="utf-8") == P2.contents


@pytest.mark.parametrize(
    "setup",
    [
        (
            DARWIN,
            {LIBRARY: {APPLICATION_SUPPORT: {CODE: {P1.src: P1.contents}}}},
            Path(LIBRARY) / APPLICATION_SUPPORT / CODE,
        ),
        (
            "linux",
            {".local": {SHARE: {CODE: {P1.src: P1.contents}}}},
            Path(".local") / SHARE / CODE,
        ),
    ],
)
@pytest.mark.parametrize(
    INSTALL,
    [
        (DARWIN, Path(LIBRARY) / APPLICATION_SUPPORT / CODE),
        ("linux", Path(".local") / SHARE / CODE),
    ],
)
def test_install_cross_os(
    monkeypatch: pytest.MonkeyPatch,
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
    setup: t.Tuple[str, t.Dict[str, t.Any], Path],
    install: t.Tuple[str, Path],
) -> None:
    """Check add and install cross platform.

    :param monkeypatch: Mock patch environment and attributes.
    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    :param setup: Params for setup to install.
    :param install: Params for install from setup.
    """
    monkeypatch.setattr(APPDIRS_SYSTEM, setup[0])
    make_tree(setup[1])
    cli((d.main, [ADD, setup[2]]), (d.main, [UNINSTALL]))
    monkeypatch.setattr(APPDIRS_SYSTEM, install[0])
    cli((d.main, [INSTALL]))
    assert install[1].is_symlink()
    cli((d.main, [UNDO]))
    assert not install[1].is_symlink()
    assert install[1].is_dir()


def test_undo_data_dir(
    monkeypatch: pytest.MonkeyPatch,
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
) -> None:
    """Assert datadir saved the same on undo.

    :param monkeypatch: Mock patch environment and attributes.
    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    monkeypatch.setattr(APPDIRS_SYSTEM, DARWIN)
    make_tree({LIBRARY: {APPLICATION_SUPPORT: {CODE: {P1.src: P1.contents}}}})
    cli((d.main, [ADD, Path(LIBRARY) / APPLICATION_SUPPORT / CODE]))
    assert '"$HOME/Library/Application Support/Code"' not in (
        DOTFILES / DOTFILESJSON
    ).read_text(encoding="utf-8")
    cli((d.main, [UNDO]))
    assert '"$HOME/Library/Application Support/Code"' not in (
        DOTFILES / DOTFILESJSON
    ).read_text(encoding="utf-8")


def test_remove_no_gitignore(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test remove does not fail if .gitignore does not exist.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    (P1.dst / ".gitignore").unlink()
    repo = git.Repo(DOTFILES)
    repo.git.add(".")
    repo.git.commit(message="remove .gitignore")
    cli((d.main, [REMOVE, P1.dst]))


def test_git_no_origin(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test pushing with no remote set.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    result = cli((d.main, [PUSH]), catch_exceptions=True)
    assert "does not appear to be a git repository" in str(result.exc_info)


def test_git_push_valid(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test pushing to a valid remote.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    remote_path = Path.cwd() / ".." / REMOTE
    git.Repo.init(remote_path, bare=True)
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    result = cli((d.main, [PUSH, args.remote, remote_path]))
    assert "changes pushed to remote" in str(result.stdout)


def test_git_push_invalid(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test pushing to an invalid remote.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    result = cli((d.main, [PUSH, args.remote, REMOTE]), catch_exceptions=True)
    assert "make sure you have the correct access" in str(result.exc_info)


def test_git_status(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test running status on dotfile.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    (P1.dst / GITIGNORE).unlink()
    (P1.dst / P3.src).touch()
    result = cli((d.main, [STATUS, args.file, P1.dst]))
    assert "Changes not staged for commit" in result.stdout
    assert "Untracked files" in result.stdout
    assert ".file_1" in result.stdout
    assert ".file_1" in result.stdout


def test_git_status_no_change(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test running status on dotfile with no changes.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    result = cli((d.main, [STATUS, args.file, P1.dst]))
    assert "no changes have been made to" in result.stdout


def test_commit(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test running commit on dotfile.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    (P1.dst / GITIGNORE).unlink()
    (P1.dst / P3.src).touch()
    result = cli((d.main, [COMMIT, P1.dst]))
    assert "committed" in result.stdout


def test_nothing_to_commit(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test running commit on dotfile.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    result = cli((d.main, [COMMIT, P1.dst]))
    assert "nothing to commit" in result.stdout


def test_ref_key_in_path(
    monkeypatch: pytest.MonkeyPatch,
    cli: FixtureCli,
    make_tree: FixtureMakeTree,
) -> None:
    """Test no `KeyError` raised.

    No need to run any assertions.

    :param monkeypatch: Mock patch environment and attributes.
    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    some_path = Path.cwd() / "some" / "nested" / "path"
    some_path.mkdir(parents=True)
    make_tree({P1.dst: {P2.src: P2.contents}})
    cli((d.main, [ADD, P1.dst]))
    monkeypatch.chdir(some_path)
    cli((d.main, ["status", args.file, P1.dst]))


def test_list(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test listing dotfiles.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents, P2.dst: P2.contents, P3.dst: P3.contents})
    result = cli(
        (d.main, [ADD, P1.dst]),
        (d.main, [ADD, P2.dst]),
        (d.main, [ADD, P3.dst]),
        (d.main, [LINK, P4.dst, P3.dst]),
        (d.main, ["list"]),
    )
    assert str(P1.dst) in result.stdout
    assert str(P2.dst) in result.stdout
    assert str(P3.dst) in result.stdout
    assert str(P4.dst) in result.stdout


def test_fail_if_not_exist(cli: FixtureCli) -> None:
    """Must fail if adding file that does not exist.

    :param cli: Cli runner for testing.
    """
    result = cli((d.main, [ADD, P1.dst]), catch_exceptions=True)
    assert isinstance(result.exception, FileNotFoundError)


def test_add_child(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test adding of child that's not yet versioned.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.dst}})
    cli((d.main, [ADD, P1.dst]))
    assert not git.Repo(DOTFILES).git.ls_files(P1.src / P2.src)
    cli((d.main, [ADD, P1.dst / P2.src]))
    git.Repo(DOTFILES).git.ls_files(P1.src / P2.src, error_unmatch=True)


def test_commit_nested(cli: FixtureCli, make_tree: FixtureMakeTree) -> None:
    """Test running commit on dotfile that is not a saved key.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: {P2.src: P2.contents}})
    nested = P1.dst / P2.src
    cli((d.main, [ADD, P1.dst]), (d.main, [ADD, nested]))
    nested.write_text("something")
    result = cli((d.main, [COMMIT, nested]))
    assert "committed" in result.stdout


def test_link_not_to_symlink(
    cli: FixtureCli, make_tree: FixtureMakeTree
) -> None:
    """Test adding of custom link that is not a symlink.

    :param cli: Cli runner for testing.
    :param make_tree: Make file tree.
    """
    make_tree({P1.dst: P1.contents})
    result = cli((d.main, [LINK, P2.dst, P1.dst]))
    assert "added" in result.stdout
    assert str(P1.dst) in result.stdout
    assert "linked" in result.stdout
    assert str(P2.dst) in result.stdout
