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

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .lexer import InputHandler


class ASTNode:
    keep: bool = True

    def __init__(self, parent: Optional["ASTNode"]):
        self.parent: Optional[ASTNode] = parent


class CompilerError(Exception):
    def __init__(self, _input: "InputHandler", msg: str):
        super().__init__(f"{_input.filename}:{_input.lc[0]}:{_input.lc[1]}: "
                         f"{self.__class__.__name__}: {msg}")
