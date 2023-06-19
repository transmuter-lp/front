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
from copy import deepcopy

from .. import TreeNode, CompilerError
from ..lexer import CompilerEOIError

if TYPE_CHECKING:
    from collections.abc import Generator

    from .. import TreeVisitor
    from ..lexer import Lexer, Terminal

Paths = dict["Terminal", set["GraphNode"]]


class GraphNode:
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
        if production.output_paths is not None:
            return {path: {GraphNode(path, production)} for path in production.output_paths}

        return {production.input_path.path: {GraphNode(production.input_path.path, production)}}

    @staticmethod
    def add_next(previous: set["GraphNode"], _next: Paths) -> None:
        for path in _next:
            for node in _next[path]:
                GraphNode.__merge_sets(node.previous, previous)

            for node in previous:
                GraphNode.__merge_sets(node.next, _next[path])

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

    def __init__(self, path: "Terminal", value: "Terminal | Production") -> None:
        self.path: "Terminal" = path
        self.value: "Terminal | Production" = value
        self.previous: set[GraphNode] = set()
        self.next: set[GraphNode] = set()
        self.visited = False

    def __eq__(self, other) -> bool:
        return isinstance(other, GraphNode) and self.path is other.path and self.value is other.value

    def __hash__(self) -> int:
        return hash((self.path, self.value))

    def accept(self, visitor: "GraphVisitor", top_down: bool = True, left_to_right: bool = True) -> None:
        if top_down:
            if left_to_right:
                visitor.visit_top_down_left_to_right(self)
            else:
                visitor.visit_top_down_right_to_left(self)

        if isinstance(self.value, Production):
            self.value.accept(visitor, top_down, self.path if not left_to_right else None)

        if not top_down:
            if left_to_right:
                visitor.visit_bottom_up_left_to_right(self)
            else:
                visitor.visit_bottom_up_right_to_left(self)

    def get_children_lists(self, ast: bool = False) -> "Generator[list[TreeNode], None, None]":
        if len(self.previous) > 0:
            for node in self.previous:
                for children_list in node.get_children_lists(ast):
                    if isinstance(self.value, Production):
                        for tree in self.value.get_path_trees(self.path, ast):
                            yield deepcopy(children_list) + [tree]
                    else:  # Terminal
                        yield children_list + [self.value]
        else:
            if isinstance(self.value, Production):
                for tree in self.value.get_path_trees(self.path, ast):
                    yield [tree]
            else:  # Terminal
                yield [self.value]


class GraphVisitor:
    def visit_top_down_left_to_right(self, node: GraphNode) -> None:
        pass

    def visit_top_down_right_to_left(self, node: GraphNode) -> None:
        pass

    def visit_bottom_up_left_to_right(self, node: GraphNode) -> None:
        pass

    def visit_bottom_up_right_to_left(self, node: GraphNode) -> None:
        pass


