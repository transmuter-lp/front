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

from typing import NamedTuple


class TransmuterCondition:
    pass


class TransmuterPosition(NamedTuple):
    index_: int
    line: int
    column: int


class TransmuterException(Exception):
    def __init__(self, filename: str, position: TransmuterPosition, type_: str, description: str) -> None:
        super().__init__(f"{filename}:{position.line}:{position.column}: {type_}: {description}")
