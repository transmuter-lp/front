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
    TransmuterTerminalTreeNode,
    TransmuterNonterminalTreeNode,
    TransmuterTreeVisitor,
    TransmuterTreeFold,
)
from ..semantic.symbol_table import (
    TransmuterSymbol,
    TransmuterSymbolTable,
    TransmuterDuplicateSymbolDefinitionError,
    TransmuterUndefinedSymbolError,
)
from .lexical import (
    Identifier,
    LeftParenthesis,
    RightParenthesis,
    VerticalLine,
    PlusSign,
    HyphenMinus,
    Asterisk,
    QuestionMark,
    ExpressionRange,
    OrdChar,
    QuotedChar,
    FullStop,
)
from .syntactic import (
    Production,
    ProductionBody,
    Condition,
    ProductionSpecifiers,
    SelectionExpression,
    ProductionSpecifier,
    IterationExpression,
    PrimaryExpression,
    PrimitiveCondition,
)


@dataclass
class LexicalSimplePattern:
    char: str

    def __repr__(self) -> str:
        return repr((self.char,))


class LexicalWildcardPattern:
    def __repr__(self) -> str:
        return repr(())


@dataclass
class LexicalRangePattern:
    first_char: str
    last_char: str

    def __repr__(self) -> str:
        return repr((self.first_char, self.last_char))


@dataclass
class LexicalBracketPattern:
    negative_match: bool
    patterns: list[LexicalSimplePattern | LexicalRangePattern]

    def __repr__(self) -> str:
        return repr((self.negative_match, self.patterns))


@dataclass(eq=False)
class LexicalState:
    pattern: (
        LexicalSimplePattern | LexicalWildcardPattern | LexicalBracketPattern
    )
    next_states: set["LexicalState"] | None = None
    state_accept: bool = field(default=False, init=False)
    next_states_indexes: list[int] = field(default_factory=list, init=False)

    def __repr__(self) -> str:
        return repr(
            (self.pattern, self.state_accept, self.next_states_indexes)
        )

    def copy(self) -> "LexicalState":
        return LexicalState(self.pattern, self.next_states)


@dataclass
class LexicalFragment:
    states: dict[LexicalState, None]
    first: set[LexicalState]
    last: set[LexicalState]
    bypass: bool = False

    def copy(self, bypass: bool) -> "LexicalFragment":
        new_states = {}

        for state in self.states:
            new_states[state] = state.copy()

        fragment = LexicalFragment(
            {s: None for s in new_states.values()},
            {new_states[s] for s in self.first},
            {new_states[s] for s in self.last},
            bypass,
        )

        for state in fragment.states:
            if state.next_states is not None:
                state.next_states = {new_states[s] for s in state.next_states}

        return fragment

    def connect(self, fragment: "LexicalFragment") -> None:
        for state in self.last:
            if state.next_states is None:
                state.next_states = set()

            state.next_states |= fragment.first


