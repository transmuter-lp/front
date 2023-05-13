# This file is part of the Alchemist front-end libraries
# Copyright (C) 2023  Natan Junges <natanajunges@gmail.com>
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

import re

from .. import ASTNode, CompilerError


class InputHandler:
    def __init__(self, _input: str, filename: str = "<stdin>", startpos: int = 0, endpos: int | None = None, newline: str = "\n") -> None:
        self.input: str = _input
        self.filename: str = filename
        self.__startpos: int = startpos
        self.endpos: int = endpos if endpos is not None else len(_input)
        self.__newline: str = newline
        self.position: int = 0
        self.poslc: tuple[int, int] = 1, 1
        self.advance(startpos)

    def get_state(self) -> tuple[int, int, int]:
        return self.position, self.poslc[0], self.poslc[1]

    def set_state(self, state: tuple[int, int, int]) -> None:
        self.position = state[0]
        self.poslc = state[1], state[2]

    def __getitem__(self, key: slice) -> str:
        return self.input[max(self.__startpos, key.start):min(key.stop, self.endpos)]

    def advance(self, length: int) -> None:
        if self.position + length <= self.endpos:
            lines: int = self.input.count(self.__newline, self.position, self.position + length)

            if lines > 0:
                self.poslc = self.poslc[0] + lines, self.position + length - self.input.rfind(self.__newline, self.position, self.position + length)
            else:
                self.poslc = self.poslc[0], self.poslc[1] + length

            self.position += length


class Terminal(ASTNode):
    _pattern: str | re.Pattern = ""
    _index: int = 0
    _weight: float = 0.0

    @classmethod
    def key(cls) -> tuple[bool, int, float]:
        if isinstance(cls._pattern, str):
            return True, -len(cls._pattern), -cls._weight

        # re.Pattern
        return False, cls._index, -cls._weight

    def __init__(self, _input: InputHandler) -> None:
        if isinstance(self._pattern, str):
            if _input[_input.position:_input.position + len(self._pattern)] != self._pattern:
                raise _CompilerTerminalError(_input, self)
        else:  # re.Pattern
            match: re.Match[str] | None = self._pattern.match(_input.input, _input.position, _input.endpos)  # pylint: disable=E1101

            if not match:
                raise _CompilerTerminalError(_input, self)

            self.__str: str = match[0]

        self.start: tuple[int, int, int] = _input.get_state()
        self.end: tuple[int, int, int] = self.start
        self.next: Terminal | None = None

    @property
    def str(self) -> str:
        return self._pattern if isinstance(self._pattern, str) else self.__str

    def accept(self, _input: InputHandler) -> None:
        _input.advance(len(self.str))
        self.end = _input.get_state()


class _Start(Terminal):
    def __init__(self, _input: InputHandler) -> None:  # pylint: disable=W0231
        self.start = _input.get_state()
        self.end = self.start
        self.next = None


_TerminalList = list[type[Terminal] | tuple[type[Terminal], "_TerminalList"]]


class Lexer:
    _terminals: _TerminalList = []
    _ignored: list[re.Pattern] = []

    @staticmethod
    def sort(terminals: _TerminalList) -> _TerminalList:
        terminals.sort(key=lambda t: t[0].key() if isinstance(t, tuple) else t.key())
        return terminals

    def __init__(self, _input: InputHandler) -> None:
        self.input: InputHandler = _input
        self.__token: Terminal = _Start(_input)

    def get_state(self) -> Terminal:
        return self.__token

    def set_state(self, state: Terminal) -> None:
        self.__token = state
        self.input.set_state(state.end)

    def __ignore(self) -> None:
        while True:
            for pattern in self._ignored:
                match: re.Match[str] | None = pattern.match(self.input.input, self.input.position, self.input.endpos)

                if match:
                    self.input.advance(len(match[0]))
                    break
            else:
                break

    def __match_terminal(self, terminals: _TerminalList, token: Terminal | None = None) -> tuple[Terminal, _TerminalList] | None:
        for term in terminals:
            terminal: type[Terminal]
            children: _TerminalList

            if isinstance(term, tuple):
                terminal, children = term
            else:  # type[Terminal]
                terminal = term
                children = []

            try:
                ctoken: Terminal = terminal(self.input)
                assert token is None or len(ctoken.str) == len(token.str)
                return ctoken, children
            except (_CompilerTerminalError, AssertionError):
                pass

        return None

    def next_token(self) -> Terminal:
        if self.__token.next is not None:
            self.set_state(self.__token.next)
            return self.__token

        self.__ignore()

        if self.input.position == self.input.endpos:
            raise CompilerEOIError(self.input)

        match: tuple[Terminal, _TerminalList] | None = self.__match_terminal(self._terminals)

        if match is None:
            raise CompilerNoTerminalError(self.input)

        token: Terminal
        children: _TerminalList
        token, children = match

        while True:
            match = self.__match_terminal(children, token)

            if match is None:
                break

            token, children = match

        token.accept(self.input)
        self.__token.next = token
        self.__token = self.__token.next
        return self.__token


class _CompilerLexicalError(CompilerError):
    def __init__(self, _input: InputHandler, msg: str) -> None:
        super().__init__(_input, "Lexical Error", msg)


class CompilerEOIError(_CompilerLexicalError):
    def __init__(self, _input: InputHandler) -> None:
        super().__init__(_input, "Unexpected end of input.")


class CompilerNoTerminalError(_CompilerLexicalError):
    def __init__(self, _input: InputHandler) -> None:
        super().__init__(_input, "Could not match any expected terminal.")


class _CompilerTerminalError(_CompilerLexicalError):
    def __init__(self, _input: InputHandler, terminal: Terminal) -> None:
        super().__init__(_input, f"Could not match expected {terminal.__class__.__name__}.")
