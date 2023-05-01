# This file is part of the Alchemist front-end libraries
# Copyright (C) 2023  Natan Junges <natanajunges@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Optional, Union
import re

class InputHandler:
    def __init__(self, input: str, filename: str = "<stdin>", startpos: int = 0, endpos: Optional[int] = None, newline: str = "\n"):
        self.input: str = input
        self.filename: str = filename
        self.startpos: int = startpos
        self.endpos: int = endpos if endpos is not None else len(input)
        self.newline: str = newline
        self.position: int = 0
        self.line: int = 1
        self.column: int = 1
        self.advance(startpos)

    def get_state(self) -> tuple[int, int, int]:
        return (self.position, self.line, self.column)

    def set_state(self, state: tuple[int, int, int]):
        self.position, self.line, self.column = state

    def __getitem__(self, key: slice) -> str:
        return self.input[max(self.startpos, key.start) : min(key.stop, self.endpos)]

    def advance(self, length: int):
        if self.position + length <= self.endpos:
            lines = self.input.count(self.newline, self.position, self.position + length)

            if lines > 0:
                self.line += lines
                self.column = self.position + length - self.input.rfind(self.newline, self.position, self.position + length)
            else:
                self.column += length

            self.position += length

from .. import ASTNode

class Terminal(ASTNode):
    pattern: Union[str, re.Pattern] = ""
    index: int = 0
    weight: float = .0

    @classmethod
    def key(cls) -> tuple[bool, int, float]:
        if type(cls.pattern) is str:
            return (True, -len(cls.pattern), -cls.weight)

        # re.Pattern
        return (False, cls.index, -cls.weight)

    def __init__(self, parent: Optional["Production"], input: InputHandler):
        if type(self.pattern) is str:
            if input[input.position : input.position + len(self.pattern)] != self.pattern:
                raise CompilerTerminalError()
        else: # re.Pattern
            match = self.pattern.match(input.input, input.position, input.endpos)

            if not match:
                raise CompilerTerminalError()

            self._str: str = match[0]

        super().__init__(parent)
        self.next: Optional[Terminal] = None

    @property
    def str(self) -> str:
        return self.pattern if type(self.pattern) is str else self._str

class Start(Terminal):
    def __init__(self, input: InputHandler):
        ASTNode.__init__(self, None)
        self.next: Optional[Terminal] = None
        self.state: tuple[int, int, int] = input.get_state()

TerminalList = list[Union[type[Terminal], tuple[type[Terminal], "TerminalList"]]]

class Lexer:
    terminals: TerminalList = []
    ignored: list[re.Pattern] = []

    @staticmethod
    def sort(terminals: TerminalList) -> TerminalList:
        terminals.sort(key = lambda t: t[0].key() if type(t) is tuple else t.key())
        return terminals

    def __init__(self, input: InputHandler):
        self.input: InputHandler = input
        self.token: Terminal = Start(input)

    def get_state(self) -> Terminal:
        return self.token

    def set_state(self, state: Terminal):
        self.token = state
        self.input.set_state(state.state)

    def ignore(self):
        while True:
            for p in self.ignored:
                match = p.match(self.input.input, self.input.position, self.input.endpos)

                if match:
                    self.input.advance(len(match[0]))
                    break
            else:
                break

    def next_token(self, parent: Optional["Production"]) -> Terminal:
        if self.token.next is not None:
            self.set_state(self.token.next)
        else:
            self.ignore()

            if self.input.position == self.input.endpos:
                raise CompilerEOIError(self.input)

            for t in self.terminals:
                try:
                    if type(t) is tuple:
                        terminal, children = t
                        token = terminal(parent, self.input)

                        while True:
                            for c in children:
                                try:
                                    if type(c) is tuple:
                                        te, ch = c
                                        to = te(parent, self.input)
                                        assert len(to.str) == len(token.str)
                                        token = to
                                        children = ch
                                    else:
                                        to = c(parent, self.input)
                                        assert len(to.str) == len(token.str)
                                        token = to
                                        children = []

                                    break
                                except (CompilerTerminalError, AssertionError): pass
                            else:
                                break
                    else:
                        token = t(parent, self.input)

                    break
                except CompilerTerminalError: pass
            else:
                raise CompilerNoTerminalError(self.input)

            self.input.advance(len(token.str))
            token.state: tuple[int, int, int] = self.input.get_state()
            self.token.next = token
            self.token = self.token.next

        return self.token

from .. import CompilerError

class CompilerLexicalError(CompilerError): pass

class CompilerEOIError(CompilerLexicalError):
    def __init__(self, input: InputHandler):
        super().__init__(input, "Unexpected end of input.")

class CompilerNoTerminalError(CompilerLexicalError):
    def __init__(self, input: InputHandler):
        super().__init__(input, "Could not match any expected terminal.")

class CompilerTerminalError(CompilerLexicalError):
    def __init__(self): pass