class LexicalFold(TransmuterTreeFold[LexicalFragment]):
    def top_after(self) -> None:
        if self.fold_queue[0] is not None:
            for state in self.fold_queue[0].last:
                state.state_accept = True

    def fold_internal(
        self,
        node: TransmuterNonterminalTreeNode,
        children: list[LexicalFragment],
    ) -> LexicalFragment | None:
        if len(children) == 0:
            return None

        if len(children) == 1:
            if node.type_ == IterationExpression and len(node.children) == 2:
                return self.fold_iteration(node.children[1], children[0])

            return children[0]

        if node.type_ == SelectionExpression:
            return self.fold_selection(children)

        # SequenceExpression
        return self.fold_sequence(children)

    def fold_external(
        self, node: TransmuterTerminalTreeNode
    ) -> LexicalFragment | None:
        if node.type_ in (
            VerticalLine,
            Asterisk,
            PlusSign,
            QuestionMark,
            ExpressionRange,
            LeftParenthesis,
            RightParenthesis,
        ):
            return None

        chars = node.end_terminal.value
        pattern: (
            LexicalSimplePattern
            | LexicalWildcardPattern
            | LexicalBracketPattern
        )

        if node.type_ in (OrdChar, QuotedChar):
            if node.type_ == QuotedChar or len(chars) == 1:
                pattern = LexicalSimplePattern(chars)
            else:
                fragments = [
                    self.fold_pattern(LexicalSimplePattern(c)) for c in chars
                ]
                return self.fold_sequence(fragments)
        elif node.type_ == FullStop:
            pattern = LexicalWildcardPattern()
        else:  # BracketExpression
            pattern = self.process_bracket(chars)

        return self.fold_pattern(pattern)

    def fold_iteration(
        self, iterator: TransmuterTerminalTreeNode, child: LexicalFragment
    ) -> LexicalFragment | None:
        iterator_type = iterator.type_

        if iterator_type == ExpressionRange:
            range_ = iterator.end_terminal.value

            if range_ in ("{0}", "{0,0}"):
                return None

            if range_ == "{0,}":
                iterator_type = Asterisk
            elif range_ == "{1,}":
                iterator_type = PlusSign
            elif range_ == "{0,1}":
                iterator_type = QuestionMark
            elif range_ not in ("{1}", "{1,0}", "{1,1}"):
                return self.fold_range(range_, child)

        if iterator_type in (Asterisk, QuestionMark):
            child.bypass = True

        if iterator_type in (Asterisk, PlusSign):
            child.connect(child)

        return child

    def fold_range(
        self, range_str: str, child: LexicalFragment
    ) -> LexicalFragment:
        range_split = range_str[1:-1].split(",")
        range_ = [
            int(range_split[0]),
            (
                (int(range_split[1]) if len(range_split[1]) > 0 else -1)
                if len(range_split) == 2
                else None
            ),
        ]
        assert range_[0] is not None

        if range_[1] is not None and range_[1] != -1:
            if range_[1] <= range_[0]:
                range_[1] = None
            elif child.bypass or range_[0] == 0:
                child.bypass = True
                range_[0] = range_[1]
                range_[1] = None

        fragments = [
            child.copy(child.bypass) if i > 0 else child
            for i in range(range_[0])
        ]

        if range_[1] is not None:
            if range_[1] == -1:
                fragments[-1].connect(fragments[-1])
            else:
                fragments.extend(
                    child.copy(True) for _ in range(range_[1] - range_[0])
                )

        return self.fold_sequence(fragments)

    def fold_selection(
        self, children: list[LexicalFragment]
    ) -> LexicalFragment:
        fragment = children[0]

        for i in range(1, len(children)):
            fragment.bypass = fragment.bypass or children[i].bypass
            fragment.states |= children[i].states
            fragment.first |= children[i].first
            fragment.last |= children[i].last

        return fragment

    def fold_sequence(
        self, children: list[LexicalFragment]
    ) -> LexicalFragment:
        fragment = children[0]

        for i in range(1, len(children)):
            children[i - 1].connect(children[i])

            if children[i - 1].bypass:
                children[i - 1].first |= children[i].first
                children[i].first = children[i - 1].first

            if children[i].bypass:
                children[i].last |= children[i - 1].last
                children[i - 1].last = children[i].last

            fragment.bypass = fragment.bypass and children[i].bypass
            fragment.states |= children[i].states

        fragment.last = children[-1].last
        return fragment

    def fold_pattern(
        self,
        pattern: (
            LexicalSimplePattern
            | LexicalWildcardPattern
            | LexicalBracketPattern
        ),
    ) -> LexicalFragment:
        state = LexicalState(pattern)
        return LexicalFragment({state: None}, {state}, {state})

    def process_bracket(self, chars: str) -> LexicalBracketPattern:
        chars = chars[1:-1]
        negative_match = False
        patterns: list[LexicalSimplePattern | LexicalRangePattern] = []

        if chars[0] == "^":
            negative_match = True
            chars = chars[1:]

        i = 0
        j = 0

        while i < len(chars):
            j = i + 1

            if chars[i] == "\\":
                j += 3 if chars[j] in "01" else 1

            if j >= len(chars) - 1 or chars[j] != "-":
                patterns.append(LexicalSimplePattern(chars[i:j]))
            else:
                first_char = chars[i:j]
                i = j + 1
                j = i + 1

                if chars[i] == "\\":
                    j += 3 if chars[j] in "01" else 1

                patterns.append(LexicalRangePattern(first_char, chars[i:j]))

            i = j

        return LexicalBracketPattern(negative_match, patterns)


@dataclass
class LexicalSymbol(TransmuterSymbol):
    states_start: list[int] = field(default_factory=list, init=False)
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
    states: list[LexicalState] = field(default_factory=list, init=False)


@dataclass
class LexicalSymbolTableBuilder(TransmuterTreeVisitor):
    condition_table: TransmuterSymbolTable = field(
        default_factory=TransmuterSymbolTable, init=False, repr=False
    )
    terminal_table: TransmuterSymbolTable = field(
        default_factory=TransmuterSymbolTable, init=False, repr=False
    )
    fold: LexicalFold | None = field(default=None, init=False, repr=False)

    def descend(
        self, node: TransmuterTreeNode, _
    ) -> TransmuterTreeNode | None:
        if node.type_ == Production:
            name = node.children[0].children[0].end_terminal.value
            symbol = self.terminal_table.add_get(name, type_=LexicalSymbol)

            if symbol.definition is not None:
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
            if symbol.definition is None:
                raise TransmuterUndefinedSymbolError(
                    self.tree.end_terminal.end_position,
                    name,
                    symbol.references[0].start_position,
                )

            self.process_conditionals(symbol)
            self.process_states(symbol)

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

    def process_states(self, symbol: LexicalSymbol) -> None:
        if self.fold is None:
            self.fold = LexicalFold(symbol.definition.children[1].children[0])
        else:
            self.fold.tree = symbol.definition.children[1].children[0]
            self.fold.fold_queue.clear()

        self.fold.visit()
        fragment = self.fold.fold_queue[0]

        if fragment is not None:
            states_indexes = {}

            for i, s in zip(range(len(fragment.states)), fragment.states):
                symbol.states.append(s)
                states_indexes[s] = i

            symbol.states_start = sorted(
                states_indexes[s] for s in fragment.first
            )

            for state in symbol.states:
                if state.next_states is not None:
                    state.next_states_indexes = sorted(
                        states_indexes[s] for s in state.next_states
                    )
                    state.next_states = None


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

            if symbol.definition is not None:
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
            if symbol.definition is None:
                raise TransmuterUndefinedSymbolError(
                    self.tree.end_terminal.end_position,
                    name,
                    symbol.references[0].start_position,
                )

        return False
