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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lexer import InputHandler
    from .parser import Production


class TreeNode:  # pylint: disable=too-few-public-methods
    _keep: bool = True

    def accept(self, visitor: "TreeVisitor", top_down: bool = True, left_to_right: bool = True) -> None:
        raise NotImplementedError()

    def _process_parent(self, parent: "Production.NonTerminal") -> None:
        pass


class TreeVisitor:
    def visit_top_down_left_to_right(self, node: TreeNode) -> None:
        pass

    def visit_top_down_right_to_left(self, node: TreeNode) -> None:
        pass

    def visit_bottom_up_left_to_right(self, node: TreeNode) -> None:
        pass

    def visit_bottom_up_right_to_left(self, node: TreeNode) -> None:
        pass


class CompilerError(Exception):
    def __init__(self, _input: "InputHandler", error: str, msg: str) -> None:
        super().__init__(f"{_input.filename}:{_input.poslc[0]}:{_input.poslc[1]}: {error}: {msg}")
