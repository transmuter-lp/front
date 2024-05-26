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

from .common import ConditionVar, Position, TransmuterException, TransmuterSymbolMatchError


class TerminalTag:
    @staticmethod
    def states_start(conditions: set[type[ConditionVar]]) -> set[int]:
        raise NotImplementedError()

    @staticmethod
    def ignore(conditions: set[type[ConditionVar]]) -> bool:
        return False

    @staticmethod
    def optional(conditions: set[type[ConditionVar]]) -> bool:
        return False

    @classmethod
    def call(cls, lexer: "BaseLexer", current_terminals: set["Terminal | None"]) -> set["Terminal"]:
        next_terminals = set()

        for current_terminal in current_terminals:
            next_terminal = cls.call_single(lexer, current_terminal)

            if next_terminal is not None:
                next_terminals.add(next_terminal)

        if len(next_terminals) == 0:
            raise TransmuterSymbolMatchError()

        return next_terminals

    @classmethod
    def call_single(cls, lexer: "BaseLexer", current_terminal: "Terminal | None") -> "Terminal | None":
        while True:
            next_terminal = lexer.next_terminal(current_terminal)

            if next_terminal is None:
                return None

            if cls not in next_terminal.tags:
                for terminal_tag in next_terminal.tags:
                    if not terminal_tag.optional(lexer.conditions):
                        return None

                current_terminal = next_terminal
                continue

            return next_terminal


@dataclass(eq=False)
class Terminal:
    start_position: Position
    end_position: Position
    tags: set[type[TerminalTag]]
    value: str
    next: "Terminal | None" = field(default=None, init=False, repr=False)


@dataclass
class BaseLexer:
    STATE_ACCEPT: ClassVar[int] = 0
    TERMINAL_TAGS: ClassVar[set[type[TerminalTag]]]

    input: str
    filename: str
    conditions: set[type[ConditionVar]]
    terminal_tags_ignore: set[type[TerminalTag]] = field(init=False, repr=False)
    states_start: set[int] = field(init=False, repr=False)
    start: Terminal | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.terminal_tags_ignore = {terminal_tag for terminal_tag in self.TERMINAL_TAGS if terminal_tag.ignore(self.conditions)}
        self.states_start = set()

        for terminal_tag in self.TERMINAL_TAGS:
            self.states_start |= terminal_tag.states_start(self.conditions)

    def next_terminal(self, current_terminal: Terminal | None) -> Terminal | None:
        if current_terminal is None:
            if self.start is None:
                self.start = self.get_terminal(Position(0, 1, 1))

            return self.start

        if current_terminal.next is None:
            current_terminal.next = self.get_terminal(current_terminal.end_position)

        return current_terminal.next

    def get_terminal(self, start_position: Position) -> Terminal | None:
        while True:
            accepted_terminal_tags = set()
            accepted_position = start_position
            current_terminal_tags = set()
            current_position = start_position
            current_states = self.states_start

            while current_states:
                if self.STATE_ACCEPT in current_states:
                    accepted_terminal_tags = current_terminal_tags
                    accepted_position = current_position

                if current_position.index_ == len(self.input):
                    if accepted_terminal_tags - self.terminal_tags_ignore:
                        break

                    return None

                current_terminal_tags, current_states = self.nfa(self.input[current_position.index_], current_states)
                current_position = Position(
                    current_position.index_ + 1,
                    current_position.line + (0 if self.input[current_position.index_] != "\n" else 1),
                    current_position.column + 1 if self.input[current_position.index_] != "\n" else 1
                )

            if not accepted_terminal_tags:
                raise TransmuterNoTerminalError(self.filename, current_position)

            if accepted_terminal_tags - self.terminal_tags_ignore:
                return Terminal(
                    start_position,
                    accepted_position,
                    accepted_terminal_tags - self.terminal_tags_ignore,
                    self.input[start_position.index_:accepted_position.index_]
                )

            start_position = accepted_position

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[type[TerminalTag]], set[int]]:
        raise NotImplementedError()


class TransmuterLexicalError(TransmuterException):
    def __init__(self, filename: str, position: Position, description: str) -> None:
        super().__init__(filename, position, "Lexical Error", description)


class TransmuterNoTerminalError(TransmuterLexicalError):
    def __init__(self, filename: str, position: Position) -> None:
        super().__init__(filename, position, "Could not match any terminal.")
