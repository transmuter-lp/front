# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2024  Natan Junges <natanajunges@gmail.com>
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

from ..common import TransmuterConditions
from ..lexical import TransmuterTerminalTag, TransmuterLexer
from .common import Conditions


class Whitespace(TransmuterTerminalTag):
    STATES_START = 1 << 0 | 1 << 1 | 1 << 2

    @staticmethod
    def ignore(conditions: TransmuterConditions) -> bool:
        return True

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 1:22
        if 1 << 0 & current_states and (char in "\t "):
            state_accept = True
            next_states |= 1 << 0 | 1 << 1 | 1 << 2

        # 1:30
        if 1 << 1 & current_states and (char == "\r"):
            next_states |= 1 << 2

        # 1:34
        if 1 << 2 & current_states and (char == "\n"):
            state_accept = True
            next_states |= 1 << 0 | 1 << 1 | 1 << 2

        return (state_accept, next_states)


class Identifier(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 3:23
        if 1 << 0 & current_states and ("A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            state_accept = True
            next_states |= 1 << 1

        # 3:33
        if 1 << 1 & current_states and ("0" <= char <= "9" or "A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            state_accept = True
            next_states |= 1 << 1

        return (state_accept, next_states)


class Colon(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 5:18
        if char == ":":
            state_accept = True

        return (state_accept, next_states)


class Semicolon(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 7:12
        if char == ";":
            state_accept = True

        return (state_accept, next_states)


class CommercialAt(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 9:25
        if char == "@":
            state_accept = True

        return (state_accept, next_states)


class LeftParenthesis(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 11:18
        if char == "(":
            state_accept = True

        return (state_accept, next_states)


class RightParenthesis(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 13:19
        if char == ")":
            state_accept = True

        return (state_accept, next_states)


class VerticalLine(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 15:15
        if char == "|":
            state_accept = True

        return (state_accept, next_states)


class Solidus(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 17:20
        if char == "/":
            state_accept = True

        return (state_accept, next_states)


class DoubleVerticalLine(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 19:21
        if 1 << 0 & current_states and (char == "|"):
            next_states |= 1 << 1

        # 19:24
        if 1 << 1 & current_states and (char == "|"):
            state_accept = True

        return (state_accept, next_states)


class Comma(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 21:18
        if char == ",":
            state_accept = True

        return (state_accept, next_states)


class DoubleAmpersand(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 23:28
        if 1 << 0 & current_states and (char == "&"):
            next_states |= 1 << 1

        # 23:29
        if 1 << 1 & current_states and (char == "&"):
            state_accept = True

        return (state_accept, next_states)


class PlusSign(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 25:19
        if char == "+":
            state_accept = True

        return (state_accept, next_states)


class HyphenMinus(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 27:32
        if char == "-":
            state_accept = True

        return (state_accept, next_states)


class Ignore(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def negatives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        negatives = {Identifier}
        return negatives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 29:40
        if 1 << 0 & current_states and (char == "i"):
            next_states |= 1 << 1

        # 29:41
        if 1 << 1 & current_states and (char == "g"):
            next_states |= 1 << 2

        # 29:42
        if 1 << 2 & current_states and (char == "n"):
            next_states |= 1 << 3

        # 29:43
        if 1 << 3 & current_states and (char == "o"):
            next_states |= 1 << 4

        # 29:44
        if 1 << 4 & current_states and (char == "r"):
            next_states |= 1 << 5

        # 29:45
        if 1 << 5 & current_states and (char == "e"):
            state_accept = True

        return (state_accept, next_states)


class Start(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def negatives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        negatives = {Identifier}
        return negatives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 31:31
        if 1 << 0 & current_states and (char == "s"):
            next_states |= 1 << 1

        # 31:32
        if 1 << 1 & current_states and (char == "t"):
            next_states |= 1 << 2

        # 31:33
        if 1 << 2 & current_states and (char == "a"):
            next_states |= 1 << 3

        # 31:34
        if 1 << 3 & current_states and (char == "r"):
            next_states |= 1 << 4

        # 31:35
        if 1 << 4 & current_states and (char == "t"):
            state_accept = True

        return (state_accept, next_states)


class Asterisk(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 33:19
        if char == "*":
            state_accept = True

        return (state_accept, next_states)


class QuestionMark(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 35:23
        if char == "?":
            state_accept = True

        return (state_accept, next_states)


class ExpressionRange(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 37:26
        if 1 << 0 & current_states and (char == "{"):
            next_states |= 1 << 1 | 1 << 2

        # 37:30
        if 1 << 1 & current_states and (char == "0"):
            next_states |= 1 << 4 | 1 << 8

        # 37:34
        if 1 << 2 & current_states and ("1" <= char <= "9"):
            next_states |= 1 << 3 | 1 << 4 | 1 << 8

        # 37:40
        if 1 << 3 & current_states and ("0" <= char <= "9"):
            next_states |= 1 << 3 | 1 << 4 | 1 << 8

        # 37:49
        if 1 << 4 & current_states and (char == ","):
            next_states |= 1 << 5 | 1 << 6 | 1 << 8

        # 37:52
        if 1 << 5 & current_states and (char == "0"):
            next_states |= 1 << 8

        # 37:56
        if 1 << 6 & current_states and ("1" <= char <= "9"):
            next_states |= 1 << 7 | 1 << 8

        # 37:62
        if 1 << 7 & current_states and ("0" <= char <= "9"):
            next_states |= 1 << 7 | 1 << 8

        # 37:73
        if 1 << 8 & current_states and (char == "}"):
            state_accept = True

        return (state_accept, next_states)


class LeftCurlyBracket(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 39:29
        if char == "{":
            state_accept = True

        return (state_accept, next_states)


class LeftCurlyBracketSolidus(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 41:36
        if 1 << 0 & current_states and (char == "{"):
            next_states |= 1 << 1

        # 41:39
        if 1 << 1 & current_states and (char == "/"):
            state_accept = True

        return (state_accept, next_states)


class RightCurlyBracket(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 43:30
        if char == "}":
            state_accept = True

        return (state_accept, next_states)


class OrdChar(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 45:18
        if not ("\000" <= char <= "\037" or char in " $()*+.;?[\\^{|\177"):
            state_accept = True

        return (state_accept, next_states)


class QuotedChar(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 47:21
        if 1 << 0 & current_states and (char == "\\"):
            next_states |= 1 << 1 | 1 << 2

        # 47:25
        if 1 << 1 & current_states and (char in " $()*+.;?[\\^abfnrtv{|"):
            state_accept = True

        # 47:52
        if 1 << 2 & current_states and (char in "01"):
            next_states |= 1 << 3

        # 47:57:1
        if 1 << 3 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 4

        # 47:57:2
        if 1 << 4 & current_states and ("0" <= char <= "7"):
            state_accept = True

        return (state_accept, next_states)


class FullStop(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 49:19
        if char == ".":
            state_accept = True

        return (state_accept, next_states)


class BracketExpression(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 51:28
        if 1 << 0 & current_states and (char == "["):
            next_states |= 1 << 1 | 1 << 2 | 1 << 3 | 1 << 8

        # 51:32
        if 1 << 1 & current_states and (char == "^"):
            next_states |= 1 << 2 | 1 << 3

        # 51:37
        if 1 << 2 & current_states and (not ("\000" <= char <= "\037" or char in "\\^\177")):
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:59
        if 1 << 3 & current_states and (char == "\\"):
            next_states |= 1 << 4 | 1 << 5

        # 51:63
        if 1 << 4 & current_states and (char in "\\abfnrtv"):
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:77
        if 1 << 5 & current_states and (char in "01"):
            next_states |= 1 << 6

        # 51:82:1
        if 1 << 6 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 7

        # 51:82:2
        if 1 << 7 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:95
        if 1 << 8 & current_states and (char == "^"):
            next_states |= 1 << 9

        # 51:98
        if 1 << 9 & current_states and (char == "^"):
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:103
        if 1 << 10 & current_states and (char == "-"):
            next_states |= 1 << 11 | 1 << 12

        # 51:106
        if 1 << 11 & current_states and (not (char == "]" or "\000" <= char <= "\037" or char in "\\\177")):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:128
        if 1 << 12 & current_states and (char == "\\"):
            next_states |= 1 << 13 | 1 << 14

        # 51:132
        if 1 << 13 & current_states and (char in "\\abfnrtv"):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:146
        if 1 << 14 & current_states and (char in "01"):
            next_states |= 1 << 15

        # 51:151:1
        if 1 << 15 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 16

        # 51:151:2
        if 1 << 16 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:166
        if 1 << 17 & current_states and (not (char == "]" or "\000" <= char <= "\037" or char in "\\\177-")):
            next_states |= 1 << 17 | 1 << 18 | 1 << 23 | 1 << 30 | 1 << 31

        # 51:189
        if 1 << 18 & current_states and (char == "\\"):
            next_states |= 1 << 19 | 1 << 20

        # 51:193
        if 1 << 19 & current_states and (char in "\\abfnrtv"):
            next_states |= 1 << 17 | 1 << 18 | 1 << 23 | 1 << 30 | 1 << 31

        # 51:207
        if 1 << 20 & current_states and (char in "01"):
            next_states |= 1 << 21

        # 51:212:1
        if 1 << 21 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 22

        # 51:212:2
        if 1 << 22 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 17 | 1 << 18 | 1 << 23 | 1 << 30 | 1 << 31

        # 51:224
        if 1 << 23 & current_states and (char == "-"):
            next_states |= 1 << 24 | 1 << 25

        # 51:227
        if 1 << 24 & current_states and (not (char == "]" or "\000" <= char <= "\037" or char in "\\\177")):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:249
        if 1 << 25 & current_states and (char == "\\"):
            next_states |= 1 << 26 | 1 << 27

        # 51:253
        if 1 << 26 & current_states and (char in "\\abfnrtv"):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:267
        if 1 << 27 & current_states and (char in "01"):
            next_states |= 1 << 28

        # 51:272:1
        if 1 << 28 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 29

        # 51:272:2
        if 1 << 29 & current_states and ("0" <= char <= "7"):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        # 51:287
        if 1 << 30 & current_states and (char == "-"):
            next_states |= 1 << 31

        # 51:290
        if 1 << 31 & current_states and (char == "]"):
            state_accept = True

        return (state_accept, next_states)


class ExclamationMark(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 53:28
        if char == "!":
            state_accept = True

        return (state_accept, next_states)


class LeftSquareBracket(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 55:30
        if char == "[":
            state_accept = True

        return (state_accept, next_states)


class LeftSquareBracketSolidus(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 57:37
        if 1 << 0 & current_states and (char == "["):
            next_states |= 1 << 1

        # 57:40
        if 1 << 1 & current_states and (char == "/"):
            state_accept = True

        return (state_accept, next_states)


class RightSquareBracket(TransmuterTerminalTag):
    STATES_START = 1 << 0

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        state_accept = False
        next_states = 0

        # 59:31
        if char == "]":
            state_accept = True

        return (state_accept, next_states)


class Lexer(TransmuterLexer):
    TERMINAL_TAGS = {Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, PlusSign, HyphenMinus, Ignore, Start, Asterisk, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket}
