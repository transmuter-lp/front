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

from ..common import TransmuterCondition
from ..lexical import TransmuterTerminalTag, TransmuterLexer
from .common import lexical, syntactic


class Whitespace(TransmuterTerminalTag):
    STATES_START = {1, 2, 3}

    @staticmethod
    def ignore(conditions: set[type[TransmuterCondition]]) -> bool:
        return True


class Identifier(TransmuterTerminalTag):
    STATES_START = {4}

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class Colon(TransmuterTerminalTag):
    STATES_START = {6}

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class Semicolon(TransmuterTerminalTag):
    STATES_START = {7}


class CommercialAt(TransmuterTerminalTag):
    STATES_START = {8}

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class LeftParenthesis(TransmuterTerminalTag):
    STATES_START = {9}


class RightParenthesis(TransmuterTerminalTag):
    STATES_START = {10}


class VerticalLine(TransmuterTerminalTag):
    STATES_START = {11}


class Solidus(TransmuterTerminalTag):
    STATES_START = {12}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class DoubleVerticalLine(TransmuterTerminalTag):
    STATES_START = {13}


class Comma(TransmuterTerminalTag):
    STATES_START = {15}

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class DoubleAmpersand(TransmuterTerminalTag):
    STATES_START = {16}

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class PlusSign(TransmuterTerminalTag):
    STATES_START = {18}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class HyphenMinus(TransmuterTerminalTag):
    STATES_START = {19}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class Ignore(TransmuterTerminalTag):
    STATES_START = {20}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives

    @staticmethod
    def negatives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        negatives = {Identifier}
        return negatives


class Start(TransmuterTerminalTag):
    STATES_START = {26}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions

    @staticmethod
    def negatives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        negatives = {Identifier}
        return negatives


class Asterisk(TransmuterTerminalTag):
    STATES_START = {31}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class QuestionMark(TransmuterTerminalTag):
    STATES_START = {32}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class ExpressionRange(TransmuterTerminalTag):
    STATES_START = {33}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class LeftCurlyBracket(TransmuterTerminalTag):
    STATES_START = {42}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class LeftCurlyBracketSolidus(TransmuterTerminalTag):
    STATES_START = {43}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class RightCurlyBracket(TransmuterTerminalTag):
    STATES_START = {45}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class OrdChar(TransmuterTerminalTag):
    STATES_START = {46}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class QuotedChar(TransmuterTerminalTag):
    STATES_START = {47}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class FullStop(TransmuterTerminalTag):
    STATES_START = {52}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class BracketExpression(TransmuterTerminalTag):
    STATES_START = {53}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return lexical in conditions


class ExclamationMark(TransmuterTerminalTag):
    STATES_START = {85}

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type[TransmuterTerminalTag]]:
        positives = {OrdChar}
        return positives


class LeftSquareBracket(TransmuterTerminalTag):
    STATES_START = {86}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class LeftSquareBracketSolidus(TransmuterTerminalTag):
    STATES_START = {87}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class RightSquareBracket(TransmuterTerminalTag):
    STATES_START = {89}

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return syntactic in conditions


