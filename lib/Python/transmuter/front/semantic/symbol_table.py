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

from .common import TransmuterSyntacticElement


@dataclass
class TransmuterSymbol:
    definition: TransmuterSyntacticElement | None = field(
        default=None, init=False, repr=False
    )
    declarations: list[TransmuterSyntacticElement] = field(
        default_factory=list, init=False, repr=False
    )
    references: list[TransmuterSyntacticElement] = field(
        default_factory=list, init=False, repr=False
    )


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
        if name not in self.symbols and (
            self.can_shadow or not self.parent or not self.parent.has(name)
        ):
            symbol = TransmuterSymbol()
            self.symbols[name] = symbol
            return symbol

        return self.get(name)

    def has(self, name: str) -> bool:
        if name in self.symbols:
            return True

        if not self.parent:
            return False

        return self.parent.has(name)

    def get(self, name: str) -> TransmuterSymbol:
        if name in self.symbols:
            return self.symbols[name]

        assert self.parent
        return self.parent.get(name)
