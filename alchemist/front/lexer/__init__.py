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

from typing import Optional, Union, TYPE_CHECKING
import re

from .. import ASTNode, CompilerError

if TYPE_CHECKING:
    from ..parser import Production


class InputHandler:
    def __init__(self, _input: str, filename: str = "<stdin>",
                 startpos: int = 0, endpos: Optional[int] = None,
                 newline: str = "\n"):
        self.input: str = _input
        self.filename: str = filename
        self.startpos: int = startpos
        self.endpos: int = endpos if endpos is not None else len(_input)
        self.newline: str = newline
        self.position: int = 0
        self.poslc: tuple[int, int] = (1, 1)
        self.advance(startpos)

    def get_state(self) -> tuple[int, int, int]:
        return (self.position, self.poslc[0], self.poslc[1])

    def set_state(self, state: tuple[int, int, int]):
        self.position = state[0]
        self.poslc = (state[1], state[2])

    def __getitem__(self, key: slice) -> str:
        return self.input[max(self.startpos, key.start):
                          min(key.stop, self.endpos)]

    def advance(self, length: int):
        if self.position + length <= self.endpos:
            lines = self.input.count(self.newline, self.position,
                                     self.position + length)

            if lines > 0:
                self.poslc = (self.poslc[0] + lines, (self.position + length -
                              self.input.rfind(self.newline, self.position,
                                               self.position + length)))
            else:
                self.poslc = (self.poslc[0], self.poslc[1] + length)

            self.position += length


class Terminal(ASTNode):
    pattern: Union[str, re.Pattern] = ""
    index: int = 0
    weight: float = .0

    @classmethod
    def key(cls) -> tuple[bool, int, float]:
        if isinstance(cls.pattern, str):
            return (True, -len(cls.pattern), -cls.weight)

        # re.Pattern
        return (False, cls.index, -cls.weight)

    def __init__(self, parent: Optional["Production"], _input: InputHandler):
        if isinstance(self.pattern, str):
            if (_input[_input.position: _input.position + len(self.pattern)] !=
                    self.pattern):
                raise CompilerTerminalError(_input, self)
        elif isinstance(self.pattern, re.Pattern):
            match = self.pattern.match(_input.input, _input.position,
                                       _input.endpos)

            if not match:
                raise CompilerTerminalError(_input, self)

            self._str: str = match[0]

        super().__init__(parent)
        self.state: tuple[int, int, int] = _input.get_state()
        self.next: Optional[Terminal] = None

    @property
    def str(self) -> str:
        return self.pattern if isinstance(self.pattern, str) else self._str


class Start(Terminal):
    def __init__(self, _input: InputHandler):
        ASTNode.__init__(self, None)
        self.state = _input.get_state()
        self.next = None


TerminalList = list[Union[
    type[Terminal],
    tuple[type[Terminal], "TerminalList"]
]]


class Lexer:
    terminals: TerminalList = []
    ignored: list[re.Pattern] = []

    @staticmethod
    def sort(terminals: TerminalList) -> TerminalList:
        terminals.sort(key=lambda t: t[0].key() if isinstance(t, tuple) else
                       t.key())
        return terminals

    def __init__(self, _input: InputHandler):
        self.input: InputHandler = _input
        self.token: Terminal = Start(_input)

    def get_state(self) -> Terminal:
        return self.token

    def set_state(self, state: Terminal):
        self.token = state
        self.input.set_state(state.state)

    def ignore(self):
        while True:
            for pattern in self.ignored:
                match = pattern.match(self.input.input, self.input.position,
                                      self.input.endpos)

                if match:
                    self.input.advance(len(match[0]))
                    break
            else:
                break

    def match_terminal(self, parent: Optional["Production"],
                       terminals: TerminalList,
                       token: Optional[Terminal] = None):
        for term in terminals:
            if isinstance(term, tuple):
                terminal, children = term
            else:
                terminal = term
                children = []

            try:
                ctoken = terminal(parent, self.input)
                assert token is None or len(ctoken.str) == len(token.str)
                return ctoken, children
            except (CompilerTerminalError, AssertionError):
                pass

        return None

    def next_token(self, parent: Optional["Production"]) -> Terminal:
        if self.token.next is not None:
            self.set_state(self.token.next)
            return self.token

        self.ignore()

        if self.input.position == self.input.endpos:
            raise CompilerEOIError(self.input)

        match = self.match_terminal(parent, self.terminals)

        if match is None:
            raise CompilerNoTerminalError(self.input)

        token, children = match

        while True:
            match = self.match_terminal(parent, children, token)

            if match is None:
                break

            token, children = match

        self.input.advance(len(token.str))
        token.state = self.input.get_state()
        self.token.next = token
        self.token = self.token.next
        return self.token


class CompilerLexicalError(CompilerError):
    pass


class CompilerEOIError(CompilerLexicalError):
    def __init__(self, _input: InputHandler):
        super().__init__(_input, "Unexpected end of input.")


class CompilerNoTerminalError(CompilerLexicalError):
    def __init__(self, _input: InputHandler):
        super().__init__(_input, "Could not match any expected terminal.")


class CompilerTerminalError(CompilerLexicalError):
    def __init__(self, _input: InputHandler, terminal: Terminal):
        super().__init__(_input, "Could not match the expected "
                         f"{terminal.__class__.__name__}.")
