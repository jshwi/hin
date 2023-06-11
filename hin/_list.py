"""
hin._list
=========
"""
from rich.console import Console as _Console

from . import _decorators
from ._config import Config as _Config
from ._file import Custom as _Custom


@_decorators.console
@_decorators.config
def list_(config: _Config, out: _Console) -> None:
    """List all versioned dotfiles.

    \f

    :param config: Dotfiles config.
    :param out: Console object.
    """
    for matrix in config.values():
        kind = "[green bold]+[/green bold]"
        value = str(matrix.key.path)
        if isinstance(matrix, _Custom):
            kind = "[cyan bold]=[/cyan bold]"
            value += f" -> {matrix.value.path}"

        out.print(kind, value)
