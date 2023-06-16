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

# pylint: disable=missing-class-docstring

import re

from alchemist.front.lexer import Terminal

WHITESPACES: re.Pattern = re.compile(r"[\t\n\v\f\r ]+")
SINGLELINE_COMMENT: re.Pattern = re.compile(r"//.*")
MULTILINE_COMMENT: re.Pattern = re.compile(r"/\*(?:[^*]|\*+[^*/])*\*+/", re.MULTILINE)


class Identifier(Terminal):
    _pattern: str | re.Pattern = re.compile(
        r"(?:[A-Z_a-z]|\\(?:u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}))(?:[0-9A-Z_a-z]|\\(?:u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}))*"
    )
    _index = 1


class Keyword(Identifier):
    _pattern = ""
    soft_match = False


class Constant(Terminal):
    _pattern: str | re.Pattern = ""


class StringLiteral(Terminal):
    _pattern = re.compile(r"(?:u8?|[LU])?\"(?:[\t\v\f !#-[\]-~]|\\(?:['\"?\\abfnrtv]|[0-7]{1,3}|x[0-9A-Fa-f]+|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}))*\"")


class Punctuator(Terminal):
    _pattern = ""


class Auto(Keyword):
    _pattern = "auto"


class Break(Keyword):
    _pattern = "break"


class Case(Keyword):
    _pattern = "case"


class Char(Keyword):
    _pattern = "char"


class Const(Keyword):
    _pattern = "const"


class Continue(Keyword):
    _pattern = "continue"


class Default(Keyword):
    _pattern = "default"


class Do(Keyword):
    _pattern = "do"


class Double(Keyword):
    _pattern = "double"


class Else(Keyword):
    _pattern = "else"


class Enum(Keyword):
    _pattern = "enum"


class Extern(Keyword):
    _pattern = "extern"


class Float(Keyword):
    _pattern = "float"


class For(Keyword):
    _pattern = "for"


class Goto(Keyword):
    _pattern = "goto"


class If(Keyword):
    _pattern = "if"


class Inline(Keyword):
    _pattern = "inline"


class Int(Keyword):
    _pattern = "int"


class Long(Keyword):
    _pattern = "long"


class Register(Keyword):
    _pattern = "register"


class Restrict(Keyword):
    _pattern = "restrict"


class Return(Keyword):
    _pattern = "return"


class Short(Keyword):
    _pattern = "short"


class Signed(Keyword):
    _pattern = "signed"


class Sizeof(Keyword):
    _pattern = "sizeof"


class Static(Keyword):
    _pattern = "static"


class Struct(Keyword):
    _pattern = "struct"


class Switch(Keyword):
    _pattern = "switch"


class Typedef(Keyword):
    _pattern = "typedef"


class Union(Keyword):
    _pattern = "union"


class Unsigned(Keyword):
    _pattern = "unsigned"


class Void(Keyword):
    _pattern = "void"


class Volatile(Keyword):
    _pattern = "volatile"


class While(Keyword):
    _pattern = "while"


class _Alignas(Keyword):
    _pattern = "_Alignas"


class _Alignof(Keyword):
    _pattern = "_Alignof"


class _Atomic(Keyword):
    _pattern = "_Atomic"


class _Bool(Keyword):
    _pattern = "_Bool"


class _Complex(Keyword):
    _pattern = "_Complex"


class _Generic(Keyword):
    _pattern = "_Generic"


class _Imaginary(Keyword):
    _pattern = "_Imaginary"


class _Noreturn(Keyword):
    _pattern = "_Noreturn"


class _Static_Assert(Keyword):  # pylint: disable=invalid-name
    _pattern = "_Static_assert"


class _Thread_Local(Keyword):  # pylint: disable=invalid-name
    _pattern = "_Thread_local"


class Integer(Constant):
    _pattern = re.compile(r"(?:[1-9][0-9]*|0(?:[0-7]+|[Xx][0-9A-Fa-f]+)?)(?:[Uu](?:ll?|LL?)?|(?:ll?|LL?)[Uu]?)?")
    _index = 1


