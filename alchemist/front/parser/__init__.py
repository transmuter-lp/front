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


class NonTerminal(ASTNode):  # pylint: disable=R0903
    @staticmethod
    def process_left_recursion(
        parent: Optional["NonTerminal"], parser: "Parser", path: "Terminal", nonterminal: "NonTerminal"
    ) -> tuple["NonTerminal", set["Terminal"]]:
        nextpaths: set["Terminal"] = set()
        recursive_path: set[type[NonTerminal]] = cast(set[type[NonTerminal]], nonterminal.recursive_path)
        nonterminal.recursive_path = None

        while True:
            if nextpaths | nonterminal.output_paths == nextpaths:
                break

            for prod in recursive_path:
                del parser.nonterminals[path, prod]

            nextpaths |= nonterminal.output_paths
            parser.nonterminals[path, nonterminal.__class__] = nonterminal
            parser.lexer.set_state(path)

            try:
                nonterminal = nonterminal.__class__(parent, parser)
            except CompilerError:
                break

        return nonterminal, nextpaths

    def __init__(self, parent: Optional["NonTerminal"], parser: "Parser") -> None:
        self.parent: NonTerminal | None = parent
        self.parser: Parser = parser
        self.output_paths: set["Terminal"] = set()
        self.input_path: "Terminal" = parser.lexer.get_state()
        self.recursive_path: set[type[NonTerminal]] | None = None

    def __left_recursive(self, paths: set["Terminal"], node: type["NonTerminal"]) -> bool:
        if self.input_path in paths and (self.input_path, node) not in self.parser.nonterminals:
            parent: NonTerminal | None = self
            recursive_path: set[type[NonTerminal]] = set()

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

    def _process_paths(self, paths: set["Terminal"], node: type[ASTNode]) -> set["Terminal"]:
        nextpaths: set["Terminal"] = set()
        state: "Terminal" = self.parser.lexer.get_state()

        if issubclass(node, NonTerminal):
            left_recursive: bool = self.__left_recursive(paths, node)

            for path in paths:
                if (path, node) not in self.parser.nonterminals:
                    if left_recursive and path is self.input_path:
                        continue

                    self.parser.lexer.set_state(path)

                    try:
                        nonterminal: NonTerminal = node(self, self.parser)

                        if nonterminal.recursive_path is not None:
                            nextpaths |= self.process_left_recursion(self, self.parser, path, nonterminal)[1]
                        else:
                            nextpaths |= nonterminal.output_paths
                            self.parser.nonterminals[path, node] = nonterminal
                    except CompilerSyntaxError:
                        self.parser.nonterminals[path, node] = None
                elif self.parser.nonterminals[path, node] is not None:
                    nextpaths |= cast(NonTerminal, self.parser.nonterminals[path, node]).output_paths
        else:  # Terminal
            for path in paths:
                self.parser.lexer.set_state(path)

                try:
                    assert isinstance(self.parser.lexer.next_token(), node)
                    nextpaths.add(self.parser.lexer.get_state())
                except (CompilerEOIError, AssertionError):
                    pass

        self.parser.lexer.set_state(state)

        if len(nextpaths) == 0:
            raise CompilerNoPathError(self)

        return nextpaths


class Parser:  # pylint: disable=R0903
    _start: type[NonTerminal] = NonTerminal

    def __init__(self, lexer: "Lexer") -> None:
        self.lexer: "Lexer" = lexer
        self.nonterminals: dict[tuple["Terminal", type[NonTerminal]], NonTerminal | None] = {}

    def parse(self) -> NonTerminal | None:
        path: "Terminal" = self.lexer.get_state()

        try:
            ast: NonTerminal = self._start(None, self)
        except CompilerError as error:
            print(error)
            return None

        if ast.recursive_path is not None:
            ast = NonTerminal.process_left_recursion(None, self, path, ast)[0]

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
    def __init__(self, nonterminal: NonTerminal, msg: str) -> None:
        super().__init__(nonterminal.parser.lexer.input, "Syntax Error", f"In {nonterminal.__class__.__name__}: {msg}")


class CompilerNoPathError(CompilerSyntaxError):
    def __init__(self, nonterminal: NonTerminal) -> None:
        super().__init__(nonterminal, "Could not find a parsing path.")


class CompilerNEOIError(CompilerSyntaxError):
    def __init__(self, nonterminal: NonTerminal) -> None:
        super().__init__(nonterminal, "Expected end of input.")
