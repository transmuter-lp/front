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

from .common import AetherCommonFileFold


class CommonFileFold(AetherCommonFileFold):
    def fold_file(self, conditions: list[str]) -> str:
        return f"""from transmuter.front.common import TransmuterConditions, TransmuterCondition


class Conditions(TransmuterConditions):
    {'\n    '.join(conditions)}"""

    def fold_condition(self, name: str) -> str:
        return f"{name} = TransmuterCondition()"
