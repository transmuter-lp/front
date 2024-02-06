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

from ..common import Condition
from ..lexical import TokenType, BaseLexer
from .common import lexical, syntactic


class Whitespace(TokenType):
    @staticmethod
    def ignore(conditions: set[type[Condition]]) -> bool:
        return True


class OrdChar(TokenType):
    pass


class Identifier(OrdChar):
    pass


class Colon(OrdChar):
    pass


class Semicolon(TokenType):
    pass


class CommercialAt(OrdChar):
    pass


class LeftParenthesis(TokenType):
    pass


class RightParenthesis(TokenType):
    pass


class GreaterThanSign(OrdChar):
    pass


class VerticalLine(TokenType):
    pass


class Solidus(TokenType):
    pass


class DoubleVerticalLine(TokenType):
    pass


class Comma(OrdChar):
    pass


class DoubleAmpersand(OrdChar):
    pass


class Ignore(OrdChar):
    pass


class Optional(OrdChar):
    pass


class Start(TokenType):
    pass


class Asterisk(TokenType):
    pass


class PlusSign(TokenType):
    pass


class QuestionMark(TokenType):
    pass


class ExpressionRange(TokenType):
    pass


class LeftCurlyBracket(TokenType):
    pass


class LeftCurlyBracketSolidus(TokenType):
    pass


class RightCurlyBracket(TokenType):
    pass


class QuotedChar(TokenType):
    pass


class FullStop(TokenType):
    pass


class BracketExpression(TokenType):
    pass


class ExclamationMark(OrdChar):
    pass


class LeftSquareBracket(TokenType):
    pass


class LeftSquareBracketSolidus(TokenType):
    pass


class RightSquareBracket(TokenType):
    pass


