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

from dataclasses import dataclass, field
from typing import ClassVar

from .common import TransmuterCondition, TransmuterPosition, TransmuterException, TransmuterSymbolMatchError
from .lexical import TransmuterLexer, TransmuterTerminal, TransmuterNoTerminalError


transmuter_once: bool = True


class TransmuterNonterminalType:
    ASCEND_PARENTS: set[type["TransmuterNonterminalType"]] = set()

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return False

    @classmethod
    def call(cls, parser: "TransmuterParser", current_terminals: set[TransmuterTerminal | None], ascend: bool = False) -> set[TransmuterTerminal]:
        next_terminals = set()

        for current_terminal in current_terminals:
            next_terminals |= cls.call_single(parser, current_terminal, ascend)

        if len(next_terminals) == 0:
            raise TransmuterSymbolMatchError()

        return next_terminals

    @classmethod
    def call_single(cls, parser: "TransmuterParser", current_terminal: TransmuterTerminal | None, ascend: bool) -> set[TransmuterTerminal]:
        if cls not in parser.memo:
            parser.memo[cls] = {}

        if ascend or current_terminal not in parser.memo[cls]:
            if current_terminal not in parser.memo[cls]:
                parser.memo[cls][current_terminal] = set()

            try:
                initial_memo_len = len(parser.memo[cls][current_terminal])
                parser.memo[cls][current_terminal] |= cls.descend(parser, current_terminal)

                if ascend and initial_memo_len != len(parser.memo[cls][current_terminal]):
                    cls.ascend(parser, current_terminal)
            except TransmuterSymbolMatchError:
                pass

        return parser.memo[cls][current_terminal]

    @classmethod
    def descend(cls, parser: "TransmuterParser", current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        raise NotImplementedError()

    @classmethod
    def ascend(cls, parser: "TransmuterParser", current_terminal: TransmuterTerminal | None) -> None:
        current_terminals = {current_terminal}

        for ascend_parent in cls.ASCEND_PARENTS:
            try:
                ascend_parent.call(parser, current_terminals, True)
            except TransmuterSymbolMatchError:
                pass


@dataclass
class TransmuterParser:
    NONTERMINAL_TYPES: ClassVar[set[type[TransmuterNonterminalType]]]

    lexer: TransmuterLexer
    nonterminal_types_start: type[TransmuterNonterminalType] = field(init=False, repr=False)
    memo: dict[type[TransmuterNonterminalType], dict[TransmuterTerminal | None, set[TransmuterTerminal]]] = field(
        default_factory=dict,
        init=False,
        repr=False
    )

    def __post_init__(self):
        nonterminal_types_start = {nonterminal_type for nonterminal_type in self.NONTERMINAL_TYPES if nonterminal_type.start(self.lexer.conditions)}

        if len(nonterminal_types_start) == 0:
            raise TransmuterNoStartError()

        if len(nonterminal_types_start) > 1:
            raise TransmuterMultipleStartsError()

        self.nonterminal_types_start = nonterminal_types_start.pop()

    def parse(self) -> bool:
        try:
            self.nonterminal_types_start.call(self, {None}, True)
            return True
        except TransmuterNoTerminalError as e:
            print(e)
            return False
        except TransmuterSymbolMatchError:
            return False


class TransmuterSyntacticError(TransmuterException):
    def __init__(self, filename: str, position: TransmuterPosition, description: str) -> None:
        super().__init__(filename, position, "Syntactic Error", description)


class TransmuterNoStartError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<conditions>", TransmuterPosition(0, 0, 0), "Could not match any starting symbol from given conditions.")


class TransmuterMultipleStartsError(TransmuterSyntacticError):
    def __init__(self) -> None:
        super().__init__("<conditions>", TransmuterPosition(0, 0, 0), "Matched multiple starting symbols from given conditions.")
