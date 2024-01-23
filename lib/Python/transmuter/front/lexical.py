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

from .common import Condition, Position, TransmuterException


@dataclass(frozen=True)
class TokenType:
    name: str
    optional: bool


@dataclass
class Token:
    types: set[TokenType]
    start_position: Position
    end_position: Position
    value: str
    next: "Token | None" = field(default=None, init=False, repr=False)


@dataclass
class BaseLexer:
    STATE_ACCEPT: ClassVar[int] = 0
    STATES_START: ClassVar[set[int]]
    TOKENTYPES_IGNORE: ClassVar[set[TokenType]]

    input: str
    filename: str
    conditions: set[Condition]
    start: Token | None = field(default=None, init=False, repr=False)

    def next_token(self, current_token: Token | None) -> Token:
        if current_token is None:
            if self.start is None:
                self.start = self.tokenize(Position(0, 1, 1))

            return self.start

        if current_token.next is None:
            current_token.next = self.tokenize(current_token.end_position)

        return current_token.next

    def tokenize(self, start_position: Position) -> Token:
        while True:
            accepted_token_types = set()
            accepted_position = start_position
            current_token_types = set()
            current_position = start_position
            current_states = self.STATES_START

            while current_states:
                if self.STATE_ACCEPT in current_states:
                    accepted_token_types = current_token_types
                    accepted_position = current_position

                if current_position.index_ == len(self.input):
                    if accepted_token_types - self.TOKENTYPES_IGNORE:
                        break

                    raise TransmuterEOIError(self.filename, current_position)

                current_token_types, current_states = self.nfa(self.input[current_position.index_], current_states)
                current_position = Position(
                    current_position.index_ + 1,
                    current_position.line + (1 if self.input[current_position.index_] == "\n" else 0),
                    1 if self.input[current_position.index_] == "\n" else current_position.column + 1
                )

            if not accepted_token_types:
                raise TransmuterNoTokenError(self.filename, current_position)

            if accepted_token_types - self.TOKENTYPES_IGNORE:
                return Token(
                    accepted_token_types - self.TOKENTYPES_IGNORE,
                    start_position,
                    accepted_position,
                    self.input[start_position.index_:accepted_position.index_]
                )

            start_position = accepted_position

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[TokenType], set[int]]:
        raise NotImplementedError()


class TransmuterLexicalError(TransmuterException):
    def __init__(self, filename: str, position: Position, description: str) -> None:
        super().__init__(filename, position, "Lexical Error", description)


class TransmuterEOIError(TransmuterLexicalError):
    def __init__(self, filename: str, position: Position) -> None:
        super().__init__(filename, position, "Unexpected end of input.")


class TransmuterNoTokenError(TransmuterLexicalError):
    def __init__(self, filename: str, position: Position) -> None:
        super().__init__(filename, position, "Could not match any token.")