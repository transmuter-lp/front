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

"""
Classes that make up the lexer.
"""

from typing import TYPE_CHECKING

from .. import TreeNode, CompilerError

if TYPE_CHECKING:
    import re

    from .. import TreeVisitor


class InputHandler:
    """
    Reads the input, keeping track of line and column position.
    """

    def __init__(self, _input: str, filename: str = "<stdin>", startpos: int = 0, endpos: int | None = None, newline: str = "\n") -> None:
        """
        :param _input: Input string.
        :param startpos: Index of input to start reading from.
        :param filename: Name of input file, used in error messages.
        :param endpos: Index of input to stop reading from.
        :param newline: Character sequence used as line delimiter.
        """
        self.input: str = _input
        self.filename: str = filename
        self.__startpos: int = startpos
        self.endpos: int = endpos if endpos is not None else len(_input)
        self.__newline: str = newline
        self.position: int = 0
        self.poslc: tuple[int, int] = 1, 1
        self.advance(startpos)

    def __getitem__(self, key: slice) -> str:
        """
        Read input delimited by ``key``, :attr:`__startpos` and :attr:`endpos`.

        :param key: Slice of input to read.
        :returns: Sliced input.
        """
        return self.input[max(self.__startpos, key.start):min(key.stop, self.endpos)]

    def get_state(self) -> tuple[int, int, int]:
        """
        Get its state.

        :returns: Input index, line and column. It is meant to be
            consumed by :method:`set_state`.
        """
        return self.position, self.poslc[0], self.poslc[1]

    def set_state(self, state: tuple[int, int, int]) -> None:
        """
        Set its state.

        :param state: Input index, line and column. It is meant to be
            produced by :method:`get_state`.
        """
        self.position = state[0]
        self.poslc = state[1], state[2]

    def advance(self, length: int) -> None:
        """
        Advance position, computing line and column.

        :param length: Amount of characters to advance in input.
        """
        if self.position + length <= self.endpos:
            lines: int = self.input.count(self.__newline, self.position, self.position + length)

            if lines > 0:
                # <new_column> = <new_position> - <start_of_last_line>
                self.poslc = self.poslc[0] + lines, self.position + length - self.input.rfind(self.__newline, self.position, self.position + length)
            else:
                self.poslc = self.poslc[0], self.poslc[1] + length

            self.position += length


class Terminal(TreeNode):
    """
    Base class for matching and representing terminal nodes.
    """

    soft_match: bool = True
    """
    Whether specialized terminals should match against their parents
    when parsing.
    """
    _pattern: "str | re.Pattern" = ""
    """
    Pattern to match against.
    """
    _index: int = 0
    """
    Matching order of regular expressions.

    This should only be used to ensure correctness of pattern
    matching. For finetuning use :attr:`_weight`.
    """
    _weight: float = 0.0
    """
    Finetuning weight of patterns.

    This should only be used for finetuning. To ensure correctness of
    pattern matching use :attr:`_index`.
    """

    @classmethod
    def key(cls) -> tuple[bool, int, float]:
        """
        Compute sorting key for terminals.

        It uses :attr:`_pattern`, :attr:`_index` and :attr:`_weight`
        as parameters.

        :returns: Combination  of sorting keys.
        """
        if isinstance(cls._pattern, str):
            return True, -len(cls._pattern), -cls._weight

        # re.Pattern
        return False, cls._index, -cls._weight

    def __init__(self, _input: InputHandler) -> None:
        """
        :param _input: Input handler object.
        """
        if isinstance(self._pattern, str):
            if _input[_input.position:_input.position + len(self._pattern)] != self._pattern:
                raise _CompilerTerminalError(_input, self)
        else:  # re.Pattern
            match: "re.Match[str] | None" = self._pattern.match(_input.input, _input.position, _input.endpos)  # pylint: disable=no-member

            if not match:
                raise _CompilerTerminalError(_input, self)

            self.__str: str = match[0]

        self.start: tuple[int, int, int] = _input.get_state()
        self.end: tuple[int, int, int] = self.start
        self.next: Terminal | None = None

    @property
    def str(self) -> str:
        """
        String matched against input.
        """
        return self._pattern if isinstance(self._pattern, str) else self.__str

    def advance(self, _input: InputHandler) -> None:
        """
        Advance input handler and set :attr:`end`.

        :param _input: Input handler object.
        """
        _input.advance(len(self.str))
        self.end = _input.get_state()

    def accept(self, visitor: "TreeVisitor", top_down: bool = True, left_to_right: bool = True) -> None:
        """
        Accept the given tree ``visitor``.

        Call one of ``visitor``'s ``visit_*`` methods on itself and
        traverse its children as specified by ``top_down`` and
        ``left_to_right``. Implements :method:`TreeNode.accept`.

        :param visitor: Tree visitor used to visit the node tree.
        :param top_down: Vertical order of traversal. ``True`` is
            top-down, and ``False`` is bottom-up.
        :param left_to_right: Horizontal order of traversal. ``True``
            is left-to-right, and ``False`` is right-to-left.
        """
        if top_down:
            if left_to_right:
                visitor.visit_top_down_left_to_right(self)
            else:
                visitor.visit_top_down_right_to_left(self)
        else:
            if left_to_right:
                visitor.visit_bottom_up_left_to_right(self)
            else:
                visitor.visit_bottom_up_right_to_left(self)


