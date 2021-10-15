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

class InvalidCharacterLexerError(Exception):
    def __init__(self, filepath: str, line: int, col: int, char: str):
        super().__init__("{}:{}:{}: {}: '{}'.".format(filepath, line, col, self.__class__.__name__, char))

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
    def __init__(self, line: int, col: int):
        self.line: int = line
        self.col: int = col
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
    def __init__(self, line: int, col: int, value: str):
        self.value: str = value
        super().__init__(line, col)
        self.str: str = "Identifier<{}>".format(value)

    def __len__(self) -> int:
        return len(self.value)

class IgnoreToken(Terminal):
    def __init__(self, line: int, col: int, value: str):
        self.value: str = value
        super().__init__(line, col)

    def __len__(self) -> int:
        return len(self.value)

class EOI(Terminal):
    str: str = "end of input"

    def __len__(self) -> int:
        return 0

def process_Identifier(filepath: str, input: str, position: int, line: int, col: int) -> Optional[Identifier]:
    if input[position].isalpha() or input[position] == "_":
        end: int = position + 1

        while end < len(input) and (input[end].isalnum() or input[end] == "_"):
            end += 1

        return Identifier(line, col, input[position:end])

    return None

def process_non_printable(input: str, position: int, line: int, col: int) -> Optional[IgnoreToken]:
    token: IgnoreToken = IgnoreToken(line, col, input[position])

    if input[position] == "\t":
        token.end_col = col + 8 - (col + 7) % 8
    elif input[position] == "\n":
        token.end_line = line + 1
        token.end_col = 1
    elif input[position] in {"\v", "\f"}:
        token.end_line = line + 1
        token.end_col = col
    elif input[position] == " ":
        pass
    else:
        return None

    return token

def lexer_run(filepath: str, input: str, terminals: set[Union[type[Terminal], tuple[str, Callable[[str, str, int, int, int], Terminal]]]], default_handler: Callable[[str, str, int, int, int], Optional[Terminal]] = process_Identifier) -> list[Terminal]:
    input = input.replace("\r\n", "\n")
    input = input.replace("\n\r", "\n")
    input = input.replace("\r", "\n")
    terminals_sorted: list[Union[type[Terminal], tuple[str, Callable[[str, str, int, int, int], Terminal]]]] = sorted(terminals, key = lambda terminal: (str(terminal) if isinstance(terminal, _TerminalMeta) else terminal[0]) + "\U0010FFFF")
    tokens: list[Terminal] = []
    line: int = 1
    col: int = 1
    position: int = 0

    while position < len(input):
        token_added: bool = False

        for terminal in terminals_sorted:
            if isinstance(terminal, _TerminalMeta):
                if input[position:position + len(terminal)] == str(terminal):
                    if (not str(terminal)[-1].isalnum() and str(terminal)[-1] not in id_chars) or position + len(terminal) >= len(input) or (not input[position + len(terminal)].isalnum() and input[position + len(terminal)] not in id_chars):
                        tokens.append(terminal(line, col))
                        position += len(tokens[-1])
                        line = tokens[-1].end_line
                        col = tokens[-1].end_col
                        token_added = True

                    break
                elif input[position:position + len(terminal)] + "\U0010FFFF" < str(terminal) + "\U0010FFFF":
                    break
            elif input[position:position + len(terminal[0])] == terminal[0]:
                token: Terminal = terminal[1](filepath, input, position, line, col)

                if not isinstance(token, IgnoreToken):
                    tokens.append(token)

                position += len(token)
                line = token.end_line
                col = token.end_col
                token_added = True
                break
            elif input[position:position + len(terminal[0])] + "\U0010FFFF" < terminal[0] + "\U0010FFFF":
                break

        if not token_added:
            token: Optional[Terminal] = default_handler(filepath, input, position, line, col)

            if token != None:
                if not isinstance(token, IgnoreToken):
                    tokens.append(token)

                position += len(token)
                line = token.end_line
                col = token.end_col
            elif not input[position].isprintable() or input[position] == " ":
                token = process_non_printable(input, position, line, col)
                position += 1

                if token != None:
                    line = token.end_line
                    col = token.end_col
            else:
                raise InvalidCharacterLexerError(filepath, line, col, input[position])

    return tokens
