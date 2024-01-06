# Alchemist front-end, front-end libraries and utilities for the Alchemist compiler infrastructure
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
from enum import Flag


@dataclass
class Token:
    type: Flag
    start_position: tuple[int, int, int]
    end_position: tuple[int, int, int]
    value: str
    next: "Token | None" = field(default=None, init=False, repr=False)


@dataclass
class Lexer:
    input: str
    filename: str
    newline: str
    start: Token | None = field(default=None, init=False, repr=False)

    def advance(self, position: tuple[int, int, int], length: int) -> tuple[int, int, int]:
        if position[0] + length <= len(self.input):
            lines = self.input.count(self.newline, position[0], position[0] + length)

            if lines > 0:
                position = (
                    position[0] + length,
                    position[1] + lines,
                    position[0] + length - self.input.rfind(self.newline, position[0], position[0] + length)
                )
            else:
                position = (position[0] + length, position[1], position[2] + length)

        return position

    def next_token(self, token: Token | None) -> Token:
        if token is None:
            if self.start is None:
                self.start = self.tokenize((0, 1, 1))

            return self.start

        if token.next is None:
            token.next = self.tokenize(token.end_position)

        return token.next

    def tokenize(self, position: tuple[int, int, int]) -> Token:
        raise NotImplementedError()
