# This file is part of Alchemist Front-end
# Copyright (C) 2021  Natan Junges <natanajunges@gmail.com>
#
# Alchemist Front-end is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alchemist Front-end is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Alchemist Front-end.  If not, see <https://www.gnu.org/licenses/>.

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

def process_non_printable(input: str, position: int, page: int, line: int, col: int) -> Optional[IgnoreToken]:
    token: IgnoreToken = IgnoreToken(page, line, col, input[position])

    if input[position] == "\t":
        token.end_col = col + 8 - (col + 7) % 8
    elif input[position] == "\n":
        token.end_line = line + 1
        token.end_col = 1
    elif input[position] == "\v":
        token.end_line = line + 1
        token.end_col = col
    elif input[position] == "\f":
        token.end_page = page + 1
        token.end_line = 1
        token.end_col = 1
    elif input[position] == " ":
        pass
    else:
        return None

    return token

def lexer_run(filepath: str, input: str, terminals: list[Union[type[Terminal], tuple[str, Callable[[str, str, int, int, int, int], Terminal]]]], id_chars: str = "_") -> Optional[list[Terminal]]:
    input = input.replace("\r\n", "\n")
    input = input.replace("\n\r", "\n")
    input = input.replace("\r", "\n")
    terminals = sorted(terminals, key = lambda terminal: (str(terminal) if isinstance(terminal, _TerminalMeta) else terminal[0]) + "\U0010FFFF")
    tokens: list[Terminal] = []
    page: int = 1
    line: int = 1
    col: int = 1
    position: int = 0

    while position < len(input):
        try:
            token_added: bool = False

            for terminal in terminals:
                if isinstance(terminal, _TerminalMeta):
                    if input[position:position + len(terminal)] == str(terminal):
                        if (not str(terminal)[-1].isalnum() and str(terminal)[-1] not in id_chars) or position + len(terminal) >= len(input) or (not input[position + len(terminal)].isalnum() and input[position + len(terminal)] not in id_chars):
                            tokens.append(terminal(page, line, col))
                            position += len(tokens[-1])
                            col += len(tokens[-1])
                            token_added = True

                        break
                    elif input[position:position + len(terminal)] + "\U0010FFFF" < str(terminal) + "\U0010FFFF":
                        break
                elif input[position:position + len(terminal[0])] == terminal[0]:
                    token: Terminal = terminal[1](filepath, input, position, page, line, col)

                    if not isinstance(token, IgnoreToken):
                        tokens.append(token)

                    position += len(token)
                    page = token.end_page
                    line = token.end_line
                    col = token.end_col
                    token_added = True
                    break
                elif input[position:position + len(terminal[0])] + "\U0010FFFF" < terminal[0] + "\U0010FFFF":
                    break

            if not token_added:
                if input[position].isalpha() or input[position] in id_chars:
                    end: int = position + 1

                    while end < len(input) and (input[end].isalnum() or input[end] in id_chars):
                        end += 1

                    tokens.append(Identifier(page, line, col, input[position:end]))
                    position += len(tokens[-1])
                    col += len(tokens[-1])
                elif not input[position].isprintable() or input[position] == " ":
                    token: Optional[IgnoreToken] = process_non_printable(input, position, page, line, col)

                    if token != None:
                        page = token.end_page
                        line = token.end_line
                        col = token.end_col

                    position += 1
                else:
                    raise InvalidStringLexerException(filepath, page, line, col, input[position:])
        except InvalidStringLexerException as e:
            print(e)
            return None

    return tokens
