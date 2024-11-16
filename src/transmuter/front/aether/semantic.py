# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2024  The Transmuter Project
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

from dataclasses import dataclass, field

from ..semantic.common import TransmuterTreeNode, TransmuterTreeVisitor
from ..semantic.symbol_table import (
    TransmuterSymbolTable,
    TransmuterDuplicateSymbolDefinitionError,
    TransmuterUndefinedSymbolError,
)
from .lexical import Identifier, PlusSign, HyphenMinus
from .syntactic import (
    Production,
    ProductionSpecifier,
    PrimaryExpression,
    PrimitiveCondition,
)


@dataclass
class LexicalSymbolTableBuilder(TransmuterTreeVisitor):
    condition_table: TransmuterSymbolTable = field(
        default_factory=TransmuterSymbolTable, init=False, repr=False
    )
    terminal_table: TransmuterSymbolTable = field(
        default_factory=TransmuterSymbolTable, init=False, repr=False
    )

    def descend(self, node: TransmuterTreeNode) -> TransmuterTreeNode | None:
        if node.type_ == Production:
            symbol = self.terminal_table.add_get(
                node.children[0].children[0].end_terminal.value
            )

            if symbol.definition:
                raise TransmuterDuplicateSymbolDefinitionError(
                    node.start_position,
                    symbol.definition.children[0]
                    .children[0]
                    .end_terminal.value,
                    symbol.definition.start_position,
                )

            symbol.definition = node
        elif node.type_ == ProductionSpecifier and node.children[0].type_ in (
            PlusSign,
            HyphenMinus,
        ):
            symbol = self.terminal_table.add_get(
                node.children[1].end_terminal.value
            )
            symbol.references.append(node)
        elif (
            node.type_ == PrimitiveCondition
            and node.children[0].type_ == Identifier
        ):
            symbol = self.condition_table.add_get(
                node.children[0].end_terminal.value
            )
            symbol.references.append(node)

        return node

    def bottom(self) -> bool:
        for name, symbol in self.terminal_table:
            if not symbol.definition:
                raise TransmuterUndefinedSymbolError(
                    self.tree.end_terminal.end_position,
                    name,
                    symbol.references[0].start_position,
                )

        return False


@dataclass
class SyntacticSymbolTableBuilder(TransmuterTreeVisitor):
    condition_table: TransmuterSymbolTable
    terminal_table: TransmuterSymbolTable
    nonterminal_table: TransmuterSymbolTable = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.nonterminal_table = TransmuterSymbolTable(
            self.terminal_table, False
        )

    def descend(self, node: TransmuterTreeNode) -> TransmuterTreeNode | None:
        if node.type_ == Production:
            symbol = self.nonterminal_table.add_get(
                node.children[0].children[0].end_terminal.value
            )

            if symbol.definition:
                raise TransmuterDuplicateSymbolDefinitionError(
                    node.start_position,
                    symbol.definition.children[0]
                    .children[0]
                    .end_terminal.value,
                    symbol.definition.start_position,
                )

            symbol.definition = node
        elif (
            node.type_ == PrimaryExpression
            and node.children[0].type_ == Identifier
        ):
            symbol = self.nonterminal_table.add_get(
                node.children[0].end_terminal.value
            )
            symbol.references.append(node)
        elif (
            node.type_ == PrimitiveCondition
            and node.children[0].type_ == Identifier
        ):
            symbol = self.condition_table.add_get(
                node.children[0].end_terminal.value
            )
            symbol.references.append(node)

        return node

    def bottom(self) -> bool:
        for name, symbol in self.nonterminal_table:
            if not symbol.definition:
                raise TransmuterUndefinedSymbolError(
                    self.tree.end_terminal.end_position,
                    name,
                    symbol.references[0].start_position,
                )

        return False
