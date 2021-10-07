# This file is part of Alchemist.py
# Copyright (C) 2021  Natan Junges <natanajunges@gmail.com>
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

from .lexer import _TerminalMeta, Terminal, EOI
from functools import wraps
from collections.abc import Callable
from typing import Union, Optional

class UnexpectedFirstTokenParserException(Exception):
    def __init__(self, filepath: str, symbol: Callable, token: Terminal, symbols: list[type[Terminal]]):
        super().__init__("{}:{}:{}:{}: {}: '{}' starting {}. Allowed options are: {}.".format(filepath, token.page, token.line, token.col, self.__class__.__name__, token, symbol.__name__, symbols))

class UnexpectedTokenParserException(Exception):
    def __init__(self, filepath: str, token: Terminal, symbol: Optional[type[Terminal]] = None):
        if symbol != None:
            super().__init__("{}:{}:{}:{}: {}: '{}'. Expected '{}'.".format(filepath, token.page, token.line, token.col, self.__class__.__name__, token, symbol))
        else:
            super().__init__("{}:{}:{}:{}: {}: '{}'.".format(filepath, token.page, token.line, token.col, self.__class__.__name__, token))

def self(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args):
        return fn(wrapper, *args)

    return wrapper

def optional(*symbols: list[Union[type[Terminal], Callable[[str, list[Terminal], int], list[Union[type[Terminal], Callable]]]]]) -> Callable[[str, list[Terminal], int], list[Union[type[Terminal], Callable]]]:
    def optional_fn(filepath: str, tokens: list[Terminal], position: int) -> list[Union[type[Terminal], Callable]]:
        symbol: Union[type[Terminal], Callable[[str, list[Terminal], int], list[Union[type[Terminal], Callable]]]] = symbols[0]

        if isinstance(symbol, _TerminalMeta):
            if tokens[position] == symbol:
                return list(symbols)

            return []

        try:
            s: list[Union[type[Terminal], Callable]] = symbol(filepath, tokens, position)

            if len(s) > 0:
                s = s + list(symbols[1:])
                return s
            elif len(symbols) > 1:
                return optional(*symbols[1:])(filepath, tokens, position)
        except UnexpectedFirstTokenParserException:
            pass

        return []

    return optional_fn

def lookahead(*symbols: list[type[Terminal]]) -> Callable[[str, list[Terminal], int], list[type[Terminal]]]:
    def lookahead_fn(filepath: str, tokens: list[Terminal], position: int) -> list[type[Terminal]]:
        if position + len(symbols) > len(tokens):
            return []

        i: int = 0

        while i < len(symbols):
            if tokens[position + i] != symbols[i]:
                return []

            i += 1

        return [symbols[0]]

    return lookahead_fn

def parser_run(filepath: str, tokens: list[Terminal], start: Callable[[str, list[Terminal], int], list[Union[type[Terminal], Callable]]]) -> None:
    stack: list[Union[type[Terminal], Callable[[str, list[Terminal], int], list[Union[type[Terminal], Callable]]]]] = [EOI, start]
    position: int = 0

    try:
        while len(stack) > 0 and position < len(tokens):
            symbol: Union[type[Terminal], Callable[[str, list[Terminal], int], list[Union[type[Terminal], Callable]]]] = stack.pop()

            if isinstance(symbol, _TerminalMeta):
                token: Terminal = tokens[position]

                if token == symbol:
                    position += 1
                else:
                    raise UnexpectedTokenParserException(filepath, token, symbol)
            else:
                symbols: list[Union[type[Terminal], Callable]] = symbol(filepath, tokens, position)
                symbols.reverse()
                stack += symbols

        if len(stack) > 0 and stack[-1] != EOI:
            raise UnexpectedTokenParserException(filepath, EOI(tokens[position - 1].end_page, tokens[position - 1].end_line, tokens[position - 1].end_col), stack[-1] if isinstance(stack[-1], _TerminalMeta) else None)
        elif position < len(tokens) and tokens[position] != EOI:
            raise UnexpectedTokenParserException(filepath, tokens[position], EOI)
    except UnexpectedFirstTokenParserException as e:
        print(e)
    except UnexpectedTokenParserException as e:
        print(e)
