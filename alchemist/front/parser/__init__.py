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

from .. import CompilerError
from ..lexer import CompilerEOIError

if TYPE_CHECKING:
    from ..lexer import Lexer, Terminal


class Production:  # pylint: disable=R0903
    _left_recursive: bool = True

    @staticmethod
    def process_left_recursion(
        parent: Optional["Production"], parser: "Parser", path: "Terminal", production: "Production"
    ) -> tuple["Production", set["Terminal"]]:
        nextpaths: set["Terminal"] = set()
        recursive_path: set[type[Production]] = cast(set[type[Production]], production.recursive_path)
        production.recursive_path = None

        while True:
            if nextpaths | production.output_paths == nextpaths:
                break

            for prod in recursive_path:
                del parser.productions[path, prod]

            nextpaths |= production.output_paths
            parser.productions[path, production.__class__] = production
            parser.lexer.set_state(path)

            try:
                production = production.__class__(parent, parser)
            except CompilerError:
                break

        return production, nextpaths

    def __init__(self, parent: Optional["Production"], parser: "Parser") -> None:
        self.parent: Production | None = parent
        self.parser: Parser = parser
        self.output_paths: set["Terminal"] = set()
        self.input_path: Optional["Terminal"] = parser.lexer.get_state()
        self.recursive_path: set[type[Production]] | None = None
        self._derive()
        self.parent = None
        self.input_path = None

    def __left_recursive(self, paths: set["Terminal"], node: type["Production"]) -> bool:
        if self.input_path in paths and (self.input_path, node) not in self.parser.productions:
            parent: Production | None = self
            recursive_path: set[type[Production]] = set()

            while parent is not None and parent.input_path is self.input_path:
                if parent.__class__ is node:
                    if parent.recursive_path is None:
                        parent.recursive_path = recursive_path
                    else:
                        parent.recursive_path |= recursive_path

                    return True

                recursive_path.add(parent.__class__)
                parent = parent.parent

        return False

    def _process_paths(self, paths: set["Terminal"], node: type["Terminal"] | type["Production"]) -> set["Terminal"]:
        nextpaths: set["Terminal"] = set()
        state: "Terminal" = self.parser.lexer.get_state()

        if issubclass(node, Production):
            left_recursive: bool = self._left_recursive and self.__left_recursive(paths, node)

            for path in paths:
                if (path, node) not in self.parser.productions:
                    if left_recursive and path is self.input_path:
                        continue

                    self.parser.lexer.set_state(path)

                    try:
                        production: Production = node(self, self.parser)

                        if production.recursive_path is not None:
                            nextpaths |= self.process_left_recursion(self, self.parser, path, production)[1]
                        else:
                            nextpaths |= production.output_paths
                            self.parser.productions[path, node] = production
                    except CompilerSyntaxError:
                        self.parser.productions[path, node] = None
                elif self.parser.productions[path, node] is not None:
                    nextpaths |= cast(Production, self.parser.productions[path, node]).output_paths
        else:  # Terminal
            for path in paths:
                self.parser.lexer.set_state(path)

                try:
                    token: "Terminal" = self.parser.lexer.next_token()
                    assert isinstance(token, node) if token.soft_match else token.__class__ is node
                    nextpaths.add(self.parser.lexer.get_state())
                except (CompilerEOIError, AssertionError):
                    pass

        self.parser.lexer.set_state(state)

        if len(nextpaths) == 0:
            raise CompilerNoPathError(self)

        return nextpaths

    def _derive(self) -> None:
        raise NotImplementedError()


class Parser:  # pylint: disable=R0903
    _start: type[Production] = Production

    def __init__(self, lexer: "Lexer") -> None:
        self.lexer: "Lexer" = lexer
        self.productions: dict[tuple["Terminal", type[Production]], Production | None] = {}

    def parse(self) -> Production | None:
        path: "Terminal" = self.lexer.get_state()

        try:
            ast: Production = self._start(None, self)
        except CompilerError as error:
            print(error)
            return None

        if ast.recursive_path is not None:
            ast = Production.process_left_recursion(None, self, path, ast)[0]

        output_path: "Terminal" | None = None

        for path in ast.output_paths:
            if path.end[0] == self.lexer.input.endpos:
                output_path = path
                break

        if output_path is None:
            print(CompilerNEOIError(ast))
            return None

        ast.output_paths = {output_path}
        return ast


class CompilerSyntaxError(CompilerError):
    def __init__(self, production: Production, msg: str) -> None:
        super().__init__(production.parser.lexer.input, "Syntax Error", f"In {production.__class__.__name__}: {msg}")


class CompilerNoPathError(CompilerSyntaxError):
    def __init__(self, production: Production) -> None:
        super().__init__(production, "Could not find a parsing path.")


class CompilerNEOIError(CompilerSyntaxError):
    def __init__(self, production: Production) -> None:
        super().__init__(production, "Expected end of input.")


class BreakException(Exception):
    pass
