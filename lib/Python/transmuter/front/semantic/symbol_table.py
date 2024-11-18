# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
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

from collections.abc import Iterator
from dataclasses import dataclass, field

from ..common import TransmuterPosition
from .common import TransmuterSyntacticElement, TransmuterSemanticError


@dataclass
class TransmuterSymbol:
    definition: TransmuterSyntacticElement | None = field(
        default=None, init=False
    )
    declarations: list[TransmuterSyntacticElement] = field(
        default_factory=list, init=False
    )
    references: list[TransmuterSyntacticElement] = field(
        default_factory=list, init=False
    )

    def __repr__(self) -> str:
        return repr((self.definition, self.declarations, self.references))


@dataclass
class TransmuterSymbolTable:
    parent: "TransmuterSymbolTable | None" = None
    can_shadow: bool = True
    symbols: dict[str, TransmuterSymbol] = field(
        default_factory=dict, init=False, repr=False
    )

    def __iter__(self) -> Iterator[tuple[str, TransmuterSymbol]]:
        return iter(self.symbols.items())

    def add_get(self, name: str) -> TransmuterSymbol:
        table: TransmuterSymbolTable | None = self

        if name not in self.symbols and (
            self.can_shadow
            or not self.parent
            or not (table := self.parent.table(name))
        ):
            symbol = TransmuterSymbol()
            self.symbols[name] = symbol
            return symbol

        assert table
        return table.get(name)

    def table(self, name: str) -> "TransmuterSymbolTable | None":
        if name in self.symbols:
            return self

        if not self.parent:
            return None

        return self.parent.table(name)

    def get(self, name: str) -> TransmuterSymbol:
        return self.symbols[name]


class TransmuterDuplicateSymbolDefinitionError(TransmuterSemanticError):
    def __init__(
        self,
        position: TransmuterPosition,
        name: str,
        first_position: TransmuterPosition,
    ) -> None:
        super().__init__(
            position,
            f"Duplicate definition of symbol '{name}', first defined at {first_position.filename}:{first_position.line}:{first_position.column}.",
        )


class TransmuterUndefinedSymbolError(TransmuterSemanticError):
    def __init__(
        self,
        position: TransmuterPosition,
        name: str,
        first_position: TransmuterPosition,
    ) -> None:
        super().__init__(
            position,
            f"Undefined symbol '{name}', first referenced at {first_position.filename}:{first_position.line}:{first_position.column}.",
        )