class _Start(Terminal):
    """
    The starting token.

    It is only used internally by the lexing logic.
    """

    def __init__(self, _input: InputHandler) -> None:  # pylint: disable=super-init-not-called
        """
        :param _input: Input handler object.
        """
        self.start = _input.get_state()
        self.end = self.start
        self.next = None


_TerminalList = list[type[Terminal] | tuple[type[Terminal], "_TerminalList"]]
"""
A terminal list supporting terminal specialization.
"""


class Lexer:
    """
    Base main lexer class.
    """

    _terminals: _TerminalList = []
    """
    List of terminals to match against.
    """
    _ignored: list["re.Pattern"] = []
    """
    List of regular expressions patterns to ignore.
    """

    @staticmethod
    def sort(terminals: _TerminalList) -> _TerminalList:
        """
        Sort list of terminals based on their computed sorting keys.

        :param terminals: List of terminals.
        :returns: Sorted list of terminals.
        """
        terminals.sort(key=lambda t: t[0].key() if isinstance(t, tuple) else t.key())
        return terminals

    def __init__(self, _input: InputHandler) -> None:
        """
        :param _input: Input handler object.
        """
        self.input: InputHandler = _input
        self.__token: Terminal = _Start(_input)

    def get_state(self) -> Terminal:
        """
        Get its state.

        :returns: Token. It is meant to be consumed by
            :method:`set_state`.
        """
        return self.__token

    def set_state(self, state: Terminal) -> None:
        """
        Set its state.

        :param state: Token. It is meant to be produced by
            :method:`get_state`.
        """
        self.__token = state
        self.input.set_state(state.end)

    def next_token(self) -> Terminal:
        """
        Advance to next token, producing it as required.

        :returns: Next token.
        """
        if self.__token.next is not None:
            self.set_state(self.__token.next)
            return self.__token

        while True:
            for pattern in self._ignored:
                ignore: "re.Match[str] | None" = pattern.match(self.input.input, self.input.position, self.input.endpos)

                if ignore:
                    self.input.advance(len(ignore[0]))
                    break
            else:
                break

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

        token.advance(self.input)
        self.__token.next = token
        self.__token = self.__token.next
        return self.__token

    def __match_terminal(self, terminals: _TerminalList, token: Terminal | None = None) -> tuple[Terminal, _TerminalList] | None:
        """
        Match one terminal from given list, producing its token.

        :param terminals: List of terminals to match against.
        :param token: Parent token for terminal specialization.
        :returns: Produced token and children terminals for
            specialization, or None.
        """
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


class _CompilerLexicalError(CompilerError):
    """
    Base exception for all lexical errors.
    """

    def __init__(self, _input: InputHandler, msg: str) -> None:
        """
        :param _input: Input handler object.
        :param msg: Error message.
        """
        super().__init__(_input, "Lexical Error", msg)


class CompilerEOIError(_CompilerLexicalError):
    """
    Exception for unexpected end of input errors.
    """

    def __init__(self, _input: InputHandler) -> None:
        """
        :param _input: Input handler object.
        """
        super().__init__(_input, "Unexpected end of input.")


class CompilerNoTerminalError(_CompilerLexicalError):
    """
    Exception for no terminal matched errors.
    """

    def __init__(self, _input: InputHandler) -> None:
        """
        :param _input: Input handler object.
        """
        super().__init__(_input, "Could not match any expected terminal.")


class _CompilerTerminalError(_CompilerLexicalError):
    """
    Internal exception for terminal not matched errors.

    It is raised whenever a :class:`Terminal` can't be matched against the input.
    """

    def __init__(self, _input: InputHandler, terminal: Terminal) -> None:
        """
        :param _input: Input handler object.
        :param terminal: Terminal object.
        """
        super().__init__(_input, f"Could not match expected {terminal.__class__.__name__}.")
