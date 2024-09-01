# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2021, 2023, 2024  Natan Junges <natanajunges@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass, field
from typing import ClassVar, NamedTuple

from .common import TransmuterConditions, TransmuterMeta, TransmuterPosition, TransmuterException
from .lexical import TransmuterTerminalTag, TransmuterTerminal, TransmuterLexer

transmuter_selection: range = range(1)


class TransmuterNonterminalType(metaclass=TransmuterMeta):
    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return False

    @staticmethod
    def ascend_parents(conditions: TransmuterConditions) -> set[type["TransmuterNonterminalType"]]:
        return set()

    @staticmethod
    def descend(parser: "TransmuterParser", current_state: "TransmuterParsingState") -> set["TransmuterParsingState"]:
        raise NotImplementedError()

    @classmethod
    def ascend(cls, parser: "TransmuterParser", current_state: "TransmuterParsingState") -> None:
        current_states = {current_state}

        for ascend_parent in parser.nonterminal_types_ascend_parents[cls]:
            try:
                parser.call(ascend_parent, current_states, True)
            except TransmuterInternalError:
                pass


class TransmuterExtendedPackedNode(NamedTuple):
    type_: type[TransmuterNonterminalType] | None
    state: "TransmuterParsingState"

    def __repr__(self) -> str:
        return repr((self.type_, self.state))


class TransmuterParsingState(NamedTuple):
    string: tuple[type[TransmuterTerminalTag | TransmuterNonterminalType], ...]
    start_terminal: TransmuterTerminal | None
    split_terminal: TransmuterTerminal | None
    end_terminal: TransmuterTerminal | None

    def __repr__(self) -> str:
        return repr((self.string, self.start_terminal, self.split_terminal, self.end_terminal))


@dataclass
class TransmuterBinarySubtreeRepresentation:
    start: tuple[type[TransmuterNonterminalType],  None, TransmuterTerminal] | None = field(default=None, init=False, repr=False)
    epns: dict[
        tuple[
            type[TransmuterNonterminalType] | tuple[type[TransmuterTerminalTag | TransmuterNonterminalType], ...],
            TransmuterTerminal | None,
            TransmuterTerminal | None
        ],
        set[TransmuterExtendedPackedNode]
    ] = field(default_factory=dict, init=False, repr=False)

    def add(self, epn: TransmuterExtendedPackedNode) -> None:
        key = (epn.type_ or epn.state.string, epn.state.start_terminal, epn.state.end_terminal)

        if key not in self.epns:
            self.epns[key] = set()

        self.epns[key].add(epn)

    def left_children(self, parent: TransmuterExtendedPackedNode) -> set[TransmuterExtendedPackedNode]:
        if parent.state.start_terminal == parent.state.split_terminal:
            return set()

        if len(parent.state.string) == 2:
            if issubclass(parent.state.string[0], TransmuterTerminalTag):
                return set()

            key = (parent.state.string[0], parent.state.start_terminal, parent.state.split_terminal)
        else:
            key = (parent.state.string[:-1], parent.state.start_terminal, parent.state.split_terminal)

        if key not in self.epns:
            return set()

        return self.epns[key]

    def right_children(self, parent: TransmuterExtendedPackedNode) -> set[TransmuterExtendedPackedNode]:
        key = (parent.state.string[-1], parent.state.split_terminal, parent.state.end_terminal)

        if (
            parent.state.split_terminal == parent.state.end_terminal
            or issubclass(parent.state.string[-1], TransmuterTerminalTag)
            or key not in self.epns
        ):
            return set()

        return self.epns[key]

    def cleanup(self) -> None:
        if not self.start:
            return

        current_epns = set(self.epns[self.start])
        epns_kept = set()
        next_epns = {}

        while current_epns:
            epn = current_epns.pop()
            epns_kept.add(epn)
            next_epns, self.epns = self.epns, next_epns
            self.add(epn)
            next_epns, self.epns = self.epns, next_epns
            current_epns |= self.left_children(epn)
            current_epns |= self.right_children(epn)
            current_epns -= epns_kept

        self.epns = next_epns


