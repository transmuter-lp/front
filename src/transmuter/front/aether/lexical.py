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

from ..lexical import BaseTokenType, BaseLexer
from .common import Condition


class TokenType(BaseTokenType):
    Whitespace = BaseTokenType("Whitespace", False)
    Identifier = BaseTokenType("Identifier", False)
    Colon = BaseTokenType("Colon", False)
    Semicolon = BaseTokenType("Semicolon", False)
    CommercialAt = BaseTokenType("CommercialAt", False)
    LeftParenthesis = BaseTokenType("LeftParenthesis", False)
    RightParenthesis = BaseTokenType("RightParenthesis", False)
    GreaterThanSign = BaseTokenType("GreaterThanSign", False)
    VerticalLine = BaseTokenType("VerticalLine", False)
    Solidus = BaseTokenType("Solidus", False)
    DoubleVerticalLine = BaseTokenType("DoubleVerticalLine", False)
    Comma = BaseTokenType("Comma", False)
    DoubleAmpersand = BaseTokenType("DoubleAmpersand", False)
    Ignore = BaseTokenType("Ignore", False)
    Optional = BaseTokenType("Optional", False)
    Start = BaseTokenType("Start", False)
    Asterisk = BaseTokenType("Asterisk", False)
    PlusSign = BaseTokenType("PlusSign", False)
    QuestionMark = BaseTokenType("QuestionMark", False)
    ExpressionRange = BaseTokenType("ExpressionRange", False)
    LeftCurlyBracket = BaseTokenType("LeftCurlyBracket", False)
    LeftCurlyBracketSolidus = BaseTokenType("LeftCurlyBracketSolidus", False)
    RightCurlyBracket = BaseTokenType("RightCurlyBracket", False)
    OrdChar = BaseTokenType("OrdChar", False)
    QuotedChar = BaseTokenType("QuotedChar", False)
    FullStop = BaseTokenType("FullStop", False)
    BracketExpression = BaseTokenType("BracketExpression", False)
    ExclamationMark = BaseTokenType("ExclamationMark", False)
    LeftSquareBracket = BaseTokenType("LeftSquareBracket", False)
    LeftSquareBracketSolidus = BaseTokenType("LeftSquareBracketSolidus", False)
    RightSquareBracket = BaseTokenType("RightSquareBracket", False)


