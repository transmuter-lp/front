# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2021, 2023, 2024  Natan Junges <natanajunges@gmail.com>
# Copyright (C) 2024, 2025  The Transmuter Project
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
import sys
import warnings

TransmuterConditions = IntFlag
TransmuterCondition = auto


def transmuter_compute_sccs[T](graph: dict[T, set[T]]) -> list[set[T]]:
    # Tarjan's strongly connected components algorithm
    # Index of visited nodes
    visited_index: dict[T, int] = {}
    # Smallest index in stack reachable from nodes
    min_index = {}
    stack = []
    sccs = []

    def compute_scc(v: T) -> None:
        index = len(visited_index)
        min_index[v] = index
        visited_index[v] = index
        stack.append(v)

        for w in graph[v]:
            if w not in visited_index:
                compute_scc(w)
                min_index[v] = min(min_index[v], min_index[w])
            elif w in stack:
                min_index[v] = min(min_index[v], visited_index[w])
            # If w is not in stack, (v, w) points to an SCC already
            # found

        # If v is a root node
        if min_index[v] == index:
            scc = set()
            w = stack.pop()
            scc.add(w)

            while w != v:
                w = stack.pop()
                scc.add(w)

            sccs.append(scc)

    for v in graph:
        if v not in visited_index:
            compute_scc(v)

    return sccs


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

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}"

    def copy(self) -> "TransmuterPosition":
        return TransmuterPosition(
            self.filename, self.index_, self.line, self.column
        )

    def update(self, position: "TransmuterPosition") -> None:
        self.filename = position.filename
        self.index_ = position.index_
        self.line = position.line
        self.column = position.column


class TransmuterException(Exception):
    def __init__(
        self, position: TransmuterPosition, type_: str, description: str
    ) -> None:
        super().__init__(f"{position}: {type_}: {description}")


class TransmuterExceptionHandler:
    def __enter__(self) -> "TransmuterExceptionHandler":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        _,
    ) -> bool:
        if exc_type is not None and issubclass(exc_type, TransmuterException):
            print(exc_value, file=sys.stderr)
            return True

        return False


class TransmuterWarning(TransmuterException, Warning):
    pass


def transmuter_init_warnings() -> None:
    original_formatwarning = warnings.formatwarning

    def formatwarning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        line: str | None = None,
    ) -> str:
        if issubclass(category, TransmuterWarning):
            return f"{str(message)}\n"

        return original_formatwarning(
            message, category, filename, lineno, line
        )

    warnings.formatwarning = formatwarning
    warnings.filterwarnings("always", category=TransmuterWarning)