class Lexer(BaseLexer):
    STATES_START = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 25, 33, 38, 39, 40, 41, 50, 51, 53, 54, 55, 60, 61, 93, 94, 95, 97}
    TOKENTYPES = {Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, GreaterThanSign, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, Ignore, Optional, Start, Asterisk, PlusSign, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket}

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[type[TokenType]], set[int]]:
        current_token_types = set()
        next_states = set()

        # Whitespace
        # 1:12
        if 1 in current_states and (char == "\t" or char == " "):
            current_token_types |= {Whitespace}
            next_states |= {1, self.STATE_ACCEPT}

        # 1:30
        if 2 in current_states and (char == "\r"):
            next_states |= {3}

        # 1:34
        if 3 in current_states and (char == "\n"):
            current_token_types |= {Whitespace}
            next_states |= {self.STATE_ACCEPT}

        # Identifier
        # 3:22
        if 4 in current_states and not current_token_types & {Ignore, Optional, Start} and ("A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_token_types |= {Identifier, OrdChar}
            next_states |= {5, self.STATE_ACCEPT}

        # 3:31
        if 5 in current_states and not current_token_types & {Ignore, Optional, Start} and ("0" <= char <= "9" or "A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_token_types |= {Identifier, OrdChar}
            next_states |= {5, self.STATE_ACCEPT}

        # Colon
        # 5:17
        if 6 in current_states and (char == ":"):
            current_token_types |= {Colon, OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # Semicolon
        # 7:12
        if 7 in current_states and (char == ";"):
            current_token_types |= {Semicolon}
            next_states |= {self.STATE_ACCEPT}

        # CommercialAt
        # 9:24
        if 8 in current_states and (char == "@"):
            current_token_types |= {CommercialAt, OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # LeftParenthesis
        # 11:18
        if 9 in current_states and (char == "("):
            current_token_types |= {LeftParenthesis}
            next_states |= {self.STATE_ACCEPT}

        # RightParenthesis
        # 13:19
        if 10 in current_states and (char == ")"):
            current_token_types |= {RightParenthesis}
            next_states |= {self.STATE_ACCEPT}

        # GreaterThanSign
        # 15:35
        if 11 in current_states and (lexical in self.conditions) and (char == ">"):
            current_token_types |= {GreaterThanSign, OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # VerticalLine
        # 17:15
        if 12 in current_states and (char == "|"):
            current_token_types |= {VerticalLine}
            next_states |= {self.STATE_ACCEPT}

        # Solidus
        # 19:20
        if 13 in current_states and (syntactic in self.conditions) and (char == "/"):
            current_token_types |= {Solidus}
            next_states |= {self.STATE_ACCEPT}

        # DoubleVerticalLine
        # 21:21
        if 14 in current_states and (char == "|"):
            next_states |= {15}

        # 21:23
        if 15 in current_states and (char == "|"):
            current_token_types |= {DoubleVerticalLine}
            next_states |= {self.STATE_ACCEPT}

        # Comma
        # 23:17
        if 16 in current_states and (char == ","):
            current_token_types |= {Comma, OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # DoubleAmpersand
        # 25:27
        if 17 in current_states and (char == "&"):
            next_states |= {18}

        # 25:28
        if 18 in current_states and (char == "&"):
            current_token_types |= {DoubleAmpersand, OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # Ignore
        # 27:39
        if 19 in current_states and (lexical in self.conditions) and (char == "i"):
            next_states |= {20}

        # 27:40
        if 20 in current_states and (char == "g"):
            next_states |= {21}

        # 27:41
        if 21 in current_states and (char == "n"):
            next_states |= {22}

        # 27:42
        if 22 in current_states and (char == "o"):
            next_states |= {23}

        # 27:43
        if 23 in current_states and (char == "r"):
            next_states |= {24}

        # 27:44
        if 24 in current_states and (char == "e"):
            current_token_types |= {Ignore, OrdChar}
            current_token_types -= {Identifier}
            next_states |= {self.STATE_ACCEPT}

        # Optional
        # 29:41
        if 25 in current_states and (lexical in self.conditions) and (char == "o"):
            next_states |= {26}

        # 29:42
        if 26 in current_states and (char == "p"):
            next_states |= {27}

        # 29:43
        if 27 in current_states and (char == "t"):
            next_states |= {28}

        # 29:44
        if 28 in current_states and (char == "i"):
            next_states |= {29}

        # 29:45
        if 29 in current_states and (char == "o"):
            next_states |= {30}

        # 29:46
        if 30 in current_states and (char == "n"):
            next_states |= {31}

        # 29:47
        if 31 in current_states and (char == "a"):
            next_states |= {32}

        # 29:48
        if 32 in current_states and (char == "l"):
            current_token_types |= {Optional, OrdChar}
            current_token_types -= {Identifier}
            next_states |= {self.STATE_ACCEPT}

        # Start
        # 31:31
        if 33 in current_states and (syntactic in self.conditions) and (char == "s"):
            next_states |= {34}

        # 31:32
        if 34 in current_states and (char == "t"):
            next_states |= {35}

        # 31:33
        if 35 in current_states and (char == "a"):
            next_states |= {36}

        # 31:34
        if 36 in current_states and (char == "r"):
            next_states |= {37}

        # 31:35
        if 37 in current_states and (char == "t"):
            current_token_types |= {Start}
            current_token_types -= {Identifier}
            next_states |= {self.STATE_ACCEPT}

        # Asterisk
        # 33:19
        if 38 in current_states and (lexical in self.conditions) and (char == "*"):
            current_token_types |= {Asterisk}
            next_states |= {self.STATE_ACCEPT}

        # PlusSign
        # 35:19
        if 39 in current_states and (lexical in self.conditions) and (char == "+"):
            current_token_types |= {PlusSign}
            next_states |= {self.STATE_ACCEPT}

        # QuestionMark
        # 37:23
        if 40 in current_states and (lexical in self.conditions) and (char == "?"):
            current_token_types |= {QuestionMark}
            next_states |= {self.STATE_ACCEPT}

        # ExpressionRange
        # 39:26
        if 41 in current_states and (lexical in self.conditions) and (char == "{"):
            next_states |= {42, 43}

        # 39:30
        if 42 in current_states and (char == "0"):
            next_states |= {45, 49}

        # 39:34
        if 43 in current_states and ("1" <= char <= "9"):
            next_states |= {44, 45, 49}

        # 39:39
        if 44 in current_states and ("0" <= char <= "9"):
            next_states |= {44, 45, 49}

        # 39:48
        if 45 in current_states and (char == ","):
            next_states |= {46, 47, 49}

        # 39:51
        if 46 in current_states and (char == "0"):
            next_states |= {49}

        # 39:55
        if 47 in current_states and ("1" <= char <= "9"):
            next_states |= {48, 49}

        # 39:60
        if 48 in current_states and ("0" <= char <= "9"):
            next_states |= {48, 49}

        # 39:71
        if 49 in current_states and (char == "}"):
            current_token_types |= {ExpressionRange}
            next_states |= {self.STATE_ACCEPT}

        # LeftCurlyBracket
        # 41:29
        if 50 in current_states and (syntactic in self.conditions) and (char == "{"):
            current_token_types |= {LeftCurlyBracket}
            next_states |= {self.STATE_ACCEPT}

        # LeftCurlyBracketSolidus
        # 43:36
        if 51 in current_states and (syntactic in self.conditions) and (char == "{"):
            next_states |= {52}

        # 43:38
        if 52 in current_states and (char == "/"):
            current_token_types |= {LeftCurlyBracketSolidus}
            next_states |= {self.STATE_ACCEPT}

        # RightCurlyBracket
        # 45:30
        if 53 in current_states and (syntactic in self.conditions) and (char == "}"):
            current_token_types |= {RightCurlyBracket}
            next_states |= {self.STATE_ACCEPT}

        # OrdChar
        # 47:18
        if 54 in current_states and (lexical in self.conditions) and not current_token_types & {Identifier, Colon, CommercialAt, GreaterThanSign, Comma, DoubleAmpersand, Ignore, Optional, ExclamationMark} and (not ("\000" <= char <= "\037" or char == "\177" or char == " " or char == ";" or char == "^" or char == "." or char == "[" or char == "$" or char == "(" or char == ")" or char == "|" or char == "*" or char == "+" or char == "?" or char == "{" or char == "\\")):
            current_token_types |= {OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # QuotedChar
        # 49:21
        if 55 in current_states and (lexical in self.conditions) and (char == "\\"):
            next_states |= {56, 57}

        # 49:25
        if 56 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == " " or char == ";" or char == "^" or char == "." or char == "[" or char == "$" or char == "(" or char == ")" or char == "|" or char == "*" or char == "+" or char == "?" or char == "{" or char == "\\"):
            current_token_types |= {QuotedChar}
            next_states |= {self.STATE_ACCEPT}

        # 49:52
        if 57 in current_states and (char == "0" or char == "1"):
            next_states |= {58}

        # 49:56:1
        if 58 in current_states and ("0" <= char <= "7"):
            next_states |= {59}

        # 49:56:2
        if 59 in current_states and ("0" <= char <= "7"):
            current_token_types |= {QuotedChar}
            next_states |= {self.STATE_ACCEPT}

        # FullStop
        # 51:19
        if 60 in current_states and (lexical in self.conditions) and (char == "."):
            current_token_types |= {FullStop}
            next_states |= {self.STATE_ACCEPT}

        # BracketExpression
        # 53:28
        if 61 in current_states and (lexical in self.conditions) and (char == "["):
            next_states |= {62, 63, 64, 69}

        # 53:32
        if 62 in current_states and (char == "^"):
            next_states |= {63, 64}

        # 53:37
        if 63 in current_states and (not ("\000" <= char <= "\037" or char == "\177" or char == "\\" or char == "^")):
            next_states |= {71, 78, 79, 91, 92}

        # 53:59
        if 64 in current_states and (char == "\\"):
            next_states |= {65, 66}

        # 53:63
        if 65 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {71, 78, 79, 91, 92}

        # 53:77
        if 66 in current_states and (char == "0" or char == "1"):
            next_states |= {67}

        # 53:81:1
        if 67 in current_states and ("0" <= char <= "7"):
            next_states |= {68}

        # 53:81:2
        if 68 in current_states and ("0" <= char <= "7"):
            next_states |= {71, 78, 79, 91, 92}

        # 53:94
        if 69 in current_states and (char == "^"):
            next_states |= {70}

        # 53:97
        if 70 in current_states and (char == "^"):
            next_states |= {71, 78, 79, 91, 92}

        # 53:102
        if 71 in current_states and (char == "-"):
            next_states |= {72, 73}

        # 53:105
        if 72 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\")):
            next_states |= {78, 79, 91, 92}

        # 53:127
        if 73 in current_states and (char == "\\"):
            next_states |= {74, 75}

        # 53:131
        if 74 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {78, 79, 91, 92}

        # 53:145
        if 75 in current_states and (char == "0" or char == "1"):
            next_states |= {76}

        # 53:149:1
        if 76 in current_states and ("0" <= char <= "7"):
            next_states |= {77}

        # 53:149:2
        if 77 in current_states and ("0" <= char <= "7"):
            next_states |= {78, 79, 91, 92}

        # 53:164
        if 78 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\" or char == "-")):
            next_states |= {78, 79, 84, 91, 92}

        # 53:187
        if 79 in current_states and (char == "\\"):
            next_states |= {80, 81}

        # 53:191
        if 80 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {78, 79, 84, 91, 92}

        # 53:205
        if 81 in current_states and (char == "0" or char == "1"):
            next_states |= {82}

        # 53:209:1
        if 82 in current_states and ("0" <= char <= "7"):
            next_states |= {83}

        # 53:209:2
        if 83 in current_states and ("0" <= char <= "7"):
            next_states |= {78, 79, 84, 91, 92}

        # 53:221
        if 84 in current_states and (char == "-"):
            next_states |= {85, 86}

        # 53:224
        if 85 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\")):
            next_states |= {78, 79, 91, 92}

        # 53:246
        if 86 in current_states and (char == "\\"):
            next_states |= {87, 88}

        # 53:250
        if 87 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {78, 79, 91, 92}

        # 53:264
        if 88 in current_states and (char == "0" or char == "1"):
            next_states |= {89}

        # 53:268:1
        if 89 in current_states and ("0" <= char <= "7"):
            next_states |= {90}

        # 53:268:2
        if 90 in current_states and ("0" <= char <= "7"):
            next_states |= {78, 79, 91, 92}

        # 53:283
        if 91 in current_states and (char == "-"):
            next_states |= {92}

        # 53:286
        if 92 in current_states and (char == "]"):
            current_token_types |= {BracketExpression}
            next_states |= {self.STATE_ACCEPT}

        # ExclamationMark
        # 55:27
        if 93 in current_states and (char == "!"):
            current_token_types |= {ExclamationMark, OrdChar}
            next_states |= {self.STATE_ACCEPT}

        # LeftSquareBracket
        # 57:30
        if 94 in current_states and (syntactic in self.conditions) and (char == "["):
            current_token_types |= {LeftSquareBracket}
            next_states |= {self.STATE_ACCEPT}

        # LeftSquareBracketSolidus
        # 59:37
        if 95 in current_states and (syntactic in self.conditions) and (char == "["):
            next_states |= {96}

        # 59:39
        if 96 in current_states and (char == "/"):
            current_token_types |= {LeftSquareBracketSolidus}
            next_states |= {self.STATE_ACCEPT}

        # RightSquareBracket
        # 61:31
        if 97 in current_states and (syntactic in self.conditions) and (char == "]"):
            current_token_types |= {RightSquareBracket}
            next_states |= {self.STATE_ACCEPT}

        return (current_token_types, next_states)
