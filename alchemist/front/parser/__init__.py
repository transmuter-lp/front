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

from typing import cast, TYPE_CHECKING

from .. import CompilerError
from ..lexer import CompilerEOIError

if TYPE_CHECKING:
    from ..lexer import Lexer, Terminal

Paths = dict["Terminal", set["GraphNode"]]


class GraphNode:
    @staticmethod
    def __merge_sets(set1: set["GraphNode"], set2: set["GraphNode"]) -> None:
        for node2 in set2:
            if node2 in set1:
                for node1 in set1:
                    if node2 == node1:
                        if node2 is not node1:
                            GraphNode.__merge_sets(node1.previous, node2.previous)
                            GraphNode.__merge_sets(node1.next, node2.next)

                        break
            else:
                set1.add(node2)

    @staticmethod
    def merge_paths(paths1: Paths, paths2: Paths) -> None:
        for path in paths2:
            if path in paths1:
                GraphNode.__merge_sets(paths1[path], paths2[path])
            else:
                paths1[path] = paths2[path]

    @staticmethod
    def from_token(token: "Terminal") -> Paths:
        return {token: {GraphNode(token, token)}}

    @staticmethod
    def from_production(production: "Production") -> Paths:
        return {path: {GraphNode(path, production)} for path in production.output_paths}

    @staticmethod
    def add_next(previous: set["GraphNode"], _next: Paths) -> None:
        for path in _next:
            for node in _next[path]:
                GraphNode.__merge_sets(node.previous, previous)

            for node in previous:
                GraphNode.__merge_sets(node.next, _next[path])

    def __init__(self, path: "Terminal", value: "Terminal | Production") -> None:
        self.path: "Terminal | None" = path
        self.value: "Terminal | Production" = value
        self.previous: set[GraphNode] = set()
        self.next: set[GraphNode] = set()
        self.visited = False

    def __eq__(self, other) -> bool:
        return isinstance(other, GraphNode) and self.path is other.path and self.value is other.value

    def __hash__(self) -> int:
        return hash((self.path, self.value))

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit(self)

        if isinstance(self.value, Production):
            self.value.accept(visitor)

    def accept_reverse(self, visitor: "Visitor") -> None:
        visitor.visit_reverse(self)

        if isinstance(self.value, Production) and self.path is not None:
            self.value.accept_reverse(visitor, self.path)


class Visitor:
    def visit(self, node: GraphNode) -> None:
        raise NotImplementedError()

    def visit_reverse(self, node: GraphNode) -> None:
        pass


