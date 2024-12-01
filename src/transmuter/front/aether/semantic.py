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

from ..lexical import TransmuterTerminal
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
    Ignore,
    Asterisk,
    QuestionMark,
    ExpressionRange,
    OrdChar,
    QuotedChar,
    FullStop,
    BracketExpression,
)
from .syntactic import (
    Production,
    ProductionBody,
    Condition,
    ProductionSpecifiers,
    SelectionExpression,
    DisjunctionCondition,
    SequenceExpression,
    ConjunctionCondition,
    ProductionSpecifier,
    IterationExpression,
    PrimaryExpression,
    NegationCondition,
    OptionalExpression,
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

        assert self.first <= self.states.keys()
        assert self.last <= self.states.keys()
        fragment = LexicalFragment(
            {s: None for s in new_states.values()},
            {new_states[s] for s in self.first},
            {new_states[s] for s in self.last},
            bypass,
        )

        for state in fragment.states:
            if state.next_states is not None:
                assert state.next_states <= self.states.keys()
                state.next_states = {new_states[s] for s in state.next_states}

        return fragment

    def connect(self, fragment: "LexicalFragment") -> None:
        for state in self.last:
            if state.next_states is None:
                state.next_states = set()

            state.next_states |= fragment.first


class LexicalFold(TransmuterTreeFold[LexicalFragment]):
    def top_after(self) -> None:
        assert len(self.fold_queue) > 0

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
                assert isinstance(node.children[1], TransmuterTerminalTreeNode)
                return self.fold_iteration(node.children[1], children[0])

            return children[0]

        if node.type_ == SelectionExpression:
            return self.fold_selection(children)

        assert node.type_ == SequenceExpression
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
        else:
            assert node.type_ == BracketExpression
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
        assert len(range_split) > 0
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
                assert len(fragments) > 0
                fragments[-1].connect(fragments[-1])
            else:
                fragments.extend(
                    child.copy(True) for _ in range(range_[1] - range_[0])
                )

        return self.fold_sequence(fragments)

    def fold_selection(
        self, children: list[LexicalFragment]
    ) -> LexicalFragment:
        assert len(children) > 0
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
        assert len(children) > 0
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
        assert len(chars) > 0

        if chars[0] == "^":
            negative_match = True
            chars = chars[1:]

        i = 0
        j = 0

        while i < len(chars):
            j = i + 1

            if chars[i] == "\\":
                assert j < len(chars)
                j += 3 if chars[j] in "01" else 1

            if j >= len(chars) - 1 or chars[j] != "-":
                patterns.append(LexicalSimplePattern(chars[i:j]))
            else:
                first_char = chars[i:j]
                i = j + 1
                j = i + 1

                if chars[i] == "\\":
                    assert j < len(chars)
                    j += 3 if chars[j] in "01" else 1

                patterns.append(LexicalRangePattern(first_char, chars[i:j]))

            i = j

        return LexicalBracketPattern(negative_match, patterns)


@dataclass
class LexicalSymbol(TransmuterSymbol[TransmuterNonterminalTreeNode]):
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
    condition_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode] = (
        field(
            default_factory=TransmuterSymbolTable[
                TransmuterNonterminalTreeNode
            ],
            init=False,
            repr=False,
        )
    )
    terminal_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode] = (
        field(
            default_factory=TransmuterSymbolTable[
                TransmuterNonterminalTreeNode
            ],
            init=False,
            repr=False,
        )
    )
    fold: LexicalFold | None = field(default=None, init=False, repr=False)

    def descend(
        self, node: TransmuterTreeNode, _
    ) -> TransmuterTreeNode | None:
        if isinstance(node, TransmuterNonterminalTreeNode):
            assert len(node.children) > 0

            if node.type_ == Production:
                assert isinstance(
                    node.children[0], TransmuterNonterminalTreeNode
                )
                assert len(node.children[0].children) > 0
                name = node.children[0].children[0].end_terminal.value
                symbol = self.terminal_table.add_get(name, type_=LexicalSymbol)

                if symbol.definition is not None:
                    raise TransmuterDuplicateSymbolDefinitionError(
                        node.start_position,
                        name,
                        symbol.definition.start_position,
                    )

                symbol.definition = node
            elif node.type_ == ProductionBody:
                return None
            elif node.type_ == ProductionSpecifier and node.children[
                0
            ].type_ in (PlusSign, HyphenMinus):
                assert len(node.children) > 1
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
            assert isinstance(symbol, LexicalSymbol)

            if symbol.definition is None:
                assert len(symbol.references) > 0
                raise TransmuterUndefinedSymbolError(
                    self.tree.end_terminal.end_position,
                    name,
                    symbol.references[0].start_position,
                )

            self.process_conditionals(symbol)
            self.process_states(symbol)

        return False

    def process_conditionals(self, symbol: LexicalSymbol) -> None:
        assert symbol.definition is not None
        assert len(symbol.definition.children) > 0
        header = symbol.definition.children[0]
        assert isinstance(header, TransmuterNonterminalTreeNode)
        assert len(header.children) > 1

        if header.children[1].type_ == Condition:
            assert isinstance(
                header.children[1], TransmuterNonterminalTreeNode
            )
            symbol.start = header.children[1]

        if header.children[1].type_ == ProductionSpecifiers:
            assert isinstance(
                header.children[1], TransmuterNonterminalTreeNode
            )
            specifiers = header.children[1]
        elif (
            len(header.children) > 2
            and header.children[2].type_ == ProductionSpecifiers
        ):
            assert isinstance(
                header.children[2], TransmuterNonterminalTreeNode
            )
            specifiers = header.children[2]
        else:
            return

        assert len(specifiers.children) > 1
        assert isinstance(
            specifiers.children[1], TransmuterNonterminalTreeNode
        )

        for i in range(0, len(specifiers.children[1].children), 2):
            specifier = specifiers.children[1].children[i]
            assert isinstance(specifier, TransmuterNonterminalTreeNode)
            assert len(specifier.children) > 0

            if specifier.children[0].type_ == PlusSign:
                assert len(specifier.children) > 1
                positive = specifier.children[1].end_terminal.value

                if len(specifier.children) > 2:
                    assert isinstance(
                        specifier.children[2], TransmuterNonterminalTreeNode
                    )
                    symbol.conditional_positives[positive] = (
                        specifier.children[2]
                    )
                else:
                    symbol.static_positives.append(positive)
            elif specifier.children[0].type_ == HyphenMinus:
                assert len(specifier.children) > 1
                negative = specifier.children[1].end_terminal.value

                if len(specifier.children) > 2:
                    assert isinstance(
                        specifier.children[2], TransmuterNonterminalTreeNode
                    )
                    symbol.conditional_negatives[negative] = (
                        specifier.children[2]
                    )
                else:
                    symbol.static_negatives.append(negative)
            else:
                assert specifier.children[0].type_ == Ignore

                if len(specifier.children) > 1:
                    assert isinstance(
                        specifier.children[1], TransmuterNonterminalTreeNode
                    )
                    symbol.ignore = specifier.children[1]
                else:
                    symbol.ignore = True

    def process_states(self, symbol: LexicalSymbol) -> None:
        assert symbol.definition is not None
        assert len(symbol.definition.children) > 1
        assert isinstance(
            symbol.definition.children[1], TransmuterNonterminalTreeNode
        )
        assert len(symbol.definition.children[1].children) > 0
        assert isinstance(
            symbol.definition.children[1].children[0],
            TransmuterNonterminalTreeNode,
        )

        if self.fold is None:
            self.fold = LexicalFold(symbol.definition.children[1].children[0])
        else:
            self.fold.tree = symbol.definition.children[1].children[0]
            self.fold.fold_queue.clear()

        self.fold.visit()
        assert len(self.fold.fold_queue) > 0
        fragment = self.fold.fold_queue[0]

        if fragment is not None:
            states_indexes = {}

            for i, s in zip(range(len(fragment.states)), fragment.states):
                symbol.states.append(s)
                states_indexes[s] = i

            assert fragment.first <= fragment.states.keys()
            symbol.states_start = sorted(
                states_indexes[s] for s in fragment.first
            )

            for state in symbol.states:
                if state.next_states is not None:
                    assert state.next_states <= fragment.states.keys()
                    state.next_states_indexes = sorted(
                        states_indexes[s] for s in state.next_states
                    )
                    state.next_states = None


