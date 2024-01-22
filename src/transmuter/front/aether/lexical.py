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

from ..lexical import TokenType, BaseLexer
from .common import Conditions


class TokenTypes:
    Whitespace = TokenType("Whitespace", False)
    Identifier = TokenType("Identifier", False)
    Colon = TokenType("Colon", False)
    Semicolon = TokenType("Semicolon", False)
    CommercialAt = TokenType("CommercialAt", False)
    LeftParenthesis = TokenType("LeftParenthesis", False)
    RightParenthesis = TokenType("RightParenthesis", False)
    GreaterThanSign = TokenType("GreaterThanSign", False)
    VerticalLine = TokenType("VerticalLine", False)
    Solidus = TokenType("Solidus", False)
    DoubleVerticalLine = TokenType("DoubleVerticalLine", False)
    Comma = TokenType("Comma", False)
    DoubleAmpersand = TokenType("DoubleAmpersand", False)
    Ignore = TokenType("Ignore", False)
    Optional = TokenType("Optional", False)
    Start = TokenType("Start", False)
    Asterisk = TokenType("Asterisk", False)
    PlusSign = TokenType("PlusSign", False)
    QuestionMark = TokenType("QuestionMark", False)
    ExpressionRange = TokenType("ExpressionRange", False)
    LeftCurlyBracket = TokenType("LeftCurlyBracket", False)
    LeftCurlyBracketSolidus = TokenType("LeftCurlyBracketSolidus", False)
    RightCurlyBracket = TokenType("RightCurlyBracket", False)
    OrdChar = TokenType("OrdChar", False)
    QuotedChar = TokenType("QuotedChar", False)
    FullStop = TokenType("FullStop", False)
    BracketExpression = TokenType("BracketExpression", False)
    ExclamationMark = TokenType("ExclamationMark", False)
    LeftSquareBracket = TokenType("LeftSquareBracket", False)
    LeftSquareBracketSolidus = TokenType("LeftSquareBracketSolidus", False)
    RightSquareBracket = TokenType("RightSquareBracket", False)


