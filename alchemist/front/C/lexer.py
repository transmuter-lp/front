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

from ..lexer import Terminal, Lexer

__all__: list[str] = []


def _export(cls: type[Terminal]) -> type[Terminal]:
    global __all__  # pylint: disable=global-variable-not-assigned
    __all__.append(cls.__name__)
    return cls


keywords: list[type["Keyword"]] = []


def _keyword(cls: type["Keyword"]) -> type["Keyword"]:
    global keywords  # pylint: disable=global-variable-not-assigned
    keywords.append(cls)
    return cls


punctuators: list[type["Punctuator"]] = []


def _punctuator(cls: type["Punctuator"]) -> type["Punctuator"]:
    global punctuators  # pylint: disable=global-variable-not-assigned
    punctuators.append(cls)
    return cls


WHITESPACES: re.Pattern = re.compile(r"[\t\n\v\f\r ]+")
SINGLELINE_COMMENT: re.Pattern = re.compile(r"//.*")
MULTILINE_COMMENT: re.Pattern = re.compile(r"/\*(?:[^*]|\*+[^*/])*\*+/", re.MULTILINE)


@_export
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


@_export
class StringLiteral(Terminal):
    _pattern = re.compile(r"(?:u8?|[LU])?\"(?:[\t\v\f !#-[\]-~]|\\(?:['\"?\\abfnrtv]|[0-7]{1,3}|x[0-9A-Fa-f]+|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}))*\"")


class Punctuator(Terminal):
    _pattern = ""


@_export
@_keyword
class _Static_Assert(Keyword):  # pylint: disable=invalid-name
    _pattern = "_Static_assert"


@_export
@_keyword
class _Thread_Local(Keyword):  # pylint: disable=invalid-name
    _pattern = "_Thread_local"


@_export
@_keyword
class _Imaginary(Keyword):
    _pattern = "_Imaginary"


@_export
@_keyword
class _Noreturn(Keyword):
    _pattern = "_Noreturn"


@_export
@_keyword
class Continue(Keyword):
    _pattern = "continue"


@_export
@_keyword
class Register(Keyword):
    _pattern = "register"


@_export
@_keyword
class Restrict(Keyword):
    _pattern = "restrict"


@_export
@_keyword
class Unsigned(Keyword):
    _pattern = "unsigned"


@_export
@_keyword
class Volatile(Keyword):
    _pattern = "volatile"


@_export
@_keyword
class _Alignas(Keyword):
    _pattern = "_Alignas"


@_export
@_keyword
class _Alignof(Keyword):
    _pattern = "_Alignof"


@_export
@_keyword
class _Complex(Keyword):
    _pattern = "_Complex"


@_export
@_keyword
class _Generic(Keyword):
    _pattern = "_Generic"


@_export
@_keyword
class Default(Keyword):
    _pattern = "default"


@_export
@_keyword
class Typedef(Keyword):
    _pattern = "typedef"


@_export
@_keyword
class _Atomic(Keyword):
    _pattern = "_Atomic"


@_export
@_keyword
class Double(Keyword):
    _pattern = "double"


@_export
@_keyword
class Extern(Keyword):
    _pattern = "extern"


@_export
@_keyword
class Inline(Keyword):
    _pattern = "inline"


@_export
@_keyword
class Return(Keyword):
    _pattern = "return"


@_export
@_keyword
class Signed(Keyword):
    _pattern = "signed"


@_export
@_keyword
class Sizeof(Keyword):
    _pattern = "sizeof"


@_export
@_keyword
class Static(Keyword):
    _pattern = "static"


@_export
@_keyword
class Struct(Keyword):
    _pattern = "struct"


@_export
@_keyword
class Switch(Keyword):
    _pattern = "switch"


@_export
@_keyword
class Break(Keyword):
    _pattern = "break"


@_export
@_keyword
class Const(Keyword):
    _pattern = "const"


@_export
@_keyword
class Float(Keyword):
    _pattern = "float"


@_export
@_keyword
class Short(Keyword):
    _pattern = "short"


@_export
@_keyword
class Union(Keyword):
    _pattern = "union"


@_export
@_keyword
class While(Keyword):
    _pattern = "while"


@_export
@_keyword
class _Bool(Keyword):
    _pattern = "_Bool"


@_export
@_keyword
class Auto(Keyword):
    _pattern = "auto"


@_export
@_keyword
class Case(Keyword):
    _pattern = "case"


@_export
@_keyword
class Char(Keyword):
    _pattern = "char"


@_export
@_keyword
class Else(Keyword):
    _pattern = "else"


@_export
@_keyword
class Enum(Keyword):
    _pattern = "enum"


@_export
@_keyword
class Goto(Keyword):
    _pattern = "goto"


@_export
@_keyword
class Long(Keyword):
    _pattern = "long"


@_export
@_keyword
class Void(Keyword):
    _pattern = "void"


@_export
@_keyword
class For(Keyword):
    _pattern = "for"


@_export
@_keyword
class Int(Keyword):
    _pattern = "int"


@_export
@_keyword
class Do(Keyword):
    _pattern = "do"


@_export
@_keyword
class If(Keyword):
    _pattern = "if"


@_export
class Integer(Constant):
    _pattern = re.compile(r"(?:[1-9][0-9]*|0(?:[0-7]+|[Xx][0-9A-Fa-f]+)?)(?:[Uu](?:ll?|LL?)?|(?:ll?|LL?)[Uu]?)?")
    _index = 1


@_export
class Floating(Constant):
    _pattern = re.compile(
        r"(?:(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+|"
        r"0[Xx](?:[0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?|\.[0-9A-Fa-f]+)[Pp][+-]?[0-9]+)[FLfl]?"
    )


