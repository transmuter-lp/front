# This file was automatically generated by Aether, the front-end
# generator for the Transmuter language processing infrastructure.

# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2024  Natan Junges <natanajunges@gmail.com>
# Copyright (C) 2024, 2025  The Transmuter Project
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

from transmuter.front.lexical import TransmuterTerminalTag, TransmuterLexer
from .common import Conditions


class Whitespace(TransmuterTerminalTag):
    STATES_START = 1 << 0 | 1 << 1 | 1 << 2

    @staticmethod
    def ignore(conditions):
        return True

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char in "\t ":
            state_accept = True
            next_states |= 1 << 0 | 1 << 1 | 1 << 2

        if 1 << 1 & current_states and char == "\r":
            next_states |= 1 << 2

        if 1 << 2 & current_states and char == "\n":
            state_accept = True
            next_states |= 1 << 0 | 1 << 1 | 1 << 2

        return state_accept, next_states


class Identifier(TransmuterTerminalTag):
    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and (
            "A" <= char <= "Z" or char == "_" or "a" <= char <= "z"
        ):
            state_accept = True
            next_states |= 1 << 1

        if 1 << 1 & current_states and (
            "0" <= char <= "9"
            or "A" <= char <= "Z"
            or char == "_"
            or "a" <= char <= "z"
        ):
            state_accept = True
            next_states |= 1 << 1

        return state_accept, next_states


class Colon(TransmuterTerminalTag):
    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == ":":
            state_accept = True

        return state_accept, next_states


class Semicolon(TransmuterTerminalTag):
    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == ";":
            state_accept = True

        return state_accept, next_states


class CommercialAt(TransmuterTerminalTag):
    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "@":
            state_accept = True

        return state_accept, next_states


class LeftParenthesis(TransmuterTerminalTag):
    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "(":
            state_accept = True

        return state_accept, next_states


class RightParenthesis(TransmuterTerminalTag):
    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == ")":
            state_accept = True

        return state_accept, next_states


class VerticalLine(TransmuterTerminalTag):
    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "|":
            state_accept = True

        return state_accept, next_states


