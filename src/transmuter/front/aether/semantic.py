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

from ..semantic.common import (
    TransmuterTreeNode,
    TransmuterNonterminalTreeNode,
    TransmuterTreeVisitor,
)
from ..semantic.symbol_table import (
    TransmuterSymbol,
    TransmuterSymbolTable,
    TransmuterDuplicateSymbolDefinitionError,
    TransmuterUndefinedSymbolError,
)
from .lexical import Identifier, PlusSign, HyphenMinus
from .syntactic import (
    Production,
    ProductionBody,
    Condition,
    ProductionSpecifiers,
    ProductionSpecifier,
    PrimaryExpression,
    PrimitiveCondition,
)


@dataclass
class LexicalSymbol(TransmuterSymbol):
    start: TransmuterNonterminalTreeNode | None = field(
        default=None, init=False
    )
    ignore: TransmuterNonterminalTreeNode | bool = field(
        default=False, init=False
    )
    static_positives: list[str] = field(default_factory=list, init=False)
    conditional_positives: dict[str, TransmuterNonterminalTreeNode] = field(
        default_factory=dict, init=False
    )
    static_negatives: list[str] = field(default_factory=list, init=False)
    conditional_negatives: dict[str, TransmuterNonterminalTreeNode] = field(
        default_factory=dict, init=False
    )


@dataclass
class LexicalSymbolTableBuilder(TransmuterTreeVisitor):
    condition_table: TransmuterSymbolTable = field(
        default_factory=TransmuterSymbolTable, init=False, repr=False
    )
    terminal_table: TransmuterSymbolTable = field(
        default_factory=TransmuterSymbolTable, init=False, repr=False
    )

    def descend(
        self, node: TransmuterTreeNode, _
    ) -> TransmuterTreeNode | None:
        if node.type_ == Production:
            name = node.children[0].children[0].end_terminal.value
            symbol = self.terminal_table.add_get(name, type_=LexicalSymbol)

            if symbol.definition:
                raise TransmuterDuplicateSymbolDefinitionError(
                    node.start_position, name, symbol.definition.start_position
                )

            symbol.definition = node
        elif node.type_ == ProductionBody:
            return None
        elif node.type_ == ProductionSpecifier and node.children[0].type_ in (
            PlusSign,
            HyphenMinus,
        ):
            symbol = self.terminal_table.add_get(
                node.children[1].end_terminal.value, type_=LexicalSymbol
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

            self.process_conditionals(symbol)

        return False

    def process_conditionals(self, symbol: LexicalSymbol) -> None:
        header = symbol.definition.children[0]

        if header.children[1].type_ == Condition:
            symbol.start = header.children[1]

        if header.children[1].type_ == ProductionSpecifiers:
            specifiers = header.children[1]
        elif (
            len(header.children) > 2
            and header.children[2].type_ == ProductionSpecifiers
        ):
            specifiers = header.children[2]
        else:
            return

        for i in range(0, len(specifiers.children[1].children), 2):
            specifier = specifiers.children[1].children[i]

            if specifier.children[0].type_ == PlusSign:
                positive = specifier.children[1].end_terminal.value

                if len(specifier.children) > 2:
                    symbol.conditional_positives[positive] = (
                        specifier.children[2]
                    )
                else:
                    symbol.static_positives.append(positive)
            elif specifier.children[0].type_ == HyphenMinus:
                negative = specifier.children[1].end_terminal.value

                if len(specifier.children) > 2:
                    symbol.conditional_negatives[negative] = (
                        specifier.children[2]
                    )
                else:
                    symbol.static_negatives.append(negative)
            else:  # Ignore
                symbol.ignore = (
                    specifier.children[1]
                    if len(specifier.children) > 1
                    else True
                )


@dataclass
class SyntacticSymbolTableBuilder(TransmuterTreeVisitor):
    condition_table: TransmuterSymbolTable
    terminal_table: TransmuterSymbolTable
    nonterminal_table: TransmuterSymbolTable = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.nonterminal_table = TransmuterSymbolTable(self.terminal_table)

    def descend(
        self, node: TransmuterTreeNode, _
    ) -> TransmuterTreeNode | None:
        if node.type_ == Production:
            name = node.children[0].children[0].end_terminal.value
            symbol = self.nonterminal_table.add_get(name)

            if symbol.definition:
                raise TransmuterDuplicateSymbolDefinitionError(
                    node.start_position, name, symbol.definition.start_position
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
