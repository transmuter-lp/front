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

from dataclasses import dataclass

from ....semantic.common import TransmuterNonterminalTreeNode
from ....semantic.symbol_table import TransmuterSymbolTable


@dataclass
class AetherFileFold:
    symbol_table: TransmuterSymbolTable[TransmuterNonterminalTreeNode]

    @staticmethod
    def indent(value: str) -> str:
        return f"    {value.replace('\n', '\n    ')}"

    def fold(self) -> str:
        raise NotImplementedError()


class AetherCommonFileFold(AetherFileFold):
    def fold(self) -> str:
        conditions = []

        for name, _ in self.symbol_table:
            conditions.append(self.fold_condition(name))

        return self.fold_file(conditions)

    def fold_file(self, conditions: list[str]) -> str:
        raise NotImplementedError()

    def fold_condition(self, name: str) -> str:
        raise NotImplementedError()
