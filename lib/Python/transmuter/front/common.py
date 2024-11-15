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

from dataclasses import dataclass
from enum import auto, IntFlag

TransmuterConditions = IntFlag
TransmuterCondition = auto


class TransmuterMeta(type):
    def __repr__(cls) -> str:
        return repr(cls.__name__)


@dataclass(eq=False)
class TransmuterPosition:
    filename: str
    index_: int
    line: int
    column: int

    def __repr__(self) -> str:
        return repr((self.filename, self.index_, self.line, self.column))

    def copy(self) -> "TransmuterPosition":
        return TransmuterPosition(
            self.filename, self.index_, self.line, self.column
        )


class TransmuterException(Exception):
    def __init__(
        self, position: TransmuterPosition, type_: str, description: str
    ) -> None:
        super().__init__(
            f"{position.filename}:{position.line}:{position.column}: {type_}: {description}"
        )