class Lexer(BaseLexer):
    STATE_START = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 25, 33, 38, 39, 40, 41, 50, 51, 53, 54, 55, 60, 61, 93, 94, 95, 97}
    TOKENTYPE_IGNORE = {TokenType.Whitespace}

    def nfa(self, char: str, current_state: set[int]) -> tuple[set[BaseTokenType], set[int]]:
        current_token_type = set()
        next_state = set()

        if 1 in current_state and (char == "\t" or char == " "):
            current_token_type |= {TokenType.Whitespace}
            next_state |= {1, self.STATE_ACCEPT}

        if 2 in current_state and (char == "\r"):
            next_state |= {3}

        if 3 in current_state and (char == "\n"):
            current_token_type |= {TokenType.Whitespace}
            next_state |= {self.STATE_ACCEPT}

        if 4 in current_state and not current_token_type & {TokenType.Ignore, TokenType.Optional, TokenType.Start} and ("A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_token_type |= {TokenType.Identifier, TokenType.OrdChar}
            next_state |= {5, self.STATE_ACCEPT}

        if 5 in current_state and not current_token_type & {TokenType.Ignore, TokenType.Optional, TokenType.Start} and ("0" <= char <= "9" or "A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_token_type |= {TokenType.Identifier, TokenType.OrdChar}
            next_state |= {5, self.STATE_ACCEPT}

        if 6 in current_state and (char == ":"):
            current_token_type |= {TokenType.Colon, TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 7 in current_state and (char == ";"):
            current_token_type |= {TokenType.Semicolon}
            next_state |= {self.STATE_ACCEPT}

        if 8 in current_state and (char == "@"):
            current_token_type |= {TokenType.CommercialAt, TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 9 in current_state and (char == "("):
            current_token_type |= {TokenType.LeftParenthesis}
            next_state |= {self.STATE_ACCEPT}

        if 10 in current_state and (char == ")"):
            current_token_type |= {TokenType.RightParenthesis}
            next_state |= {self.STATE_ACCEPT}

        if 11 in current_state and (Condition.lexical in self.condition) and (char == ">"):
            current_token_type |= {TokenType.GreaterThanSign, TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 12 in current_state and (char == "|"):
            current_token_type |= {TokenType.VerticalLine}
            next_state |= {self.STATE_ACCEPT}

        if 13 in current_state and (Condition.syntactic in self.condition) and (char == "/"):
            current_token_type |= {TokenType.Solidus}
            next_state |= {self.STATE_ACCEPT}

        if 14 in current_state and (char == "|"):
            next_state |= {15}

        if 15 in current_state and (char == "|"):
            current_token_type |= {TokenType.DoubleVerticalLine}
            next_state |= {self.STATE_ACCEPT}

        if 16 in current_state and (char == ","):
            current_token_type |= {TokenType.Comma, TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 17 in current_state and (char == "&"):
            next_state |= {18}

        if 18 in current_state and (char == "&"):
            current_token_type |= {TokenType.DoubleAmpersand, TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 19 in current_state and (Condition.lexical in self.condition) and (char == "i"):
            next_state |= {20}

        if 20 in current_state and (char == "g"):
            next_state |= {21}

        if 21 in current_state and (char == "n"):
            next_state |= {22}

        if 22 in current_state and (char == "o"):
            next_state |= {23}

        if 23 in current_state and (char == "r"):
            next_state |= {24}

        if 24 in current_state and (char == "e"):
            current_token_type |= {TokenType.Ignore, TokenType.OrdChar}
            current_token_type -= {TokenType.Identifier}
            next_state |= {self.STATE_ACCEPT}

        if 25 in current_state and (Condition.lexical in self.condition) and (char == "o"):
            next_state |= {26}

        if 26 in current_state and (char == "p"):
            next_state |= {27}

        if 27 in current_state and (char == "t"):
            next_state |= {28}

        if 28 in current_state and (char == "i"):
            next_state |= {29}

        if 29 in current_state and (char == "o"):
            next_state |= {30}

        if 30 in current_state and (char == "n"):
            next_state |= {31}

        if 31 in current_state and (char == "a"):
            next_state |= {32}

        if 32 in current_state and (char == "l"):
            current_token_type |= {TokenType.Optional, TokenType.OrdChar}
            current_token_type -= {TokenType.Identifier}
            next_state |= {self.STATE_ACCEPT}

        if 33 in current_state and (Condition.syntactic in self.condition) and (char == "s"):
            next_state |= {34}

        if 34 in current_state and (char == "t"):
            next_state |= {35}

        if 35 in current_state and (char == "a"):
            next_state |= {36}

        if 36 in current_state and (char == "r"):
            next_state |= {37}

        if 37 in current_state and (char == "t"):
            current_token_type |= {TokenType.Start}
            current_token_type -= {TokenType.Identifier}
            next_state |= {self.STATE_ACCEPT}

        if 38 in current_state and (Condition.lexical in self.condition) and (char == "*"):
            current_token_type |= {TokenType.Asterisk}
            next_state |= {self.STATE_ACCEPT}

        if 39 in current_state and (Condition.lexical in self.condition) and (char == "+"):
            current_token_type |= {TokenType.PlusSign}
            next_state |= {self.STATE_ACCEPT}

        if 40 in current_state and (Condition.lexical in self.condition) and (char == "?"):
            current_token_type |= {TokenType.QuestionMark}
            next_state |= {self.STATE_ACCEPT}

        if 41 in current_state and (Condition.lexical in self.condition) and (char == "{"):
            next_state |= {42, 43}

        if 42 in current_state and (char == "0"):
            next_state |= {45, 49}

        if 43 in current_state and ("1" <= char <= "9"):
            next_state |= {44, 45, 49}

        if 44 in current_state and ("0" <= char <= "9"):
            next_state |= {44, 45, 49}

        if 45 in current_state and (char == ","):
            next_state |= {46, 47, 49}

        if 46 in current_state and (char == "0"):
            next_state |= {49}

        if 47 in current_state and ("1" <= char <= "9"):
            next_state |= {48, 49}

        if 48 in current_state and ("0" <= char <= "9"):
            next_state |= {48, 49}

        if 49 in current_state and (char == "}"):
            current_token_type |= {TokenType.ExpressionRange}
            next_state |= {self.STATE_ACCEPT}

        if 50 in current_state and (Condition.syntactic in self.condition) and (char == "{"):
            current_token_type |= {TokenType.LeftCurlyBracket}
            next_state |= {self.STATE_ACCEPT}

        if 51 in current_state and (Condition.syntactic in self.condition) and (char == "{"):
            next_state |= {52}

        if 52 in current_state and (char == "/"):
            current_token_type |= {TokenType.LeftCurlyBracketSolidus}
            next_state |= {self.STATE_ACCEPT}

        if 53 in current_state and (Condition.syntactic in self.condition) and (char == "}"):
            current_token_type |= {TokenType.RightCurlyBracket}
            next_state |= {self.STATE_ACCEPT}

        if 54 in current_state and (Condition.lexical in self.condition) and not current_token_type & {TokenType.Identifier, TokenType.Colon, TokenType.CommercialAt, TokenType.GreaterThanSign, TokenType.Comma, TokenType.DoubleAmpersand, TokenType.Ignore, TokenType.Optional, TokenType.ExclamationMark} and (not ("\000" <= char <= "\037" or char == "\177" or char == " " or char == ";" or char == "^" or char == "." or char == "[" or char == "$" or char == "(" or char == ")" or char == "|" or char == "*" or char == "+" or char == "?" or char == "{" or char == "\\")):
            current_token_type |= {TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 55 in current_state and (Condition.lexical in self.condition) and (char == "\\"):
            next_state |= {56, 57}

        if 56 in current_state and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == " " or char == ";" or char == "^" or char == "." or char == "[" or char == "$" or char == "(" or char == ")" or char == "|" or char == "*" or char == "+" or char == "?" or char == "{" or char == "\\"):
            current_token_type |= {TokenType.QuotedChar}
            next_state |= {self.STATE_ACCEPT}

        if 57 in current_state and (char == "0" or char == "1"):
            next_state |= {58}

        if 58 in current_state and ("0" <= char <= "7"):
            next_state |= {59}

        if 59 in current_state and ("0" <= char <= "7"):
            current_token_type |= {TokenType.QuotedChar}
            next_state |= {self.STATE_ACCEPT}

        if 60 in current_state and (Condition.lexical in self.condition) and (char == "."):
            current_token_type |= {TokenType.FullStop}
            next_state |= {self.STATE_ACCEPT}

        if 61 in current_state and (Condition.lexical in self.condition) and (char == "["):
            next_state |= {62, 63, 64, 69}

        if 62 in current_state and (char == "^"):
            next_state |= {63, 64}

        if 63 in current_state and (not ("\000" <= char <= "\037" or char == "\177" or char == "\\" or char == "^")):
            next_state |= {71, 78, 79, 91, 92}

        if 64 in current_state and (char == "\\"):
            next_state |= {65, 66}

        if 65 in current_state and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_state |= {71, 78, 79, 91, 92}

        if 66 in current_state and (char == "0" or char == "1"):
            next_state |= {67}

        if 67 in current_state and ("0" <= char <= "7"):
            next_state |= {68}

        if 68 in current_state and ("0" <= char <= "7"):
            next_state |= {71, 78, 79, 91, 92}

        if 69 in current_state and (char == "^"):
            next_state |= {70}

        if 70 in current_state and (char == "^"):
            next_state |= {71, 78, 79, 91, 92}

        if 71 in current_state and (char == "-"):
            next_state |= {72, 73}

        if 72 in current_state and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\")):
            next_state |= {78, 79, 91, 92}

        if 73 in current_state and (char == "\\"):
            next_state |= {74, 75}

        if 74 in current_state and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_state |= {78, 79, 91, 92}

        if 75 in current_state and (char == "0" or char == "1"):
            next_state |= {76}

        if 76 in current_state and ("0" <= char <= "7"):
            next_state |= {77}

        if 77 in current_state and ("0" <= char <= "7"):
            next_state |= {78, 79, 91, 92}

        if 78 in current_state and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\" or char == "-")):
            next_state |= {78, 79, 84, 91, 92}

        if 79 in current_state and (char == "\\"):
            next_state |= {80, 81}

        if 80 in current_state and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_state |= {78, 79, 84, 91, 92}

        if 81 in current_state and (char == "0" or char == "1"):
            next_state |= {82}

        if 82 in current_state and ("0" <= char <= "7"):
            next_state |= {83}

        if 83 in current_state and ("0" <= char <= "7"):
            next_state |= {78, 79, 84, 91, 92}

        if 84 in current_state and (char == "-"):
            next_state |= {85, 86}

        if 85 in current_state and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\")):
            next_state |= {78, 79, 91, 92}

        if 86 in current_state and (char == "\\"):
            next_state |= {87, 88}

        if 87 in current_state and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_state |= {78, 79, 91, 92}

        if 88 in current_state and (char == "0" or char == "1"):
            next_state |= {89}

        if 89 in current_state and ("0" <= char <= "7"):
            next_state |= {90}

        if 90 in current_state and ("0" <= char <= "7"):
            next_state |= {78, 79, 91, 92}

        if 91 in current_state and (char == "-"):
            next_state |= {92}

        if 92 in current_state and (char == "]"):
            current_token_type |= {TokenType.BracketExpression}
            next_state |= {self.STATE_ACCEPT}

        if 93 in current_state and (char == "!"):
            current_token_type |= {TokenType.ExclamationMark, TokenType.OrdChar}
            next_state |= {self.STATE_ACCEPT}

        if 94 in current_state and (Condition.syntactic in self.condition) and (char == "["):
            current_token_type |= {TokenType.LeftSquareBracket}
            next_state |= {self.STATE_ACCEPT}

        if 95 in current_state and (Condition.syntactic in self.condition) and (char == "["):
            next_state |= {96}

        if 96 in current_state and (char == "/"):
            current_token_type |= {TokenType.LeftSquareBracketSolidus}
            next_state |= {self.STATE_ACCEPT}

        if 97 in current_state and (Condition.syntactic in self.condition) and (char == "]"):
            current_token_type |= {TokenType.RightSquareBracket}
            next_state |= {self.STATE_ACCEPT}

        return (current_token_type, next_state)