class Solidus(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "/":
            state_accept = True

        return state_accept, next_states


class DoubleVerticalLine(TransmuterTerminalTag):
    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "|":
            next_states |= 1 << 1

        if 1 << 1 & current_states and char == "|":
            state_accept = True

        return state_accept, next_states


class Comma(TransmuterTerminalTag):
    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == ",":
            state_accept = True

        return state_accept, next_states


class DoubleAmpersand(TransmuterTerminalTag):
    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "&":
            next_states |= 1 << 1

        if 1 << 1 & current_states and char == "&":
            state_accept = True

        return state_accept, next_states


class PlusSign(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "+":
            state_accept = True

        return state_accept, next_states


class HyphenMinus(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "-":
            state_accept = True

        return state_accept, next_states


class Ignore(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def negatives(conditions):
        negatives = {Identifier}
        return negatives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "i":
            next_states |= 1 << 1

        if 1 << 1 & current_states and char == "g":
            next_states |= 1 << 2

        if 1 << 2 & current_states and char == "n":
            next_states |= 1 << 3

        if 1 << 3 & current_states and char == "o":
            next_states |= 1 << 4

        if 1 << 4 & current_states and char == "r":
            next_states |= 1 << 5

        if 1 << 5 & current_states and char == "e":
            state_accept = True

        return state_accept, next_states


class Start(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def negatives(conditions):
        negatives = {Identifier}
        return negatives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "s":
            next_states |= 1 << 1

        if 1 << 1 & current_states and char == "t":
            next_states |= 1 << 2

        if 1 << 2 & current_states and char == "a":
            next_states |= 1 << 3

        if 1 << 3 & current_states and char == "r":
            next_states |= 1 << 4

        if 1 << 4 & current_states and char == "t":
            state_accept = True

        return state_accept, next_states


class Asterisk(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "*":
            state_accept = True

        return state_accept, next_states


class QuestionMark(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "?":
            state_accept = True

        return state_accept, next_states


class ExpressionRange(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "{":
            next_states |= 1 << 1 | 1 << 2

        if 1 << 1 & current_states and char == "0":
            next_states |= 1 << 4 | 1 << 8

        if 1 << 2 & current_states and "1" <= char <= "9":
            next_states |= 1 << 3 | 1 << 4 | 1 << 8

        if 1 << 3 & current_states and "0" <= char <= "9":
            next_states |= 1 << 3 | 1 << 4 | 1 << 8

        if 1 << 4 & current_states and char == ",":
            next_states |= 1 << 5 | 1 << 6 | 1 << 8

        if 1 << 5 & current_states and char == "0":
            next_states |= 1 << 8

        if 1 << 6 & current_states and "1" <= char <= "9":
            next_states |= 1 << 7 | 1 << 8

        if 1 << 7 & current_states and "0" <= char <= "9":
            next_states |= 1 << 7 | 1 << 8

        if 1 << 8 & current_states and char == "}":
            state_accept = True

        return state_accept, next_states


class LeftCurlyBracket(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "{":
            state_accept = True

        return state_accept, next_states


class LeftCurlyBracketSolidus(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "{":
            next_states |= 1 << 1

        if 1 << 1 & current_states and char == "/":
            state_accept = True

        return state_accept, next_states


class RightCurlyBracket(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "}":
            state_accept = True

        return state_accept, next_states


class OrdChar(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and not (
            "\000" <= char <= "\037" or char in " $()*+.;?[\\^{|\177"
        ):
            state_accept = True

        return state_accept, next_states


class QuotedChar(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "\\":
            next_states |= 1 << 1 | 1 << 2

        if 1 << 1 & current_states and char in " $()*+.;?[\\^abfnrtv{|":
            state_accept = True

        if 1 << 2 & current_states and char in "01":
            next_states |= 1 << 3

        if 1 << 3 & current_states and "0" <= char <= "7":
            next_states |= 1 << 4

        if 1 << 4 & current_states and "0" <= char <= "7":
            state_accept = True

        return state_accept, next_states


class FullStop(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == ".":
            state_accept = True

        return state_accept, next_states


class BracketExpression(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.lexical in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "[":
            next_states |= 1 << 1 | 1 << 2 | 1 << 3 | 1 << 8

        if 1 << 1 & current_states and char == "^":
            next_states |= 1 << 2 | 1 << 3

        if 1 << 2 & current_states and not (
            "\000" <= char <= "\037" or char in "\\^\177"
        ):
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 3 & current_states and char == "\\":
            next_states |= 1 << 4 | 1 << 5

        if 1 << 4 & current_states and char in "\\abfnrtv":
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 5 & current_states and char in "01":
            next_states |= 1 << 6

        if 1 << 6 & current_states and "0" <= char <= "7":
            next_states |= 1 << 7

        if 1 << 7 & current_states and "0" <= char <= "7":
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 8 & current_states and char == "^":
            next_states |= 1 << 9

        if 1 << 9 & current_states and char == "^":
            next_states |= 1 << 10 | 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 10 & current_states and char == "-":
            next_states |= 1 << 11 | 1 << 12

        if 1 << 11 & current_states and not (
            char == "]" or "\000" <= char <= "\037" or char in "\\\177"
        ):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 12 & current_states and char == "\\":
            next_states |= 1 << 13 | 1 << 14

        if 1 << 13 & current_states and char in "\\abfnrtv":
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 14 & current_states and char in "01":
            next_states |= 1 << 15

        if 1 << 15 & current_states and "0" <= char <= "7":
            next_states |= 1 << 16

        if 1 << 16 & current_states and "0" <= char <= "7":
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 17 & current_states and not (
            char == "]" or "\000" <= char <= "\037" or char in "\\\177-"
        ):
            next_states |= 1 << 17 | 1 << 18 | 1 << 23 | 1 << 30 | 1 << 31

        if 1 << 18 & current_states and char == "\\":
            next_states |= 1 << 19 | 1 << 20

        if 1 << 19 & current_states and char in "\\abfnrtv":
            next_states |= 1 << 17 | 1 << 18 | 1 << 23 | 1 << 30 | 1 << 31

        if 1 << 20 & current_states and char in "01":
            next_states |= 1 << 21

        if 1 << 21 & current_states and "0" <= char <= "7":
            next_states |= 1 << 22

        if 1 << 22 & current_states and "0" <= char <= "7":
            next_states |= 1 << 17 | 1 << 18 | 1 << 23 | 1 << 30 | 1 << 31

        if 1 << 23 & current_states and char == "-":
            next_states |= 1 << 24 | 1 << 25

        if 1 << 24 & current_states and not (
            char == "]" or "\000" <= char <= "\037" or char in "\\\177"
        ):
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 25 & current_states and char == "\\":
            next_states |= 1 << 26 | 1 << 27

        if 1 << 26 & current_states and char in "\\abfnrtv":
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 27 & current_states and char in "01":
            next_states |= 1 << 28

        if 1 << 28 & current_states and "0" <= char <= "7":
            next_states |= 1 << 29

        if 1 << 29 & current_states and "0" <= char <= "7":
            next_states |= 1 << 17 | 1 << 18 | 1 << 30 | 1 << 31

        if 1 << 30 & current_states and char == "-":
            next_states |= 1 << 31

        if 1 << 31 & current_states and char == "]":
            state_accept = True

        return state_accept, next_states


class ExclamationMark(TransmuterTerminalTag):
    @staticmethod
    def positives(conditions):
        positives = {OrdChar}
        return positives

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "!":
            state_accept = True

        return state_accept, next_states


class LeftSquareBracket(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "[":
            state_accept = True

        return state_accept, next_states


class LeftSquareBracketSolidus(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "[":
            next_states |= 1 << 1

        if 1 << 1 & current_states and char == "/":
            state_accept = True

        return state_accept, next_states


class RightSquareBracket(TransmuterTerminalTag):
    @staticmethod
    def start(conditions):
        return Conditions.syntactic in conditions

    @staticmethod
    def nfa(current_states, char):
        state_accept = False
        next_states = 0

        if 1 << 0 & current_states and char == "]":
            state_accept = True

        return state_accept, next_states


class Lexer(TransmuterLexer):
    TERMINAL_TAGS = [
        Whitespace,
        Identifier,
        Colon,
        Semicolon,
        CommercialAt,
        LeftParenthesis,
        RightParenthesis,
        VerticalLine,
        Solidus,
        DoubleVerticalLine,
        Comma,
        DoubleAmpersand,
        PlusSign,
        HyphenMinus,
        Ignore,
        Start,
        Asterisk,
        QuestionMark,
        ExpressionRange,
        LeftCurlyBracket,
        LeftCurlyBracketSolidus,
        RightCurlyBracket,
        OrdChar,
        QuotedChar,
        FullStop,
        BracketExpression,
        ExclamationMark,
        LeftSquareBracket,
        LeftSquareBracketSolidus,
        RightSquareBracket,
    ]