class Floating(Constant):
    _pattern = re.compile(
        r"(?:(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+|"
        r"0[Xx](?:[0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?|\.[0-9A-Fa-f]+)[Pp][+-]?[0-9]+)[FLfl]?"
    )


class Character(Constant):
    _pattern = re.compile(r"[LUu]?'(?:[\t\v\f -&(-[\]-~]|\\(?:['\"?\\abfnrtv]|[0-7]{1,3}|x[0-9A-Fa-f]+|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}))+'")


class LeftSquareBracket(Punctuator):
    _pattern = "["


class RightSquareBracket(Punctuator):
    _pattern = "]"


class LeftParenthesis(Punctuator):
    _pattern = "("


class RightParenthesis(Punctuator):
    _pattern = ")"


class LeftCurlyBracket(Punctuator):
    _pattern = "{"


class RightCurlyBracket(Punctuator):
    _pattern = "}"


class FullStop(Punctuator):
    _pattern = "."


class HyphenGreaterThan(Punctuator):
    _pattern = "->"


class DoublePlus(Punctuator):
    _pattern = "++"


class DoubleMinus(Punctuator):
    _pattern = "--"


class Ampersand(Punctuator):
    _pattern = "&"


class Asterisk(Punctuator):
    _pattern = "*"


class Plus(Punctuator):
    _pattern = "+"


class Minus(Punctuator):
    _pattern = "-"


class Tilde(Punctuator):
    _pattern = "~"


class Exclamation(Punctuator):
    _pattern = "!"


class Slash(Punctuator):
    _pattern = "/"


class Percent(Punctuator):
    _pattern = "%"


class DoubleLessThan(Punctuator):
    _pattern = "<<"


class DoubleGreaterThan(Punctuator):
    _pattern = ">>"


class LessThan(Punctuator):
    _pattern = "<"


class GreaterThan(Punctuator):
    _pattern = ">"


class LessThanEquals(Punctuator):
    _pattern = "<="


class GreaterThanEquals(Punctuator):
    _pattern = ">="


class DoubleEquals(Punctuator):
    _pattern = "=="


class ExclamationEquals(Punctuator):
    _pattern = "!="


class Caret(Punctuator):
    _pattern = "^"


class VerticalBar(Punctuator):
    _pattern = "|"


class DoubleAmpersand(Punctuator):
    _pattern = "&&"


class DoubleVerticalBar(Punctuator):
    _pattern = "||"


class Question(Punctuator):
    _pattern = "?"


class Colon(Punctuator):
    _pattern = ":"


class Semicolon(Punctuator):
    _pattern = ";"


class TripleFullStop(Punctuator):
    _pattern = "..."


class Equals(Punctuator):
    _pattern = "="


class AsteriskEquals(Punctuator):
    _pattern = "*="


class SlashEquals(Punctuator):
    _pattern = "/="


class PercentEquals(Punctuator):
    _pattern = "%="


class PlusEquals(Punctuator):
    _pattern = "+="


class MinusEquals(Punctuator):
    _pattern = "-="


class DoubleLessThanEquals(Punctuator):
    _pattern = "<<="


class DoubleGreaterThanEquals(Punctuator):
    _pattern = ">>="


class AmpersandEquals(Punctuator):
    _pattern = "&="


class CaretEquals(Punctuator):
    _pattern = "^="


class VerticalBarEquals(Punctuator):
    _pattern = "|="


class Comma(Punctuator):
    _pattern = ","


class Number(Punctuator):
    _pattern = "#"


class DoubleNumber(Punctuator):
    _pattern = "##"


class LessThanColon(Punctuator):
    _pattern = "<:"


class ColonGreaterThan(Punctuator):
    _pattern = ":>"


class LessThanPercent(Punctuator):
    _pattern = "<%"


class PercentGreaterThan(Punctuator):
    _pattern = "%>"


class PercentColon(Punctuator):
    _pattern = "%:"


class PercentColonPercentColon(Punctuator):
    _pattern = "%:%:"