@_export
class Character(Constant):
    _pattern = re.compile(r"[LUu]?'(?:[\t\v\f -&(-[\]-~]|\\(?:['\"?\\abfnrtv]|[0-7]{1,3}|x[0-9A-Fa-f]+|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}))+'")


@_export
@_punctuator
class PercentColonPercentColon(Punctuator):
    _pattern = "%:%:"


@_export
@_punctuator
class TripleFullStop(Punctuator):
    _pattern = "..."


@_export
@_punctuator
class DoubleLessThanEquals(Punctuator):
    _pattern = "<<="


@_export
@_punctuator
class DoubleGreaterThanEquals(Punctuator):
    _pattern = ">>="


@_export
@_punctuator
class HyphenGreaterThan(Punctuator):
    _pattern = "->"


@_export
@_punctuator
class DoublePlus(Punctuator):
    _pattern = "++"


@_export
@_punctuator
class DoubleMinus(Punctuator):
    _pattern = "--"


@_export
@_punctuator
class DoubleLessThan(Punctuator):
    _pattern = "<<"


@_export
@_punctuator
class DoubleGreaterThan(Punctuator):
    _pattern = ">>"


@_export
@_punctuator
class LessThanEquals(Punctuator):
    _pattern = "<="


@_export
@_punctuator
class GreaterThanEquals(Punctuator):
    _pattern = ">="


@_export
@_punctuator
class DoubleEquals(Punctuator):
    _pattern = "=="


@_export
@_punctuator
class ExclamationEquals(Punctuator):
    _pattern = "!="


@_export
@_punctuator
class DoubleAmpersand(Punctuator):
    _pattern = "&&"


@_export
@_punctuator
class DoubleVerticalBar(Punctuator):
    _pattern = "||"


@_export
@_punctuator
class AsteriskEquals(Punctuator):
    _pattern = "*="


@_export
@_punctuator
class SlashEquals(Punctuator):
    _pattern = "/="


@_export
@_punctuator
class PercentEquals(Punctuator):
    _pattern = "%="


@_export
@_punctuator
class PlusEquals(Punctuator):
    _pattern = "+="


@_export
@_punctuator
class MinusEquals(Punctuator):
    _pattern = "-="


@_export
@_punctuator
class AmpersandEquals(Punctuator):
    _pattern = "&="


@_export
@_punctuator
class CaretEquals(Punctuator):
    _pattern = "^="


@_export
@_punctuator
class VerticalBarEquals(Punctuator):
    _pattern = "|="


@_export
@_punctuator
class DoubleNumber(Punctuator):
    _pattern = "##"


@_export
@_punctuator
class LessThanColon(Punctuator):
    _pattern = "<:"


@_export
@_punctuator
class ColonGreaterThan(Punctuator):
    _pattern = ":>"


@_export
@_punctuator
class LessThanPercent(Punctuator):
    _pattern = "<%"


@_export
@_punctuator
class PercentGreaterThan(Punctuator):
    _pattern = "%>"


@_export
@_punctuator
class PercentColon(Punctuator):
    _pattern = "%:"


@_export
@_punctuator
class LeftSquareBracket(Punctuator):
    _pattern = "["


@_export
@_punctuator
class RightSquareBracket(Punctuator):
    _pattern = "]"


@_export
@_punctuator
class LeftParenthesis(Punctuator):
    _pattern = "("


@_export
@_punctuator
class RightParenthesis(Punctuator):
    _pattern = ")"


@_export
@_punctuator
class LeftCurlyBracket(Punctuator):
    _pattern = "{"


@_export
@_punctuator
class RightCurlyBracket(Punctuator):
    _pattern = "}"


@_export
@_punctuator
class FullStop(Punctuator):
    _pattern = "."


@_export
@_punctuator
class Ampersand(Punctuator):
    _pattern = "&"


@_export
@_punctuator
class Asterisk(Punctuator):
    _pattern = "*"


@_export
@_punctuator
class Plus(Punctuator):
    _pattern = "+"


@_export
@_punctuator
class Minus(Punctuator):
    _pattern = "-"


@_export
@_punctuator
class Tilde(Punctuator):
    _pattern = "~"


@_export
@_punctuator
class Exclamation(Punctuator):
    _pattern = "!"


@_export
@_punctuator
class Slash(Punctuator):
    _pattern = "/"


@_export
@_punctuator
class Percent(Punctuator):
    _pattern = "%"


@_export
@_punctuator
class LessThan(Punctuator):
    _pattern = "<"


@_export
@_punctuator
class GreaterThan(Punctuator):
    _pattern = ">"


@_export
@_punctuator
class Caret(Punctuator):
    _pattern = "^"


@_export
@_punctuator
class VerticalBar(Punctuator):
    _pattern = "|"


@_export
@_punctuator
class Question(Punctuator):
    _pattern = "?"


@_export
@_punctuator
class Colon(Punctuator):
    _pattern = ":"


@_export
@_punctuator
class Semicolon(Punctuator):
    _pattern = ";"


@_export
@_punctuator
class Equals(Punctuator):
    _pattern = "="


@_export
@_punctuator
class Comma(Punctuator):
    _pattern = ","


@_export
@_punctuator
class Number(Punctuator):
    _pattern = "#"


class CLexer(Lexer):
    _terminals = Lexer.sort([StringLiteral, Floating, Character, (Identifier, Lexer.sort(keywords)), Integer, *punctuators])  # type: ignore[arg-type]
    _ignored = [WHITESPACES, SINGLELINE_COMMENT, MULTILINE_COMMENT]
