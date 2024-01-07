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
class BaseLexer:
    input: str
    filename: str
    condition: Flag
    start: Token | None = field(default=None, init=False, repr=False)

    def advance_position(self, position: tuple[int, int, int]) -> tuple[int, int, int]:
        if position[0] < len(self.input):
            if self.input[position[0]] == "\n":
                position = (position[0] + 1, position[1] + 1, 1)
            else:
                position = (position[0] + 1, position[1], position[2] + 1)

        return position

    def next_token(self, current_token: Token | None) -> Token:
        if current_token is None:
            if self.start is None:
                self.start = self.tokenize((0, 1, 1))

            return self.start

        if current_token.next is None:
            current_token.next = self.tokenize(current_token.end_position)

        return current_token.next

    def tokenize(self, start_position: tuple[int, int, int]) -> Token:
        raise NotImplementedError()