class Production:
    _left_recursive: bool = True

    class NonTerminal(TreeNode):
        def __init__(self, ast: bool = False) -> None:
            self.__ast: bool = ast
            self.children: list[TreeNode] = []

        def add_child(self, child: TreeNode) -> None:
            if self.__ast:
                child._process_parent(self)  # pylint: disable=protected-access
                self._process_child(child)

                if child._keep:  # pylint: disable=protected-access
                    self.children.append(child)
            else:
                self.children.append(child)

        def add_children(self, children: list[TreeNode]) -> None:
            for child in children:
                self.add_child(child)

        def accept(self, visitor: "TreeVisitor", top_down: bool = True, left_to_right: bool = True) -> None:
            if top_down:
                if left_to_right:
                    visitor.visit_top_down_left_to_right(self)
                else:
                    visitor.visit_top_down_right_to_left(self)

            for child in self.children if left_to_right else reversed(self.children):
                child.accept(visitor, top_down, left_to_right)

            if not top_down:
                if left_to_right:
                    visitor.visit_bottom_up_left_to_right(self)
                else:
                    visitor.visit_bottom_up_right_to_left(self)

        def _process_child(self, child: TreeNode) -> None:
            pass

    @staticmethod
    def process_left_recursion(
        parent: "Production | None", parser: "Parser", path: "Terminal", production: "Production"
    ) -> tuple["Production", Paths]:
        nextpaths: Paths = {}
        recursive_path: set[type[Production]] = cast(set[type[Production]], production.recursive_path)
        production.recursive_path = None

        while True:
            if production.output_paths is None or nextpaths.keys() | production.output_paths.keys() == nextpaths.keys():
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
        self.output_paths: Paths | None = {}
        state: "Terminal" = parser.lexer.get_state()
        self.input_path: GraphNode = GraphNode(state, state)
        self.recursive_path: set[type[Production]] | None = None
        self.children: set[GraphNode] = set()
        self._derive()

        if len(self.output_paths) == 1 and state in self.output_paths:
            self.output_paths = None

        self.children = self.input_path.next

        for child in self.children:
            child.previous.clear()

        self.parent = None

    def accept(self, visitor: GraphVisitor, top_down: bool = True, path: "Terminal | None" = None) -> None:
        if path is None or self.output_paths is not None:
            children: set[GraphNode] = self.children if path is None else cast(dict["Terminal", set[GraphNode]], self.output_paths)[path]
            next_children: set[GraphNode] = set()

            while len(children) > 0:
                for child in children:
                    child.accept(visitor, top_down, path is None)
                    next_children |= (child.next if path is None else child.previous) - children

                children = next_children
                next_children = set()

    def get_path_trees(self, path: "Terminal", ast: bool = False) -> "Generator[Production.NonTerminal, None, None]":
        if self.output_paths is not None:
            for node in self.output_paths[path]:
                for children_list in node.get_children_lists(ast):
                    tree: Production.NonTerminal = self.NonTerminal(ast)
                    tree.add_children(children_list)
                    yield tree
        else:
            yield self.NonTerminal(ast)

    def get_trees(self, ast: bool = False) -> "Generator[Production.NonTerminal, None, None]":
        if self.output_paths is not None:
            for path in self.output_paths:
                for tree in self.get_path_trees(path, ast):
                    yield tree
        else:
            yield self.NonTerminal(ast)

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

    def __left_recursive(self, paths: Paths, production: type["Production"]) -> bool:
        input_path: GraphNode = self.input_path

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


class PruneOutputPaths(GraphVisitor):
    def visit_top_down_left_to_right(self, node: GraphNode) -> None:
        if isinstance(node.value, Production):
            node.value.output_paths = None


class PruneTokens(GraphVisitor):
    def visit_top_down_left_to_right(self, node: GraphNode) -> None:
        if not isinstance(node.value, Production):
            node.value.next = None


class PruneIncompletePaths(GraphVisitor):
    def visit_top_down_left_to_right(self, node: GraphNode) -> None:
        if not node.visited:
            for next_node in node.next:
                for previous_node in next_node.previous:
                    if previous_node == node:
                        next_node.previous.remove(previous_node)
                        break

            for previous_node in node.previous:
                for next_node in previous_node.next:
                    if next_node == node:
                        previous_node.next.remove(next_node)
                        break

    def visit_top_down_right_to_left(self, node: GraphNode) -> None:
        node.visited = True


class PrettyPrint(GraphVisitor):
    def __init__(self) -> None:
        self.output: str = ""
        self.__indent: list[int] = [0]

    def visit_top_down_left_to_right(self, node: GraphNode) -> None:
        if isinstance(node.value, Production):
            self.output += f'\n{" " * self.__indent[-1]}{node.value.__class__.__name__}'

            if len(node.value.children) > 0:
                if len(node.next) == 0:
                    self.__indent[-1] += 1
                else:
                    self.__indent.append(self.__indent[-1] + 1)
        else:
            self.output += f'\n{" " * self.__indent[-1]}{node.value.str}'

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