class Lexer(TransmuterLexer):
    TERMINAL_TAGS = {Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, PlusSign, HyphenMinus, Ignore, Start, Asterisk, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket}

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[type[TransmuterTerminalTag]], set[int]]:
        current_terminal_tags = set()
        next_states = set()

        # Whitespace
        # 1:22
        if 1 in current_states and (char in {"\t", " "}):
            current_terminal_tags.add(Whitespace)
            next_states |= {self.STATE_ACCEPT, 1, 2, 3}

        # 1:30
        if 2 in current_states and (char == "\r"):
            next_states |= {3}

        # 1:34
        if 3 in current_states and (char == "\n"):
            current_terminal_tags.add(Whitespace)
            next_states |= {self.STATE_ACCEPT, 1, 2, 3}

        # Identifier
        # 3:23
        if 4 in current_states and ("A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_terminal_tags.add(Identifier)
            next_states |= {self.STATE_ACCEPT, 5}

        # 3:33
        if 5 in current_states and ("0" <= char <= "9" or "A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_terminal_tags.add(Identifier)
            next_states |= {self.STATE_ACCEPT, 5}

        # Colon
        # 5:18
        if 6 in current_states and (char == ":"):
            current_terminal_tags.add(Colon)
            next_states |= {self.STATE_ACCEPT}

        # Semicolon
        # 7:12
        if 7 in current_states and (char == ";"):
            current_terminal_tags.add(Semicolon)
            next_states |= {self.STATE_ACCEPT}

        # CommercialAt
        # 9:25
        if 8 in current_states and (char == "@"):
            current_terminal_tags.add(CommercialAt)
            next_states |= {self.STATE_ACCEPT}

        # LeftParenthesis
        # 11:18
        if 9 in current_states and (char == "("):
            current_terminal_tags.add(LeftParenthesis)
            next_states |= {self.STATE_ACCEPT}

        # RightParenthesis
        # 13:19
        if 10 in current_states and (char == ")"):
            current_terminal_tags.add(RightParenthesis)
            next_states |= {self.STATE_ACCEPT}

        # VerticalLine
        # 15:15
        if 11 in current_states and (char == "|"):
            current_terminal_tags.add(VerticalLine)
            next_states |= {self.STATE_ACCEPT}

        # Solidus
        # 17:20
        if 12 in current_states and (char == "/"):
            current_terminal_tags.add(Solidus)
            next_states |= {self.STATE_ACCEPT}

        # DoubleVerticalLine
        # 19:21
        if 13 in current_states and (char == "|"):
            next_states |= {14}

        # 19:24
        if 14 in current_states and (char == "|"):
            current_terminal_tags.add(DoubleVerticalLine)
            next_states |= {self.STATE_ACCEPT}

        # Comma
        # 21:18
        if 15 in current_states and (char == ","):
            current_terminal_tags.add(Comma)
            next_states |= {self.STATE_ACCEPT}

        # DoubleAmpersand
        # 23:28
        if 16 in current_states and (char == "&"):
            next_states |= {17}

        # 23:29
        if 17 in current_states and (char == "&"):
            current_terminal_tags.add(DoubleAmpersand)
            next_states |= {self.STATE_ACCEPT}

        # PlusSign
        # 25:19
        if 18 in current_states and (char == "+"):
            current_terminal_tags.add(PlusSign)
            next_states |= {self.STATE_ACCEPT}

        # HyphenMinus
        # 27:32
        if 19 in current_states and (char == "-"):
            current_terminal_tags.add(HyphenMinus)
            next_states |= {self.STATE_ACCEPT}

        # Ignore
        # 29:40
        if 20 in current_states and (char == "i"):
            next_states |= {21}

        # 29:41
        if 21 in current_states and (char == "g"):
            next_states |= {22}

        # 29:42
        if 22 in current_states and (char == "n"):
            next_states |= {23}

        # 29:43
        if 23 in current_states and (char == "o"):
            next_states |= {24}

        # 29:44
        if 24 in current_states and (char == "r"):
            next_states |= {25}

        # 29:45
        if 25 in current_states and (char == "e"):
            current_terminal_tags.add(Ignore)
            next_states |= {self.STATE_ACCEPT}

        # Start
        # 31:31
        if 26 in current_states and (char == "s"):
            next_states |= {27}

        # 31:32
        if 27 in current_states and (char == "t"):
            next_states |= {28}

        # 31:33
        if 28 in current_states and (char == "a"):
            next_states |= {29}

        # 31:34
        if 29 in current_states and (char == "r"):
            next_states |= {30}

        # 31:35
        if 30 in current_states and (char == "t"):
            current_terminal_tags.add(Start)
            next_states |= {self.STATE_ACCEPT}

        # Asterisk
        # 33:19
        if 31 in current_states and (char == "*"):
            current_terminal_tags.add(Asterisk)
            next_states |= {self.STATE_ACCEPT}

        # QuestionMark
        # 35:23
        if 32 in current_states and (char == "?"):
            current_terminal_tags.add(QuestionMark)
            next_states |= {self.STATE_ACCEPT}

        # ExpressionRange
        # 37:26
        if 33 in current_states and (char == "{"):
            next_states |= {34, 35}

        # 37:30
        if 34 in current_states and (char == "0"):
            next_states |= {37, 41}

        # 37:34
        if 35 in current_states and ("1" <= char <= "9"):
            next_states |= {36, 37, 41}

        # 37:40
        if 36 in current_states and ("0" <= char <= "9"):
            next_states |= {36, 37, 41}

        # 37:49
        if 37 in current_states and (char == ","):
            next_states |= {38, 39, 41}

        # 37:52
        if 38 in current_states and (char == "0"):
            next_states |= {41}

        # 37:56
        if 39 in current_states and ("1" <= char <= "9"):
            next_states |= {40, 41}

        # 37:62
        if 40 in current_states and ("0" <= char <= "9"):
            next_states |= {40, 41}

        # 37:73
        if 41 in current_states and (char == "}"):
            current_terminal_tags.add(ExpressionRange)
            next_states |= {self.STATE_ACCEPT}

        # LeftCurlyBracket
        # 39:29
        if 42 in current_states and (char == "{"):
            current_terminal_tags.add(LeftCurlyBracket)
            next_states |= {self.STATE_ACCEPT}

        # LeftCurlyBracketSolidus
        # 41:36
        if 43 in current_states and (char == "{"):
            next_states |= {44}

        # 41:39
        if 44 in current_states and (char == "/"):
            current_terminal_tags.add(LeftCurlyBracketSolidus)
            next_states |= {self.STATE_ACCEPT}

        # RightCurlyBracket
        # 43:30
        if 45 in current_states and (char == "}"):
            current_terminal_tags.add(RightCurlyBracket)
            next_states |= {self.STATE_ACCEPT}

        # OrdChar
        # 45:18
        if 46 in current_states and (not ("\000" <= char <= "\037" or char in {" ", "$", "(", ")", "*", "+", ".", ";", "?", "[", "\\", "^", "{", "|", "\177"})):
            current_terminal_tags.add(OrdChar)
            next_states |= {self.STATE_ACCEPT}

        # QuotedChar
        # 47:21
        if 47 in current_states and (char == "\\"):
            next_states |= {48, 49}

        # 47:25
        if 48 in current_states and (char in {" ", "$", "(", ")", "*", "+", ".", ";", "?", "[", "\\", "^", "a", "b", "f", "n", "r", "t", "v", "{", "|"}):
            current_terminal_tags.add(QuotedChar)
            next_states |= {self.STATE_ACCEPT}

        # 47:52
        if 49 in current_states and (char in {"0", "1"}):
            next_states |= {50}

        # 47:57:1
        if 50 in current_states and ("0" <= char <= "7"):
            next_states |= {51}

        # 47:57:2
        if 51 in current_states and ("0" <= char <= "7"):
            current_terminal_tags.add(QuotedChar)
            next_states |= {self.STATE_ACCEPT}

        # FullStop
        # 49:19
        if 52 in current_states and (char == "."):
            current_terminal_tags.add(FullStop)
            next_states |= {self.STATE_ACCEPT}

        # BracketExpression
        # 51:28
        if 53 in current_states and (char == "["):
            next_states |= {54, 55, 56, 61}

        # 51:32
        if 54 in current_states and (char == "^"):
            next_states |= {55, 56}

        # 51:37
        if 55 in current_states and (not ("\000" <= char <= "\037" or char in {"\\", "^", "\177"})):
            next_states |= {63, 70, 71, 83, 84}

        # 51:59
        if 56 in current_states and (char == "\\"):
            next_states |= {57, 58}

        # 51:63
        if 57 in current_states and (char in {"\\", "a", "b", "f", "n", "r", "t", "v"}):
            next_states |= {63, 70, 71, 83, 84}

        # 51:77
        if 58 in current_states and (char in {"0", "1"}):
            next_states |= {59}

        # 51:82:1
        if 59 in current_states and ("0" <= char <= "7"):
            next_states |= {60}

        # 51:82:2
        if 60 in current_states and ("0" <= char <= "7"):
            next_states |= {63, 70, 71, 83, 84}

        # 51:95
        if 61 in current_states and (char == "^"):
            next_states |= {62}

        # 51:98
        if 62 in current_states and (char == "^"):
            next_states |= {63, 70, 71, 83, 84}

        # 51:103
        if 63 in current_states and (char == "-"):
            next_states |= {64, 65}

        # 51:106
        if 64 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char in {"\\", "\177"})):
            next_states |= {70, 71, 83, 84}

        # 51:128
        if 65 in current_states and (char == "\\"):
            next_states |= {66, 67}

        # 51:132
        if 66 in current_states and (char in {"\\", "a", "b", "f", "n", "r", "t", "v"}):
            next_states |= {70, 71, 83, 84}

        # 51:146
        if 67 in current_states and (char in {"0", "1"}):
            next_states |= {68}

        # 51:151:1
        if 68 in current_states and ("0" <= char <= "7"):
            next_states |= {69}

        # 51:151:2
        if 69 in current_states and ("0" <= char <= "7"):
            next_states |= {70, 71, 83, 84}

        # 51:166
        if 70 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char in {"\\", "\177", "-"})):
            next_states |= {70, 71, 76, 83, 84}

        # 51:189
        if 71 in current_states and (char == "\\"):
            next_states |= {72, 73}

        # 51:193
        if 72 in current_states and (char in {"\\", "a", "b", "f", "n", "r", "t", "v"}):
            next_states |= {70, 71, 76, 83, 84}

        # 51:207
        if 73 in current_states and (char in {"0", "1"}):
            next_states |= {74}

        # 51:212:1
        if 74 in current_states and ("0" <= char <= "7"):
            next_states |= {75}

        # 51:212:2
        if 75 in current_states and ("0" <= char <= "7"):
            next_states |= {70, 71, 76, 83, 84}

        # 51:224
        if 76 in current_states and (char == "-"):
            next_states |= {77, 78}

        # 51:227
        if 77 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char in {"\\", "\177"})):
            next_states |= {70, 71, 83, 84}

        # 51:249
        if 78 in current_states and (char == "\\"):
            next_states |= {79, 80}

        # 51:253
        if 79 in current_states and (char in {"\\", "a", "b", "f", "n", "r", "t", "v"}):
            next_states |= {70, 71, 83, 84}

        # 51:267
        if 80 in current_states and (char in {"0", "1"}):
            next_states |= {81}

        # 51:272:1
        if 81 in current_states and ("0" <= char <= "7"):
            next_states |= {82}

        # 51:272:2
        if 82 in current_states and ("0" <= char <= "7"):
            next_states |= {70, 71, 83, 84}

        # 51:287
        if 83 in current_states and (char == "-"):
            next_states |= {84}

        # 51:290
        if 84 in current_states and (char == "]"):
            current_terminal_tags.add(BracketExpression)
            next_states |= {self.STATE_ACCEPT}

        # ExclamationMark
        # 53:28
        if 85 in current_states and (char == "!"):
            current_terminal_tags.add(ExclamationMark)
            next_states |= {self.STATE_ACCEPT}

        # LeftSquareBracket
        # 55:30
        if 86 in current_states and (char == "["):
            current_terminal_tags.add(LeftSquareBracket)
            next_states |= {self.STATE_ACCEPT}

        # LeftSquareBracketSolidus
        # 57:37
        if 87 in current_states and (char == "["):
            next_states |= {88}

        # 57:40
        if 88 in current_states and (char == "/"):
            current_terminal_tags.add(LeftSquareBracketSolidus)
            next_states |= {self.STATE_ACCEPT}

        # RightSquareBracket
        # 59:31
        if 89 in current_states and (char == "]"):
            current_terminal_tags.add(RightSquareBracket)
            next_states |= {self.STATE_ACCEPT}

        return (current_terminal_tags, next_states)
