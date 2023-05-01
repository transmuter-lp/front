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

from typing import Optional

from .. import ASTNode, CompilerError

class Production(ASTNode):
    def __init__(self, parent: Optional["Production"], lexer: "Lexer"):
        super().__init__(parent)
        self.lexer: "Lexer" = lexer

    def process_paths(self, paths: set["Terminal"], node: type[ASTNode]) -> set["Terminal"]:
        nextpaths = set()
        state = self.lexer.get_state()

        for p in paths:
            self.lexer.set_state(p)

            if issubclass(node, Production):
                try:
                    nextpaths |= node(self, self.lexer).paths
                except CompilerSyntaxError: pass
            else: # Terminal
                try:
                    assert isinstance(self.lexer.next_token(self), node)
                    nextpaths.add(self.lexer.get_state())
                except AssertionError: pass

        self.lexer.set_state(state)

        if len(nextpaths) == 0:
            raise CompilerSyntaxError()

        return nextpaths

class CompilerSyntaxError(CompilerError):
    def __init__(self): pass