class Production:
    _left_recursive: bool = True

    @staticmethod
    def process_left_recursion(
        parent: "Production | None", parser: "Parser", path: "Terminal", production: "Production"
    ) -> tuple["Production", Paths]:
        nextpaths: Paths = {}
        recursive_path: set[type[Production]] = cast(set[type[Production]], production.recursive_path)
        production.recursive_path = None

        while True:
            if nextpaths.keys() | production.output_paths.keys() == nextpaths.keys():
                break

            for prod in recursive_path:
                del parser.productions[path, prod]

            output_paths: Paths = GraphNode.from_production(production)
            GraphNode.merge_paths(nextpaths, output_paths)
            parser.productions[path, production.__class__] = production
            parser.lexer.set_state(path)

            try:
                production = production.__class__(parent, parser)
            except CompilerError:
                break

        return production, nextpaths

    def __init__(self, parent: "Production | None", parser: "Parser") -> None:
        self.parent: Production | None = parent
        self.parser: Parser = parser
        self.output_paths: Paths = {}
        state: "Terminal" = parser.lexer.get_state()
        self.input_path: GraphNode | None = GraphNode(state, state)
        self.recursive_path: set[type[Production]] | None = None
        self.children: set[GraphNode] = set()
        self._derive()
        self.children = self.input_path.next

        for child in self.children:
            child.previous.clear()

        self.parent = None
        self.input_path = None

    def __left_recursive(self, paths: Paths, production: type["Production"]) -> bool:
        input_path = cast(GraphNode, self.input_path)
        if input_path.path in paths and (input_path.path, production) not in self.parser.productions:
            parent: Production | None = self
            recursive_path: set[type[Production]] = set()

            while parent is not None and parent.input_path == self.input_path:
                if parent.__class__ is production:
                    if parent.recursive_path is None:
                        parent.recursive_path = recursive_path
                    else:
                        parent.recursive_path |= recursive_path

                    return True

                recursive_path.add(parent.__class__)
                parent = parent.parent

        return False

    def _process_paths(self, paths: Paths, symbol: type["Terminal"] | type["Production"]) -> Paths:
        nextpaths: Paths = {}
        state: "Terminal" = self.parser.lexer.get_state()
        output_paths: Paths

        if issubclass(symbol, Production):
            left_recursive: bool = self._left_recursive and self.__left_recursive(paths, symbol)

            for path in paths:
                if (path, symbol) not in self.parser.productions:
                    if left_recursive and path == self.input_path:
                        continue

                    self.parser.lexer.set_state(path)

                    try:
                        production: Production = symbol(self, self.parser)

                        if production.recursive_path is not None:
                            output_paths = self.process_left_recursion(self, self.parser, path, production)[1]
                            GraphNode.add_next(paths[path], output_paths)
                            GraphNode.merge_paths(nextpaths, output_paths)
                        else:
                            output_paths = GraphNode.from_production(production)
                            GraphNode.add_next(paths[path], output_paths)
                            GraphNode.merge_paths(nextpaths, output_paths)
                            self.parser.productions[path, symbol] = production
                    except CompilerSyntaxError:
                        self.parser.productions[path, symbol] = None
                elif self.parser.productions[path, symbol] is not None:
                    output_paths = GraphNode.from_production(cast(Production, self.parser.productions[path, symbol]))
                    GraphNode.add_next(paths[path], output_paths)
                    GraphNode.merge_paths(nextpaths, output_paths)
        else:  # Terminal
            for path in paths:
                self.parser.lexer.set_state(path)

                try:
                    token: "Terminal" = self.parser.lexer.next_token()
                    assert isinstance(token, symbol) if token.soft_match else token.__class__ is symbol
                    output_paths = GraphNode.from_token(token)
                    GraphNode.add_next(paths[path], output_paths)
                    GraphNode.merge_paths(nextpaths, output_paths)
                except (CompilerEOIError, AssertionError):
                    pass

        self.parser.lexer.set_state(state)

        if len(nextpaths) == 0:
            raise CompilerNoPathError(self)

        return nextpaths

    def _derive(self) -> None:
        raise NotImplementedError()

    def accept(self, visitor: Visitor) -> None:
        children: set[GraphNode] = self.children
        next_children: set[GraphNode] = set()

        while len(children) > 0:
            for child in children:
                child.accept(visitor)

                next_children |= child.next - children

            children = next_children
            next_children = set()

    def accept_reverse(self, visitor: Visitor, path: "Terminal") -> None:
        children: set[GraphNode] = self.output_paths[path]
        previous_children: set[GraphNode] = set()

        while len(children) > 0:
            for child in children:
                child.accept_reverse(visitor)

                previous_children |= child.previous - children

            children = previous_children
            previous_children = set()


class PruneOutputPaths(Visitor):
    def visit(self, node: GraphNode) -> None:
        if isinstance(node.value, Production):
            node.value.output_paths = {}


class PruneTokens(Visitor):
    def visit(self, node: GraphNode) -> None:
        if not isinstance(node.value, Production):
            node.value.next = None


class PruneIncompletePaths(Visitor):
    def visit(self, node: GraphNode) -> None:
        if not node.visited:
            for next_node in node.next:
                next_node.previous.remove(node)

            for previous_node in node.previous:
                previous_node.next.remove(node)

    def visit_reverse(self, node: GraphNode) -> None:
        node.visited = True


class PrettyPrint(Visitor):
    def __init__(self) -> None:
        self.__indent: list[int] = [0]

    def visit(self, node: GraphNode) -> None:
        if isinstance(node.value, Production):
            print(f'{" " * self.__indent[-1]}{node.value.__class__.__name__}')

            if len(node.next) == 0:
                self.__indent[-1] += 1
            else:
                self.__indent.append(self.__indent[-1] + 1)
        else:
            print(f'{" " * self.__indent[-1]}{node.value.str}')

            if len(node.next) == 0:
                self.__indent.pop()


class Parser:
    _start: type[Production] = Production

    def __init__(self, lexer: "Lexer") -> None:
        self.lexer: "Lexer" = lexer
        self.productions: dict[tuple["Terminal", type[Production]], Production | None] = {}

    def parse(self) -> Production | None:
        path: "Terminal" = self.lexer.get_state()

        try:
            forest: Production = self._start(None, self)
        except CompilerError as error:
            print(error)
            return None

        if forest.recursive_path is not None:
            forest = Production.process_left_recursion(None, self, path, forest)[0]

        return forest

    def prune_incomplete_paths(self, forest: Production) -> None:
        if forest.output_paths is not None:
            output_path: "Terminal | None" = None

            for path in forest.output_paths:
                if path.end[0] == self.lexer.input.endpos:
                    output_path = path
                    break

            if output_path is None:
                print(CompilerNEOIError(forest))
            else:
                forest.output_paths = {output_path: forest.output_paths[output_path]}

    def prune_memoization(self) -> None:
        self.productions = {}


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
