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

from .common import Condition, Position, SymbolType, Symbol, TransmuterException


class TerminalType(SymbolType):
    @staticmethod
    def ignore(conditions: set[type[Condition]]) -> bool:
        return False

    @staticmethod
    def optional(conditions: set[type[Condition]]) -> bool:
        return False


@dataclass
class Terminal(Symbol):
    end_position: Position
    types: set[type[TerminalType]]
    value: str
    next: "Terminal | None" = field(default=None, init=False, repr=False)


@dataclass
class BaseLexer:
    STATE_ACCEPT: ClassVar[int] = 0
    STATES_START: ClassVar[set[int]]
    TERMINAL_TYPES: ClassVar[set[type[TerminalType]]]

    input: str
    filename: str
    conditions: set[type[Condition]]
    terminal_types_ignore: set[type[TerminalType]] = field(init=False, repr=False)
    start: Terminal | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.terminal_types_ignore = {terminal_type for terminal_type in self.TERMINAL_TYPES if terminal_type.ignore(self.conditions)}

    def next_terminal(self, current_terminal: Terminal | None) -> Terminal:
        if current_terminal is None:
            if self.start is None:
                self.start = self.get_terminal(Position(0, 1, 1))

            return self.start

        if current_terminal.next is None:
            current_terminal.next = self.get_terminal(current_terminal.end_position)

        return current_terminal.next

    def get_terminal(self, start_position: Position) -> Terminal:
        while True:
            accepted_terminal_types = set()
            accepted_position = start_position
            current_terminal_types = set()
            current_position = start_position
            current_states = self.STATES_START

            while current_states:
                if self.STATE_ACCEPT in current_states:
                    accepted_terminal_types = current_terminal_types
                    accepted_position = current_position

                if current_position.index_ == len(self.input):
                    if accepted_terminal_types - self.terminal_types_ignore:
                        break

                    raise TransmuterEOIError(self.filename, current_position)

                current_terminal_types, current_states = self.nfa(self.input[current_position.index_], current_states)
                current_position = Position(
                    current_position.index_ + 1,
                    current_position.line + (1 if self.input[current_position.index_] == "\n" else 0),
                    1 if self.input[current_position.index_] == "\n" else current_position.column + 1
                )

            if not accepted_terminal_types:
                raise TransmuterNoTerminalError(self.filename, current_position)

            if accepted_terminal_types - self.terminal_types_ignore:
                return Terminal(
                    start_position,
                    accepted_position,
                    accepted_terminal_types - self.terminal_types_ignore,
                    self.input[start_position.index_:accepted_position.index_]
                )

            start_position = accepted_position

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[type[TerminalType]], set[int]]:
        raise NotImplementedError()


class TransmuterLexicalError(TransmuterException):
    def __init__(self, filename: str, position: Position, description: str) -> None:
        super().__init__(filename, position, "Lexical Error", description)


class TransmuterEOIError(TransmuterLexicalError):
    def __init__(self, filename: str, position: Position) -> None:
        super().__init__(filename, position, "Unexpected end of input.")


class TransmuterNoTerminalError(TransmuterLexicalError):
    def __init__(self, filename: str, position: Position) -> None:
        super().__init__(filename, position, "Could not match any terminal.")
