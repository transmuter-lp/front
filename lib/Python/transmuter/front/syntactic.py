# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2021, 2023, 2024  Natan Junges <natanajunges@gmail.com>
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
from typing import ClassVar, NamedTuple

from .common import (
    TransmuterConditions,
    TransmuterMeta,
    TransmuterPosition,
    TransmuterException,
)
from .lexical import TransmuterTerminalTag, TransmuterTerminal, TransmuterLexer

transmuter_selection: range = range(1)


class TransmuterNonterminalType(metaclass=TransmuterMeta):
    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return False

    @staticmethod
    def ascend_parents(
        conditions: TransmuterConditions,
    ) -> set[type["TransmuterNonterminalType"]]:
        return set()

    @staticmethod
    def descend(
        parser: "TransmuterParser", current_state: "TransmuterParsingState"
    ) -> set["TransmuterParsingState"]:
        raise NotImplementedError()

    @classmethod
    def ascend(
        cls,
        parser: "TransmuterParser",
        current_state: "TransmuterParsingState",
    ) -> None:
        current_states = {current_state}
        assert cls in parser.nonterminal_types_ascend_parents

        for ascend_parent in parser.nonterminal_types_ascend_parents[cls]:
            try:
                parser.call(ascend_parent, current_states, True)
            except TransmuterInternalError:
                pass


class TransmuterParsingState(NamedTuple):
    string: tuple[type[TransmuterTerminalTag | TransmuterNonterminalType], ...]
    start_position: TransmuterPosition
    split_position: TransmuterPosition
    end_terminal: TransmuterTerminal | None

    def __repr__(self) -> str:
        return repr(
            (
                self.string,
                self.start_position,
                self.split_position,
                self.end_terminal,
            )
        )


class TransmuterEPN(NamedTuple):
    type_: type[TransmuterNonterminalType] | None
    state: TransmuterParsingState

    def __repr__(self) -> str:
        return repr((self.type_, self.state))


@dataclass
class TransmuterBSR:
    start: (
        tuple[
            type[TransmuterNonterminalType],
            TransmuterPosition,
            TransmuterPosition,
        ]
        | None
    ) = field(default=None, init=False, repr=False)
    epns: dict[
        tuple[
            type[TransmuterNonterminalType]
            | tuple[
                type[TransmuterTerminalTag | TransmuterNonterminalType], ...
            ],
            TransmuterPosition,
            TransmuterPosition,
        ],
        set[TransmuterEPN],
    ] = field(default_factory=dict, init=False, repr=False)

    def add(self, epn: TransmuterEPN) -> None:
        key = (
            epn.type_ if epn.type_ is not None else epn.state.string,
            epn.state.start_position,
            (
                epn.state.end_terminal.end_position
                if epn.state.end_terminal is not None
                else epn.state.split_position
            ),
        )

        if key not in self.epns:
            self.epns[key] = set()

        self.epns[key].add(epn)

    def left_children(self, parent: TransmuterEPN) -> set[TransmuterEPN]:
        key = (
            parent.state.string[:-1],
            parent.state.start_position,
            parent.state.split_position,
        )

        if (
            parent.state.start_position == parent.state.split_position
            or key not in self.epns
        ):
            return set()

        return self.epns[key]

    def right_children(self, parent: TransmuterEPN) -> set[TransmuterEPN]:
        if parent.state.end_terminal is None:
            return set()

        assert len(parent.state.string) > 0
        key = (
            parent.state.string[-1],
            parent.state.split_position,
            parent.state.end_terminal.end_position,
        )

        if (
            parent.state.split_position
            == parent.state.end_terminal.end_position
            or issubclass(parent.state.string[-1], TransmuterTerminalTag)
            or key not in self.epns
        ):
            return set()

        return self.epns[key]


