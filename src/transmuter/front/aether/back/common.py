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

from ...semantic.common import (
    TransmuterTerminalTreeNode,
    TransmuterNonterminalTreeNode,
    TransmuterTreeFold,
)
from ...semantic.symbol_table import TransmuterSymbolTable
from ..lexical import (
    CommercialAt,
    LeftParenthesis,
    RightParenthesis,
    DoubleVerticalLine,
    DoubleAmpersand,
    ExclamationMark,
)
from ..syntactic import (
    DisjunctionCondition,
    ConjunctionCondition,
    NegationCondition,
    PrimitiveCondition,
)
from ..semantic import LexicalState, LexicalSymbol


@dataclass
class AetherFileFold:
    symbol_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode]

    @staticmethod
    def indent(value: str) -> str:
        return f"    {value.replace('\n', '\n    ')}".replace(
            "    \n", "\n"
        ).rstrip()

    def fold(self) -> str:
        raise NotImplementedError()


class AetherCommonFileFold(AetherFileFold):
    def fold(self) -> str:
        conditions = []

        for name, _ in self.symbol_table:
            conditions.append(self.fold_condition(name))

        return self.fold_file(conditions)

    def fold_file(self, conditions: list[str]) -> str:
        raise NotImplementedError()

    def fold_condition(self, name: str) -> str:
        raise NotImplementedError()


class AetherConditionFold(TransmuterTreeFold[str]):
    def fold_internal(
        self, node: TransmuterNonterminalTreeNode, children: list[str]
    ) -> str | None:
        if len(children) == 0:
            return None

        if len(children) == 1:
            if node.type_ == NegationCondition and len(node.children) % 2 == 0:
                return self.fold_negation(node, children[0])

            if node.type_ == PrimitiveCondition:
                return self.fold_primitive(node, children[0])

            return children[0]

        if node.type_ == DisjunctionCondition:
            return self.fold_disjunction(node, children)

        assert node.type_ == ConjunctionCondition
        return self.fold_conjunction(node, children)

    def fold_external(self, node: TransmuterTerminalTreeNode) -> str | None:
        if node.type_ in (
            CommercialAt,
            DoubleVerticalLine,
            DoubleAmpersand,
            ExclamationMark,
            LeftParenthesis,
            RightParenthesis,
        ):
            return None

        return node.end_terminal.value

    def fold_disjunction(
        self, node: TransmuterNonterminalTreeNode, children: list[str]
    ) -> str:
        raise NotImplementedError()

    def fold_conjunction(
        self, node: TransmuterNonterminalTreeNode, children: list[str]
    ) -> str:
        raise NotImplementedError()

    def fold_negation(
        self, node: TransmuterNonterminalTreeNode, child: str
    ) -> str:
        raise NotImplementedError()

    def fold_primitive(
        self, node: TransmuterNonterminalTreeNode, child: str
    ) -> str:
        raise NotImplementedError()


@dataclass
class AetherLexicalFileFold(AetherFileFold):
    condition_fold_type: type[AetherConditionFold]
    _condition_fold: AetherConditionFold | None = field(
        default=None, init=False, repr=False
    )

    def fold(self) -> str:
        terminal_tag_names = []
        terminal_tags = []

        for name, symbol in self.symbol_table:
            assert isinstance(symbol, LexicalSymbol)
            terminal_tag_names.append(name)
            states_start = (
                self.fold_states_start(symbol.states_start)
                if symbol.states_start != [0]
                else None
            )
            start = (
                self.fold_start(self.fold_condition(symbol.start))
                if symbol.start is not None
                else None
            )
            ignore = (
                self.fold_ignore(
                    self.fold_condition(symbol.ignore)
                    if symbol.ignore is not True
                    else None
                )
                if symbol.ignore is not False
                else None
            )

            if (
                len(symbol.static_positives) > 0
                or len(symbol.conditional_positives) > 0
            ):
                static_positives = self.fold_static_positives(
                    symbol.static_positives
                )
                conditional_positives = [
                    self.fold_conditional_positive(
                        p, self.fold_condition(symbol.conditional_positives[p])
                    )
                    for p in symbol.conditional_positives
                ]
                positives = self.fold_positives(
                    static_positives, conditional_positives
                )
            else:
                positives = None

            if (
                len(symbol.static_negatives) > 0
                or len(symbol.conditional_negatives) > 0
            ):
                static_negatives = self.fold_static_negatives(
                    symbol.static_negatives
                )
                conditional_negatives = [
                    self.fold_conditional_negative(
                        n, self.fold_condition(symbol.conditional_negatives[n])
                    )
                    for n in symbol.conditional_negatives
                ]
                negatives = self.fold_negatives(
                    static_negatives, conditional_negatives
                )
            else:
                negatives = None

            states = [
                self.fold_state(i, symbol.states[i])
                for i in range(len(symbol.states))
            ]
            nfa = self.fold_nfa(states)
            terminal_tags.append(
                self.fold_terminal_tag(
                    name,
                    states_start,
                    start,
                    ignore,
                    positives,
                    negatives,
                    nfa,
                )
            )

        return self.fold_file(terminal_tag_names, terminal_tags)

    def fold_condition(self, value: TransmuterNonterminalTreeNode) -> str:
        if self._condition_fold is None:
            self._condition_fold = self.condition_fold_type(value)
        else:
            self._condition_fold.tree = value

        self._condition_fold.visit()
        assert len(self._condition_fold.fold_queue) > 0
        assert self._condition_fold.fold_queue[0] is not None
        return self._condition_fold.fold_queue[0]

    def fold_file(
        self, terminal_tag_names: list[str], terminal_tags: list[str]
    ) -> str:
        raise NotImplementedError()

    def fold_terminal_tag(
        self,
        name: str,
        states_start: str | None,
        start: str | None,
        ignore: str | None,
        positives: str | None,
        negatives: str | None,
        nfa: str,
    ) -> str:
        raise NotImplementedError()

    def fold_states_start(self, value: list[int]) -> str:
        raise NotImplementedError()

    def fold_start(self, value: str) -> str:
        raise NotImplementedError()

    def fold_ignore(self, value: str | None) -> str:
        raise NotImplementedError()

    def fold_positives(
        self, static_positives: str, conditional_positives: list[str]
    ) -> str:
        raise NotImplementedError()

    def fold_negatives(
        self, static_negatives: str, conditional_negatives: list[str]
    ) -> str:
        raise NotImplementedError()

    def fold_nfa(self, states: list[str]) -> str:
        raise NotImplementedError()

    def fold_static_positives(self, value: list[str]) -> str:
        raise NotImplementedError()

    def fold_conditional_positive(self, value: str, condition: str) -> str:
        raise NotImplementedError()

    def fold_static_negatives(self, value: list[str]) -> str:
        raise NotImplementedError()

    def fold_conditional_negative(self, value: str, condition: str) -> str:
        raise NotImplementedError()

    def fold_state(self, index: int, value: LexicalState) -> str:
        raise NotImplementedError()