@dataclass
class TransmuterParser:
    NONTERMINAL_TYPES: ClassVar[set[type[TransmuterNonterminalType]]]

    lexer: TransmuterLexer
    nonterminal_types_start: type[TransmuterNonterminalType] = field(init=False, repr=False)
    nonterminal_types_ascend_parents: dict[type[TransmuterNonterminalType], set[type[TransmuterNonterminalType]]] = field(init=False, repr=False)
    bsr: TransmuterBinarySubtreeRepresentation = field(init=False, repr=False)
    eoi: TransmuterTerminal | None = field(default=None, init=False, repr=False)
    memo: dict[tuple[type[TransmuterNonterminalType], TransmuterTerminal | None], set[TransmuterTerminal]] = field(
        default_factory=dict,
        init=False,
        repr=False
    )

    def __post_init__(self):
        nonterminal_types_start = None
        self.nonterminal_types_ascend_parents = {}
        self.bsr = TransmuterBinarySubtreeRepresentation()

        for nonterminal_type in self.NONTERMINAL_TYPES:
            if nonterminal_type.start(self.lexer.conditions) and nonterminal_types_start != nonterminal_type:
                if nonterminal_types_start:
                    raise TransmuterMultipleStartsError()

                nonterminal_types_start = nonterminal_type

            self.nonterminal_types_ascend_parents[nonterminal_type] = nonterminal_type.ascend_parents(self.lexer.conditions)

        if not nonterminal_types_start:
            raise TransmuterNoStartError()

        self.nonterminal_types_start = nonterminal_types_start

    def parse(self) -> None:
        try:
            self.call(self.nonterminal_types_start, {TransmuterParsingState((), None, None, None)}, True)
        except TransmuterInternalError:
            pass

        if not self.eoi:
            return

        key = (self.nonterminal_types_start, None, self.eoi)

        if key not in self.bsr.epns:
            raise TransmuterNoDerivationError(self.lexer.filename, self.eoi.start_position)

        if self.lexer.next_terminal(self.eoi):
            raise TransmuterNoDerivationError(self.lexer.filename, self.eoi.next.start_position)

        self.bsr.start = key

    def call(
        self, cls: type[TransmuterTerminalTag | TransmuterNonterminalType], current_states: set[TransmuterParsingState], ascend: bool = False
    ) -> set[TransmuterParsingState]:
        next_states = set()

        if issubclass(cls, TransmuterTerminalTag):
            for current_state in current_states:
                next_state = self.call_single_terminal_tag(cls, current_state)

                if next_state:
                    next_states.add(next_state)
        else:  # TransmuterNonterminalType
            for current_state in current_states:
                next_states |= self.call_single_nonterminal_type(cls, current_state, ascend)

        if len(next_states) == 0:
            raise TransmuterInternalError()

        return next_states

    def call_single_terminal_tag(self, cls: type[TransmuterTerminalTag], current_state: TransmuterParsingState) -> TransmuterParsingState | None:
        self.bsr.add(TransmuterExtendedPackedNode(None, current_state))
        next_terminal = self.lexer.next_terminal(current_state.end_terminal)

        if next_terminal and (not self.eoi or self.eoi.start_position.index_ < next_terminal.start_position.index_):
            self.eoi = next_terminal

        if not next_terminal or cls not in next_terminal.tags:
            return None

        return TransmuterParsingState(current_state.string + (cls, ), current_state.start_terminal, current_state.end_terminal, next_terminal)

    def call_single_nonterminal_type(
        self, cls: type[TransmuterNonterminalType], current_state: TransmuterParsingState, ascend: bool
    ) -> set[TransmuterParsingState]:
        self.bsr.add(TransmuterExtendedPackedNode(None, current_state))

        if ascend or (cls, current_state.end_terminal) not in self.memo:
            if (cls, current_state.end_terminal) not in self.memo:
                self.memo[cls, current_state.end_terminal] = set()

            initial_memo_len = len(self.memo[cls, current_state.end_terminal])

            try:
                next_states = cls.descend(
                    self, TransmuterParsingState((), current_state.end_terminal, current_state.end_terminal, current_state.end_terminal)
                )
            except TransmuterInternalError:
                pass
            else:
                for next_state in next_states:
                    self.bsr.add(TransmuterExtendedPackedNode(cls, next_state))
                    self.memo[cls, current_state.end_terminal].add(next_state.end_terminal)

                if ascend and initial_memo_len != len(self.memo[cls, current_state.end_terminal]):
                    cls.ascend(self, current_state)

        return {
            TransmuterParsingState(
                current_state.string + (cls, ), current_state.start_terminal, current_state.end_terminal, next_terminal
            ) for next_terminal in self.memo[cls, current_state.end_terminal]
        }


class TransmuterSyntacticError(TransmuterException):
    def __init__(self, filename: str, position: TransmuterPosition, description: str) -> None:
        super().__init__(filename, position, "Syntactic Error", description)


class TransmuterNoStartError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<conditions>", TransmuterPosition(0, 0, 0), "Could not match any starting symbol from given conditions.")


class TransmuterMultipleStartsError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<conditions>", TransmuterPosition(0, 0, 0), "Matched multiple starting symbols from given conditions.")


class TransmuterNoDerivationError(TransmuterSyntacticError):
    def __init__(self, filename: str, position: TransmuterPosition) -> None:
        super().__init__(filename, position, "Could not derive input from any production rule.")


class TransmuterInternalError(TransmuterNoDerivationError):
    def __init__(self) -> None:
        super().__init__("<internal>", TransmuterPosition(0, 0, 0))