class Lexer(BaseLexer):
    STATES_START = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 25, 33, 38, 39, 40, 41, 50, 51, 53, 54, 55, 60, 61, 93, 94, 95, 97}
    TOKENTYPES_IGNORE = {TokenTypes.Whitespace}

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[TokenType], set[int]]:
        current_token_types = set()
        next_states = set()

        if 1 in current_states and (char == "\t" or char == " "):
            current_token_types |= {TokenTypes.Whitespace}
            next_states |= {1, self.STATE_ACCEPT}

        if 2 in current_states and (char == "\r"):
            next_states |= {3}

        if 3 in current_states and (char == "\n"):
            current_token_types |= {TokenTypes.Whitespace}
            next_states |= {self.STATE_ACCEPT}

        if 4 in current_states and not current_token_types & {TokenTypes.Ignore, TokenTypes.Optional, TokenTypes.Start} and ("A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_token_types |= {TokenTypes.Identifier, TokenTypes.OrdChar}
            next_states |= {5, self.STATE_ACCEPT}

        if 5 in current_states and not current_token_types & {TokenTypes.Ignore, TokenTypes.Optional, TokenTypes.Start} and ("0" <= char <= "9" or "A" <= char <= "Z" or char == "_" or "a" <= char <= "z"):
            current_token_types |= {TokenTypes.Identifier, TokenTypes.OrdChar}
            next_states |= {5, self.STATE_ACCEPT}

        if 6 in current_states and (char == ":"):
            current_token_types |= {TokenTypes.Colon, TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 7 in current_states and (char == ";"):
            current_token_types |= {TokenTypes.Semicolon}
            next_states |= {self.STATE_ACCEPT}

        if 8 in current_states and (char == "@"):
            current_token_types |= {TokenTypes.CommercialAt, TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 9 in current_states and (char == "("):
            current_token_types |= {TokenTypes.LeftParenthesis}
            next_states |= {self.STATE_ACCEPT}

        if 10 in current_states and (char == ")"):
            current_token_types |= {TokenTypes.RightParenthesis}
            next_states |= {self.STATE_ACCEPT}

        if 11 in current_states and (Conditions.lexical in self.conditions) and (char == ">"):
            current_token_types |= {TokenTypes.GreaterThanSign, TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 12 in current_states and (char == "|"):
            current_token_types |= {TokenTypes.VerticalLine}
            next_states |= {self.STATE_ACCEPT}

        if 13 in current_states and (Conditions.syntactic in self.conditions) and (char == "/"):
            current_token_types |= {TokenTypes.Solidus}
            next_states |= {self.STATE_ACCEPT}

        if 14 in current_states and (char == "|"):
            next_states |= {15}

        if 15 in current_states and (char == "|"):
            current_token_types |= {TokenTypes.DoubleVerticalLine}
            next_states |= {self.STATE_ACCEPT}

        if 16 in current_states and (char == ","):
            current_token_types |= {TokenTypes.Comma, TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 17 in current_states and (char == "&"):
            next_states |= {18}

        if 18 in current_states and (char == "&"):
            current_token_types |= {TokenTypes.DoubleAmpersand, TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 19 in current_states and (Conditions.lexical in self.conditions) and (char == "i"):
            next_states |= {20}

        if 20 in current_states and (char == "g"):
            next_states |= {21}

        if 21 in current_states and (char == "n"):
            next_states |= {22}

        if 22 in current_states and (char == "o"):
            next_states |= {23}

        if 23 in current_states and (char == "r"):
            next_states |= {24}

        if 24 in current_states and (char == "e"):
            current_token_types |= {TokenTypes.Ignore, TokenTypes.OrdChar}
            current_token_types -= {TokenTypes.Identifier}
            next_states |= {self.STATE_ACCEPT}

        if 25 in current_states and (Conditions.lexical in self.conditions) and (char == "o"):
            next_states |= {26}

        if 26 in current_states and (char == "p"):
            next_states |= {27}

        if 27 in current_states and (char == "t"):
            next_states |= {28}

        if 28 in current_states and (char == "i"):
            next_states |= {29}

        if 29 in current_states and (char == "o"):
            next_states |= {30}

        if 30 in current_states and (char == "n"):
            next_states |= {31}

        if 31 in current_states and (char == "a"):
            next_states |= {32}

        if 32 in current_states and (char == "l"):
            current_token_types |= {TokenTypes.Optional, TokenTypes.OrdChar}
            current_token_types -= {TokenTypes.Identifier}
            next_states |= {self.STATE_ACCEPT}

        if 33 in current_states and (Conditions.syntactic in self.conditions) and (char == "s"):
            next_states |= {34}

        if 34 in current_states and (char == "t"):
            next_states |= {35}

        if 35 in current_states and (char == "a"):
            next_states |= {36}

        if 36 in current_states and (char == "r"):
            next_states |= {37}

        if 37 in current_states and (char == "t"):
            current_token_types |= {TokenTypes.Start}
            current_token_types -= {TokenTypes.Identifier}
            next_states |= {self.STATE_ACCEPT}

        if 38 in current_states and (Conditions.lexical in self.conditions) and (char == "*"):
            current_token_types |= {TokenTypes.Asterisk}
            next_states |= {self.STATE_ACCEPT}

        if 39 in current_states and (Conditions.lexical in self.conditions) and (char == "+"):
            current_token_types |= {TokenTypes.PlusSign}
            next_states |= {self.STATE_ACCEPT}

        if 40 in current_states and (Conditions.lexical in self.conditions) and (char == "?"):
            current_token_types |= {TokenTypes.QuestionMark}
            next_states |= {self.STATE_ACCEPT}

        if 41 in current_states and (Conditions.lexical in self.conditions) and (char == "{"):
            next_states |= {42, 43}

        if 42 in current_states and (char == "0"):
            next_states |= {45, 49}

        if 43 in current_states and ("1" <= char <= "9"):
            next_states |= {44, 45, 49}

        if 44 in current_states and ("0" <= char <= "9"):
            next_states |= {44, 45, 49}

        if 45 in current_states and (char == ","):
            next_states |= {46, 47, 49}

        if 46 in current_states and (char == "0"):
            next_states |= {49}

        if 47 in current_states and ("1" <= char <= "9"):
            next_states |= {48, 49}

        if 48 in current_states and ("0" <= char <= "9"):
            next_states |= {48, 49}

        if 49 in current_states and (char == "}"):
            current_token_types |= {TokenTypes.ExpressionRange}
            next_states |= {self.STATE_ACCEPT}

        if 50 in current_states and (Conditions.syntactic in self.conditions) and (char == "{"):
            current_token_types |= {TokenTypes.LeftCurlyBracket}
            next_states |= {self.STATE_ACCEPT}

        if 51 in current_states and (Conditions.syntactic in self.conditions) and (char == "{"):
            next_states |= {52}

        if 52 in current_states and (char == "/"):
            current_token_types |= {TokenTypes.LeftCurlyBracketSolidus}
            next_states |= {self.STATE_ACCEPT}

        if 53 in current_states and (Conditions.syntactic in self.conditions) and (char == "}"):
            current_token_types |= {TokenTypes.RightCurlyBracket}
            next_states |= {self.STATE_ACCEPT}

        if 54 in current_states and (Conditions.lexical in self.conditions) and not current_token_types & {TokenTypes.Identifier, TokenTypes.Colon, TokenTypes.CommercialAt, TokenTypes.GreaterThanSign, TokenTypes.Comma, TokenTypes.DoubleAmpersand, TokenTypes.Ignore, TokenTypes.Optional, TokenTypes.ExclamationMark} and (not ("\000" <= char <= "\037" or char == "\177" or char == " " or char == ";" or char == "^" or char == "." or char == "[" or char == "$" or char == "(" or char == ")" or char == "|" or char == "*" or char == "+" or char == "?" or char == "{" or char == "\\")):
            current_token_types |= {TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 55 in current_states and (Conditions.lexical in self.conditions) and (char == "\\"):
            next_states |= {56, 57}

        if 56 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == " " or char == ";" or char == "^" or char == "." or char == "[" or char == "$" or char == "(" or char == ")" or char == "|" or char == "*" or char == "+" or char == "?" or char == "{" or char == "\\"):
            current_token_types |= {TokenTypes.QuotedChar}
            next_states |= {self.STATE_ACCEPT}

        if 57 in current_states and (char == "0" or char == "1"):
            next_states |= {58}

        if 58 in current_states and ("0" <= char <= "7"):
            next_states |= {59}

        if 59 in current_states and ("0" <= char <= "7"):
            current_token_types |= {TokenTypes.QuotedChar}
            next_states |= {self.STATE_ACCEPT}

        if 60 in current_states and (Conditions.lexical in self.conditions) and (char == "."):
            current_token_types |= {TokenTypes.FullStop}
            next_states |= {self.STATE_ACCEPT}

        if 61 in current_states and (Conditions.lexical in self.conditions) and (char == "["):
            next_states |= {62, 63, 64, 69}

        if 62 in current_states and (char == "^"):
            next_states |= {63, 64}

        if 63 in current_states and (not ("\000" <= char <= "\037" or char == "\177" or char == "\\" or char == "^")):
            next_states |= {71, 78, 79, 91, 92}

        if 64 in current_states and (char == "\\"):
            next_states |= {65, 66}

        if 65 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {71, 78, 79, 91, 92}

        if 66 in current_states and (char == "0" or char == "1"):
            next_states |= {67}

        if 67 in current_states and ("0" <= char <= "7"):
            next_states |= {68}

        if 68 in current_states and ("0" <= char <= "7"):
            next_states |= {71, 78, 79, 91, 92}

        if 69 in current_states and (char == "^"):
            next_states |= {70}

        if 70 in current_states and (char == "^"):
            next_states |= {71, 78, 79, 91, 92}

        if 71 in current_states and (char == "-"):
            next_states |= {72, 73}

        if 72 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\")):
            next_states |= {78, 79, 91, 92}

        if 73 in current_states and (char == "\\"):
            next_states |= {74, 75}

        if 74 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {78, 79, 91, 92}

        if 75 in current_states and (char == "0" or char == "1"):
            next_states |= {76}

        if 76 in current_states and ("0" <= char <= "7"):
            next_states |= {77}

        if 77 in current_states and ("0" <= char <= "7"):
            next_states |= {78, 79, 91, 92}

        if 78 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\" or char == "-")):
            next_states |= {78, 79, 84, 91, 92}

        if 79 in current_states and (char == "\\"):
            next_states |= {80, 81}

        if 80 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {78, 79, 84, 91, 92}

        if 81 in current_states and (char == "0" or char == "1"):
            next_states |= {82}

        if 82 in current_states and ("0" <= char <= "7"):
            next_states |= {83}

        if 83 in current_states and ("0" <= char <= "7"):
            next_states |= {78, 79, 84, 91, 92}

        if 84 in current_states and (char == "-"):
            next_states |= {85, 86}

        if 85 in current_states and (not (char == "]" or "\000" <= char <= "\037" or char == "\177" or char == "\\")):
            next_states |= {78, 79, 91, 92}

        if 86 in current_states and (char == "\\"):
            next_states |= {87, 88}

        if 87 in current_states and (char == "a" or char == "b" or char == "t" or char == "n" or char == "v" or char == "f" or char == "r" or char == "\\"):
            next_states |= {78, 79, 91, 92}

        if 88 in current_states and (char == "0" or char == "1"):
            next_states |= {89}

        if 89 in current_states and ("0" <= char <= "7"):
            next_states |= {90}

        if 90 in current_states and ("0" <= char <= "7"):
            next_states |= {78, 79, 91, 92}

        if 91 in current_states and (char == "-"):
            next_states |= {92}

        if 92 in current_states and (char == "]"):
            current_token_types |= {TokenTypes.BracketExpression}
            next_states |= {self.STATE_ACCEPT}

        if 93 in current_states and (char == "!"):
            current_token_types |= {TokenTypes.ExclamationMark, TokenTypes.OrdChar}
            next_states |= {self.STATE_ACCEPT}

        if 94 in current_states and (Conditions.syntactic in self.conditions) and (char == "["):
            current_token_types |= {TokenTypes.LeftSquareBracket}
            next_states |= {self.STATE_ACCEPT}

        if 95 in current_states and (Conditions.syntactic in self.conditions) and (char == "["):
            next_states |= {96}

        if 96 in current_states and (char == "/"):
            current_token_types |= {TokenTypes.LeftSquareBracketSolidus}
            next_states |= {self.STATE_ACCEPT}

        if 97 in current_states and (Conditions.syntactic in self.conditions) and (char == "]"):
            current_token_types |= {TokenTypes.RightSquareBracket}
            next_states |= {self.STATE_ACCEPT}

        return (current_token_types, next_states)
