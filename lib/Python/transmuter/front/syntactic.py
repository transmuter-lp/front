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
from typing import ClassVar

from .common import TransmuterCondition, TransmuterPosition, TransmuterException
from .lexical import TransmuterTerminalTag, TransmuterTerminal, TransmuterLexer, TransmuterNoTerminalError


transmuter_once: bool = True


class TransmuterNonterminalType:
    ASCEND_PARENTS: set[type["TransmuterNonterminalType"]] = set()

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return False

    @classmethod
    def descend(cls, parser: "TransmuterParser", current_state: "TransmuterParsingState") -> set["TransmuterParsingState"]:
        raise NotImplementedError()

    @classmethod
    def ascend(cls, parser: "TransmuterParser", current_state: "TransmuterParsingState") -> None:
        current_states = {current_state}

        for ascend_parent in cls.ASCEND_PARENTS:
            try:
                parser.call(ascend_parent, current_states, True)
            except TransmuterSymbolMatchError:
                pass


@dataclass(frozen=True)
class TransmuterParsingState:
    string: tuple[type[TransmuterTerminalTag | TransmuterNonterminalType], ...]
    start_terminal: TransmuterTerminal | None
    split_terminal: TransmuterTerminal | None
    end_terminal: TransmuterTerminal | None


@dataclass(frozen=True)
class TransmuterExtendedPackedNode:
    nonterminal_type: type[TransmuterNonterminalType] | None
    string: tuple[type[TransmuterTerminalTag | TransmuterNonterminalType], ...]
    start_terminal: TransmuterTerminal | None
    split_terminal: TransmuterTerminal | None
    end_terminal: TransmuterTerminal | None


@dataclass
class TransmuterParser:
    NONTERMINAL_TYPES: ClassVar[set[type[TransmuterNonterminalType]]]

    lexer: TransmuterLexer
    nonterminal_types_start: type[TransmuterNonterminalType] = field(init=False, repr=False)
    memo: dict[type[TransmuterNonterminalType], dict[TransmuterTerminal | None, set[TransmuterTerminal]]] = field(
        default_factory=dict,
        init=False,
        repr=False
    )
    bsr: set[TransmuterExtendedPackedNode] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self):
        nonterminal_types_start = {nonterminal_type for nonterminal_type in self.NONTERMINAL_TYPES if nonterminal_type.start(self.lexer.conditions)}

        if len(nonterminal_types_start) == 0:
            raise TransmuterNoStartError()

        if len(nonterminal_types_start) > 1:
            raise TransmuterMultipleStartsError()

        self.nonterminal_types_start = nonterminal_types_start.pop()

    def call(
        self, cls: type[TransmuterTerminalTag | TransmuterNonterminalType], current_states: set[TransmuterParsingState], ascend: bool = False
    ) -> set[TransmuterParsingState]:
        next_states = set()

        if issubclass(cls, TransmuterTerminalTag):
            for current_state in current_states:
                next_state = self.call_single_terminal_tag(cls, current_state)

                if next_state is not None:
                    next_states.add(next_state)
        else:  # TransmuterNonterminalType
            for current_state in current_states:
                next_states |= self.call_single_nonterminal_type(cls, current_state, ascend)

        if len(next_states) == 0:
            raise TransmuterSymbolMatchError()

        return next_states

    def call_single_terminal_tag(self, cls: type[TransmuterTerminalTag], current_state: TransmuterParsingState) -> TransmuterParsingState | None:
        self.bsr.add(TransmuterExtendedPackedNode(
            None, current_state.string, current_state.start_terminal, current_state.split_terminal, current_state.end_terminal
        ))
        current_terminal = current_state.end_terminal

        while True:
            next_terminal = self.lexer.next_terminal(current_terminal)

            if next_terminal is None:
                return None

            if cls not in next_terminal.tags:
                for terminal_tag in next_terminal.tags:
                    if not terminal_tag.optional(self.lexer.conditions):
                        return None

                current_terminal = next_terminal
                continue

            return TransmuterParsingState(current_state.string + (cls, ), current_state.start_terminal, current_state.end_terminal, next_terminal)

    def call_single_nonterminal_type(
        self, cls: type[TransmuterNonterminalType], current_state: TransmuterParsingState, ascend: bool
    ) -> set[TransmuterParsingState]:
        self.bsr.add(TransmuterExtendedPackedNode(
            None, current_state.string, current_state.start_terminal, current_state.split_terminal, current_state.end_terminal
        ))

        if cls not in self.memo:
            self.memo[cls] = {}

        if ascend or current_state.end_terminal not in self.memo[cls]:
            if current_state.end_terminal not in self.memo[cls]:
                self.memo[cls][current_state.end_terminal] = set()

            try:
                initial_memo_len = len(self.memo[cls][current_state.end_terminal])
                next_states = cls.descend(
                    self, TransmuterParsingState((), current_state.end_terminal, current_state.end_terminal, current_state.end_terminal)
                )
                self.bsr |= {
                    TransmuterExtendedPackedNode(
                        cls, next_state.string, next_state.start_terminal, next_state.split_terminal, next_state.end_terminal
                    ) for next_state in next_states
                }
                self.memo[cls][current_state.end_terminal] |= {next_state.end_terminal for next_state in next_states}

                if ascend and initial_memo_len != len(self.memo[cls][current_state.end_terminal]):
                    cls.ascend(self, current_state)
            except TransmuterSymbolMatchError:
                pass

        return {
            TransmuterParsingState(
                current_state.string + (cls, ), current_state.start_terminal, current_state.end_terminal, next_terminal
            ) for next_terminal in self.memo[cls][current_state.end_terminal]
        }

    def parse(self) -> bool:
        try:
            self.call(self.nonterminal_types_start, {TransmuterParsingState((), None, None, None)}, True)
            return True
        except TransmuterNoTerminalError as e:
            print(e)
            return False
        except TransmuterSymbolMatchError:
            return False


class TransmuterSyntacticError(TransmuterException):
    def __init__(self, filename: str, position: TransmuterPosition, description: str) -> None:
        super().__init__(filename, position, "Syntactic Error", description)


class TransmuterNoStartError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<conditions>", TransmuterPosition(0, 0, 0), "Could not match any starting symbol from given conditions.")


class TransmuterMultipleStartsError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<conditions>", TransmuterPosition(0, 0, 0), "Matched multiple starting symbols from given conditions.")


class TransmuterSymbolMatchError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<internal>", TransmuterPosition(0, 0, 0), "Could not match symbol.")