@dataclass
class SyntacticFragment:
    references: dict[TransmuterTerminal, list[TransmuterNonterminalTreeNode]]
    bypass: bool = False


@dataclass
class SyntacticFold(TransmuterTreeFold[SyntacticFragment]):
    def fold_internal(
        self,
        node: TransmuterNonterminalTreeNode,
        children: list[SyntacticFragment],
    ) -> SyntacticFragment | None:
        if len(children) == 0 or node.type_ in (
            Condition,
            DisjunctionCondition,
            ConjunctionCondition,
            NegationCondition,
            PrimitiveCondition,
        ):
            return None

        if len(children) == 1:
            if (
                node.type_ == PrimaryExpression
                and node.children[-1].type_ == Condition
            ):
                assert isinstance(
                    node.children[-1], TransmuterNonterminalTreeNode
                )

                for reference in children[0].references:
                    children[0].references[reference].insert(
                        0, node.children[-1]
                    )
            elif node.type_ in (OptionalExpression, IterationExpression):
                children[0].bypass = True
        elif node.type_ == SelectionExpression:
            for i in range(1, len(children)):
                children[0].references |= children[i].references
                children[0].bypass = children[0].bypass or children[i].bypass
        else:
            assert node.type_ == SequenceExpression

            if children[0].bypass:
                for i in range(1, len(children)):
                    children[0].references |= children[i].references
                    children[0].bypass = (
                        children[0].bypass and children[i].bypass
                    )

                    if not children[0].bypass:
                        break

        return children[0]

    def fold_external(
        self, node: TransmuterTerminalTreeNode
    ) -> SyntacticFragment | None:
        if node.type_ == Identifier:
            return SyntacticFragment({node.end_terminal: []})

        return None


