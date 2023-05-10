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
from ..lexer import CompilerEOIError

if TYPE_CHECKING:
    from ..lexer import Lexer, Terminal


class Production(ASTNode):  # pylint: disable=R0903
    def __init__(
        self, parent: Optional["Production"], parser: "Parser"
    ) -> None:
        super().__init__(parent)
        self.parser: Parser = parser
        self.output_paths: set["Terminal"] = set()
        self.input_path: "Terminal" = parser.lexer.get_state()

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
                        nextpaths |= production.output_paths
                        self.parser.productions[path, node] = production
                    except CompilerSyntaxError:
                        self.parser.productions[path, node] = None
                elif self.parser.productions[path, node] is not None:
                    nextpaths |= cast(
                        Production, self.parser.productions[path, node]
                    ).output_paths
        else:  # Terminal
            for path in paths:
                self.parser.lexer.set_state(path)

                try:
                    assert isinstance(self.parser.lexer.next_token(self), node)
                    nextpaths.add(self.parser.lexer.get_state())
                except (CompilerEOIError, AssertionError):
                    pass

        self.parser.lexer.set_state(state)

        if len(nextpaths) == 0:
            raise CompilerNoPathError(self)

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
            ast: Production = self._start(None, self)
            paths: list[Terminal] = list(ast.output_paths)
            i: int = 0

            while i < len(paths):
                if paths[i].state[0] != self.lexer.input.endpos:
                    paths = paths[:i] + paths[i + 1:]
                else:
                    i += 1

            if len(paths) == 0:
                raise CompilerNEOIError(ast)

            ast.output_paths = set(paths)
            return ast
        except CompilerError as error:
            print(error)
            return None


class CompilerSyntaxError(CompilerError):
    def __init__(self, production: Production, msg: str) -> None:
        super().__init__(
            production.parser.lexer.input,
            "Syntax Error",
            f"In {production.__class__.__name__}: {msg}"
        )


class CompilerNoPathError(CompilerSyntaxError):
    def __init__(self, production: Production) -> None:
        super().__init__(production, "Could not find a parsing path.")


class CompilerNEOIError(CompilerSyntaxError):
    def __init__(self, production: Production) -> None:
        super().__init__(production, "Expected end of input.")
