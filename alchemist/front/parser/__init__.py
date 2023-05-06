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

from typing import Optional, cast, TYPE_CHECKING

from .. import ASTNode, CompilerError
from ..lexer import CompilerNEOIError

if TYPE_CHECKING:
    from ..lexer import Lexer, Terminal


class Production(ASTNode):  # pylint: disable=R0903
    def __init__(
        self, parent: Optional["Production"], parser: "Parser"
    ) -> None:
        super().__init__(parent)
        self.parser: Parser = parser
        self.paths: set["Terminal"] = set()

    def _process_paths(
        self, paths: set["Terminal"], node: type[ASTNode]
    ) -> set["Terminal"]:
        nextpaths: set["Terminal"] = set()
        state: "Terminal" = self.parser.lexer.get_state()

        if issubclass(node, Production):
            for path in paths:
                self.parser.lexer.set_state(path)

                if (path, node) not in self.parser.productions:
                    try:
                        production: Production = node(self, self.parser)
                        nextpaths |= production.paths
                        self.parser.productions[path, node] = production
                    except CompilerSyntaxError:
                        self.parser.productions[path, node] = None
                elif self.parser.productions[path, node] is not None:
                    nextpaths |= cast(
                        Production, self.parser.productions[path, node]
                    ).paths
        else:  # Terminal
            for path in paths:
                self.parser.lexer.set_state(path)

                try:
                    assert isinstance(self.parser.lexer.next_token(self), node)
                    nextpaths.add(self.parser.lexer.get_state())
                except AssertionError:
                    pass

        self.parser.lexer.set_state(state)

        if len(nextpaths) == 0:
            raise CompilerSyntaxError(self)

        return nextpaths


class Parser:  # pylint: disable=R0903
    _start: type[Production] = Production

    def __init__(self, lexer: "Lexer") -> None:
        self.lexer: "Lexer" = lexer
        self.productions: dict[
            tuple[Terminal, type[Production]], Production | None
        ] = {}

    def parse(self) -> Production | None:
        try:
            ast = self._start(None, self)

            for path in ast.paths:
                if path.state[0] != self.lexer.input.endpos:
                    self.lexer.set_state(path)
                    raise CompilerNEOIError(self.lexer.input)

            return ast
        except CompilerError as error:
            print(error)
            return None


class CompilerSyntaxError(CompilerError):
    def __init__(self, production: Production) -> None:
        super().__init__(
            production.parser.lexer.input,
            f"In {production.__class__.__name__}: "
            "Could not find a parsing path."
        )