@dataclass
class TransmuterParser:
    NONTERMINAL_TYPES: ClassVar[set[type[TransmuterNonterminalType]]]

    lexer: TransmuterLexer
    nonterminal_types_start: type[TransmuterNonterminalType] = field(
        init=False, repr=False
    )
    nonterminal_types_ascend_parents: dict[
        type[TransmuterNonterminalType], set[type[TransmuterNonterminalType]]
    ] = field(init=False, repr=False)
    bsr: TransmuterBSR = field(init=False, repr=False)
    eoi: TransmuterTerminal | None = field(
        default=None, init=False, repr=False
    )
    memo: dict[
        tuple[type[TransmuterNonterminalType], TransmuterPosition],
        set[TransmuterTerminal],
    ] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        nonterminal_types_start = None
        self.nonterminal_types_ascend_parents = {}
        self.bsr = TransmuterBSR()

        for nonterminal_type in self.NONTERMINAL_TYPES:
            if (
                nonterminal_type.start(self.lexer.conditions)
                and nonterminal_types_start != nonterminal_type
            ):
                if nonterminal_types_start is not None:
                    raise TransmuterMultipleStartsError()

                nonterminal_types_start = nonterminal_type

            self.nonterminal_types_ascend_parents[nonterminal_type] = (
                nonterminal_type.ascend_parents(self.lexer.conditions)
            )

        if nonterminal_types_start is None:
            raise TransmuterNoStartError()

        self.nonterminal_types_start = nonterminal_types_start

    def parse(self) -> None:
        try:
            self.call(
                self.nonterminal_types_start,
                {
                    TransmuterParsingState(
                        (),
                        self.lexer.start_position,
                        self.lexer.start_position,
                        None,
                    )
                },
                True,
            )
        except TransmuterInternalError:
            pass

        if self.eoi is None:
            return

        key = (
            self.nonterminal_types_start,
            self.lexer.start_position,
            self.eoi.end_position,
        )

        if key not in self.bsr.epns:
            raise TransmuterNoDerivationError(self.eoi.start_position)

        if self.lexer.next_terminal(self.eoi) is not None:
            assert self.eoi.next is not None
            raise TransmuterNoDerivationError(self.eoi.next.start_position)

        self.bsr.start = key

    def call(
        self,
        cls: type[TransmuterTerminalTag | TransmuterNonterminalType],
        current_states: set[TransmuterParsingState],
        ascend: bool = False,
    ) -> set[TransmuterParsingState]:
        next_states = set()

        if issubclass(cls, TransmuterTerminalTag):
            for current_state in current_states:
                next_state = self.call_single_terminal_tag(cls, current_state)

                if next_state is not None:
                    next_states.add(next_state)
        else:
            assert issubclass(cls, TransmuterNonterminalType)

            for current_state in current_states:
                next_states |= self.call_single_nonterminal_type(
                    cls, current_state, ascend
                )

        if len(next_states) == 0:
            raise TransmuterInternalError()

        return next_states

    def call_single_terminal_tag(
        self,
        cls: type[TransmuterTerminalTag],
        current_state: TransmuterParsingState,
    ) -> TransmuterParsingState | None:
        self.bsr.add(TransmuterEPN(None, current_state))
        next_terminal = self.lexer.next_terminal(current_state.end_terminal)

        if next_terminal is not None and (
            self.eoi is None
            or self.eoi.start_position.index_
            < next_terminal.start_position.index_
        ):
            self.eoi = next_terminal

        if next_terminal is None or cls not in next_terminal.tags:
            return None

        return TransmuterParsingState(
            current_state.string + (cls,),
            current_state.start_position,
            (
                current_state.end_terminal.end_position
                if current_state.end_terminal is not None
                else current_state.split_position
            ),
            next_terminal,
        )

    def call_single_nonterminal_type(
        self,
        cls: type[TransmuterNonterminalType],
        current_state: TransmuterParsingState,
        ascend: bool,
    ) -> set[TransmuterParsingState]:
        self.bsr.add(TransmuterEPN(None, current_state))
        current_state_end_position = (
            current_state.end_terminal.end_position
            if current_state.end_terminal is not None
            else current_state.split_position
        )

        if ascend or (cls, current_state_end_position) not in self.memo:
            if (cls, current_state_end_position) not in self.memo:
                self.memo[cls, current_state_end_position] = set()

            initial_memo_len = len(self.memo[cls, current_state_end_position])

            try:
                next_states = cls.descend(
                    self,
                    TransmuterParsingState(
                        (),
                        current_state_end_position,
                        current_state_end_position,
                        current_state.end_terminal,
                    ),
                )
            except TransmuterInternalError:
                pass
            else:
                for next_state in next_states:
                    self.bsr.add(TransmuterEPN(cls, next_state))
                    assert next_state.end_terminal is not None
                    self.memo[cls, current_state_end_position].add(
                        next_state.end_terminal
                    )

                if ascend and initial_memo_len != len(
                    self.memo[cls, current_state_end_position]
                ):
                    cls.ascend(self, current_state)

        return {
            TransmuterParsingState(
                current_state.string + (cls,),
                current_state.start_position,
                current_state_end_position,
                next_terminal,
            )
            for next_terminal in self.memo[cls, current_state_end_position]
        }


class TransmuterSyntacticError(TransmuterException):
    def __init__(self, position: TransmuterPosition, description: str) -> None:
        super().__init__(position, "Syntactic Error", description)


class TransmuterNoStartError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__(
            TransmuterPosition("<conditions>", 0, 0, 0),
            "Could not match any starting symbol from given conditions.",
        )


class TransmuterMultipleStartsError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__(
            TransmuterPosition("<conditions>", 0, 0, 0),
            "Matched multiple starting symbols from given conditions.",
        )


class TransmuterNoDerivationError(TransmuterSyntacticError):
    def __init__(self, position: TransmuterPosition) -> None:
        super().__init__(
            position, "Could not derive input from any production rule."
        )


class TransmuterInternalError(TransmuterNoDerivationError):
    def __init__(self) -> None:
        super().__init__(TransmuterPosition("<internal>", 0, 0, 0))