@dataclass
class SyntacticSymbol(TransmuterSymbol[TransmuterNonterminalTreeNode]):
    start: TransmuterNonterminalTreeNode | bool = field(
        default=False, init=False
    )
    static_first: list[TransmuterTerminal] = field(
        default_factory=list, init=False
    )
    conditional_first: dict[
        TransmuterTerminal, list[TransmuterNonterminalTreeNode]
    ] = field(default_factory=dict, init=False)


@dataclass
class SyntacticSymbolTableBuilder(TransmuterTreeVisitor):
    condition_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode]
    terminal_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode]
    nonterminal_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode] = (
        field(init=False, repr=False)
    )
    fold: SyntacticFold | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.nonterminal_table = TransmuterSymbolTable[
            TransmuterNonterminalTreeNode
        ](self.terminal_table)

    def descend(
        self, node: TransmuterTreeNode, _
    ) -> TransmuterTreeNode | None:
        if isinstance(node, TransmuterNonterminalTreeNode):
            assert len(node.children) > 0

            if node.type_ == Production:
                assert isinstance(
                    node.children[0], TransmuterNonterminalTreeNode
                )
                assert len(node.children[0].children) > 0
                name = node.children[0].children[0].end_terminal.value
                symbol = self.nonterminal_table.add_get(
                    name, type_=SyntacticSymbol
                )

                if symbol.definition is not None:
                    raise TransmuterDuplicateSymbolDefinitionError(
                        node.start_position,
                        name,
                        symbol.definition.start_position,
                    )

                symbol.definition = node
            elif (
                node.type_ == PrimaryExpression
                and node.children[0].type_ == Identifier
            ):
                symbol = self.nonterminal_table.add_get(
                    node.children[0].end_terminal.value, type_=SyntacticSymbol
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
            assert isinstance(symbol, SyntacticSymbol)

            if symbol.definition is None:
                assert len(symbol.references) > 0
                raise TransmuterUndefinedSymbolError(
                    self.tree.end_terminal.end_position,
                    name,
                    symbol.references[0].start_position,
                )

            self.process_start(symbol)
            self.process_first(symbol)

        return False

    def process_start(self, symbol: SyntacticSymbol) -> None:
        assert symbol.definition is not None
        assert len(symbol.definition.children) > 0
        header = symbol.definition.children[0]
        assert isinstance(header, TransmuterNonterminalTreeNode)
        assert len(header.children) > 1

        if header.children[1].type_ != ProductionSpecifiers:
            return

        specifiers = header.children[1]
        assert isinstance(specifiers, TransmuterNonterminalTreeNode)
        assert len(specifiers.children) > 1
        assert isinstance(
            specifiers.children[1], TransmuterNonterminalTreeNode
        )

        for i in range(0, len(specifiers.children[1].children), 2):
            specifier = specifiers.children[1].children[i]
            assert isinstance(specifier, TransmuterNonterminalTreeNode)

            if len(specifier.children) > 1:
                assert isinstance(
                    specifier.children[1], TransmuterNonterminalTreeNode
                )
                symbol.start = specifier.children[1]
            else:
                symbol.start = True

    def process_first(self, symbol: SyntacticSymbol) -> None:
        assert symbol.definition is not None
        assert len(symbol.definition.children) > 1
        assert isinstance(
            symbol.definition.children[1], TransmuterNonterminalTreeNode
        )
        assert len(symbol.definition.children[1].children) > 0
        assert isinstance(
            symbol.definition.children[1].children[0],
            TransmuterNonterminalTreeNode,
        )

        if self.fold is None:
            self.fold = SyntacticFold(
                symbol.definition.children[1].children[0]
            )
        else:
            self.fold.tree = symbol.definition.children[1].children[0]
            self.fold.fold_queue.clear()

        self.fold.visit()
        assert len(self.fold.fold_queue) > 0
        fragment = self.fold.fold_queue[0]

        if fragment is not None:
            for reference in fragment.references:
                if reference.value in self.nonterminal_table.symbols:
                    if len(fragment.references[reference]) > 0:
                        symbol.conditional_first[reference] = (
                            fragment.references[reference]
                        )
                    else:
                        symbol.static_first.append(reference)
