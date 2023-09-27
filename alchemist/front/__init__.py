# This file is part of the Alchemist front-end libraries
# Copyright (C) 2023  Natan Junges <natanajunges@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Base classes commonly used by subpackages and modules.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lexer import InputHandler
    from .parser import Production


class TreeNode(ABC):  # pylint: disable=too-few-public-methods
    """
    Base node for dynamically building CSTs and ASTs.

    It supports the visitor pattern implemented by
    :class:`TreeVisitor`.
    """

    _keep: bool = True
    """
    Whether the node should be kept as the parent's child when building
    an AST.
    """

    @abstractmethod
    def accept(self, visitor: "TreeVisitor", top_down: bool = True, left_to_right: bool = True) -> None:
        """
        Accept the given tree ``visitor``.

        Call one of ``visitor``'s ``visit_*`` methods on itself and
        traverse its children as specified by ``top_down`` and
        ``left_to_right``.

        :param visitor: Tree visitor used to visit the node tree.
        :param top_down: Vertical order of traversal. ``True`` is
            top-down, and ``False`` is bottom-up.
        :param left_to_right: Horizontal order of traversal. ``True``
            is left-to-right, and ``False`` is right-to-left.
        """

    def _process_parent(self, parent: "Production.NonTerminal") -> None:
        """
        Process parent node when building the syntax tree.

        Must be overridden by subclasses as needed.

        :param parent: Parent node to be processed.
        """


class TreeVisitor:
    """
    Base visitor for :class:`TreeNode`s.
    """

    def visit_top_down_left_to_right(self, node: TreeNode) -> None:
        """
        Visit the given ``node``, top-down and left-to-right.

        Must be overridden by subclasses as needed.

        :param node: Node to visit.
        """

    def visit_top_down_right_to_left(self, node: TreeNode) -> None:
        """
        Visit the given ``node``, top-down and right-to-left.

        Must be overridden by subclasses as needed.

        :param node: Node to visit.
        """

    def visit_bottom_up_left_to_right(self, node: TreeNode) -> None:
        """
        Visit the given ``node``, bottom-up and left-to-right.

        Must be overridden by subclasses as needed.

        :param node: Node to visit.
        """

    def visit_bottom_up_right_to_left(self, node: TreeNode) -> None:
        """
        Visit the given ``node``, bottom-up and right-to-left.

        Must be overridden by subclasses as needed.

        :param node: Node to visit.
        """


class CompilerError(Exception):
    """
    Base exception for all compiler errors.
    """

    def __init__(self, _input: "InputHandler", error: str, msg: str) -> None:
        """
        :param _input: Input handler used to provide context.
        :param error: Brief description of the error.
        :param msg: Detailed message describing the error.
        """
        super().__init__(f"{_input.filename}:{_input.poslc[0]}:{_input.poslc[1]}: {error}: {msg}")
