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

import builtins

from .common import AetherCommonFileFold


def _escape_identifier(value: str) -> str:
    if (
        value
        in (
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "case",
            "class",
            "Conditions",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "False",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "in",
            "import",
            "is",
            "lambda",
            "Lexer",
            "match",
            "None",
            "nonlocal",
            "not",
            "or",
            "Parser",
            "pass",
            "raise",
            "return",
            "TransmuterCondition",
            "TransmuterConditions",
            "TransmuterInternalError",
            "TransmuterLexer",
            "TransmuterLexingState",
            "TransmuterNonterminalType",
            "TransmuterParser",
            "TransmuterParsingState",
            "transmuter_selection",
            "TransmuterTerminalTag",
            "True",
            "try",
            "type",
            "while",
            "with",
            "yield",
        )
        or value in builtins.__dict__
    ):
        return f"{value}_"

    return value


class CommonFileFold(AetherCommonFileFold):
    def fold_file(self, conditions: list[str]) -> str:
        return f"""from transmuter.front.common import TransmuterConditions, TransmuterCondition


class Conditions(TransmuterConditions):
    {'\n    '.join(conditions)}"""

    def fold_condition(self, name: str) -> str:
        return f"{_escape_identifier(name)} = TransmuterCondition()"
