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

from collections.abc import Callable
from typing import Union, Optional

class InvalidStringLexerException(Exception):
    def __init__(self, filepath: str, page: int, line: int, col: int, string: str):
        super().__init__("{}:{}:{}:{}: {}: '{}'.".format(filepath, page, line, col, self.__class__.__name__, string))

class _TerminalMeta(type):
    def __str__(self) -> str:
        try:
            return self.str
        except AttributeError:
            return self.__name__

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(str(self))

class Terminal(metaclass = _TerminalMeta):
    def __init__(self, page: int, line: int, col: int):
        self.page: int = page
        self.line: int = line
        self.col: int = col
        self.end_page: int = page
        self.end_line: int = line
        self.end_col: int = col + len(self)

    def __str__(self) -> str:
        try:
            return self.str
        except AttributeError:
            return self.__class__.__name__

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(str(self))

    def __eq__(self, other) -> bool:
        return other == self.__class__ or isinstance(other, self.__class__)

class Identifier(Terminal):
    def __init__(self, page: int, line: int, col: int, value: str):
        self.value: str = value
        super().__init__(page, line, col)
        self.str: str = "Identifier<{}>".format(value)

    def __len__(self) -> int:
        return len(self.value)

class IgnoreToken(Terminal):
    def __init__(self, page: int, line: int, col: int, value: str):
        self.str: str = value
        super().__init__(page, line, col)

class EOI(Terminal):
    str: str = "end of input"

    def __len__(self) -> int:
        return 0

def lexer_run(filepath: str, input: str, terminals: list[Union[type[Terminal], tuple[str, Callable[[str, str, int, int, int, int], Terminal]]]], id_chars: Optional[list[str]] = ["_"]) -> Optional[list[Terminal]]:
    input = input.replace("\r\n", "\n")
    input = input.replace("\n\r", "\n")
    input = input.replace("\r", "\n")
    terminals = sorted(terminals, key = lambda terminal: (str(terminal) if isinstance(terminal, _TerminalMeta) else terminal[0]) + "\177")
    tokens: list[Terminal] = []
    page: int = 1
    line: int = 1
    col: int = 1
    position: int = 0

    while position < len(input):
        if input[position].isprintable() and input[position] != " ":
            try:
                for terminal in terminals:
                    if isinstance(terminal, _TerminalMeta):
                        if input[position:position + len(terminal)] == str(terminal):
                            if (str(terminal)[-1].isalnum() or str(terminal)[-1] in id_chars) and position + len(terminal) < len(input) and (input[position + len(terminal)].isalnum() or input[position + len(terminal)] in id_chars):
                                end: int = position + len(terminal) + 1

                                while end < len(input) and (input[end].isalnum() or input[end] in id_chars):
                                    end += 1

                                tokens.append(Identifier(page, line, col, input[position:end]))
                            else:
                                tokens.append(terminal(page, line, col))

                            position += len(tokens[-1])
                            col += len(tokens[-1])
                            break
                    elif input[position:position + len(terminal[0])] == terminal[0]:
                        token: Terminal = terminal[1](filepath, input, position, page, line, col)

                        if not isinstance(token, IgnoreToken):
                            tokens.append(token)

                        position += len(token)
                        page = token.end_page
                        line = token.end_line
                        col = token.end_col
                        break
                else:
                    if input[position].isalpha() or input[position] in id_chars:
                        end: int = position + 1

                        while end < len(input) and (input[end].isalnum() or input[end] in id_chars):
                            end += 1

                        tokens.append(Identifier(page, line, col, input[position:end]))
                        position += len(tokens[-1])
                        col += len(tokens[-1])
                    else:
                        raise InvalidStringLexerException(filepath, page, line, col, input[position:])
            except InvalidStringLexerException as e:
                print(e)
                return None
        else:
            if input[position] == "\t":
                col += 8 - (col + 7) % 8
            elif input[position] == "\n":
                line += 1
                col = 1
            elif input[position] == "\v":
                line += 1
            elif input[position] == "\f":
                page += 1
                line = 1
                col = 1
            elif input[position] == " ":
                col += 1

            position += 1

    return tokens
