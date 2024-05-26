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

from ..common import TransmuterCondition, TransmuterSymbolMatchError
from ..lexical import TransmuterTerminal
from ..syntactic import transmuter_once, TransmuterNonterminalType, TransmuterParser
from .common import lexical, syntactic
from .lexical import Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, GreaterThanSign, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, Ignore, Optional, Start, Asterisk, PlusSign, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket


class Grammar(TransmuterNonterminalType):
    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return True

    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = Production.call(parser, paths0)
        paths1 = paths0

        while True:  # iteration
            try:
                paths1 = Production.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        return paths0


class Production(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = ProductionHeader.call(parser, paths0)
        paths0 = ProductionBody.call(parser, paths0)
        return paths0


class ProductionHeader(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = Identifier.call(parser.lexer, paths0)

        if lexical in parser.lexer.conditions:
            try:  # optional
                paths1 = paths0
                paths1 = Condition.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:  # optional
                pass

        try:  # optional
            paths1 = paths0
            paths1 = ProductionSpecifiers.call(parser, paths1)
            paths0 = paths1
        except TransmuterSymbolMatchError:  # optional
            pass

        if lexical in parser.lexer.conditions:
            try:  # optional
                paths1 = paths0
                paths1 = ProductionPrecedences.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:  # optional
                pass

        paths0 = Colon.call(parser.lexer, paths0)
        return paths0


class ProductionBody(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = SelectionExpression.call(parser, paths0)
        paths0 = Semicolon.call(parser.lexer, paths0)
        return paths0


class Condition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = CommercialAt.call(parser.lexer, paths0)
        paths0 = DisjunctionCondition.call(parser, paths0)
        return paths0


class ProductionSpecifiers(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = LeftParenthesis.call(parser.lexer, paths0)
        paths0 = ProductionSpecifierList.call(parser, paths0)
        paths0 = RightParenthesis.call(parser.lexer, paths0)
        return paths0


class ProductionPrecedences(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = GreaterThanSign.call(parser.lexer, paths0)
        paths0 = ProductionPrecedenceList.call(parser, paths0)
        return paths0


class SelectionExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = SequenceExpression.call(parser, paths0)
        paths1 = paths0

        while True:  # iteration
            try:
                while transmuter_once:  # selection
                    try:  # option 1
                        paths2 = paths1
                        paths2 = VerticalLine.call(parser.lexer, paths2)
                        paths1 = paths2
                        break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            paths2 = paths1
                            paths2 = Solidus.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                paths1 = SequenceExpression.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        return paths0


class DisjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = ConjunctionCondition.call(parser, paths0)
        paths1 = paths0

        while True:  # iteration
            try:
                paths1 = DoubleVerticalLine.call(parser.lexer, paths1)
                paths1 = ConjunctionCondition.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        return paths0


class ProductionSpecifierList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = ProductionSpecifier.call(parser, paths0)
        paths1 = paths0

        while True:  # iteration
            try:
                paths1 = Comma.call(parser.lexer, paths1)
                paths1 = ProductionSpecifier.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        return paths0


class ProductionPrecedenceList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = ProductionPrecedence.call(parser, paths0)
        paths1 = paths0

        while True:  # iteration
            try:
                paths1 = Comma.call(parser.lexer, paths1)
                paths1 = ProductionPrecedence.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        return paths0


class SequenceExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    paths1 = paths0
                    paths1 = IterationExpression.call(parser, paths1)
                    paths2 = paths1

                    while True:  # iteration
                        try:
                            paths2 = IterationExpression.call(parser, paths2)
                            paths1 = paths2
                        except TransmuterSymbolMatchError:
                            break  # iteration

                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    paths1 = paths0
                    paths1 = PrimaryExpression.call(parser, paths1)
                    paths2 = paths1

                    while True:  # iteration
                        try:
                            paths2 = PrimaryExpression.call(parser, paths2)
                            paths1 = paths2
                        except TransmuterSymbolMatchError:
                            break  # iteration

                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return paths0


class ConjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = NegationCondition.call(parser, paths0)
        paths1 = paths0

        while True:  # iteration
            try:
                paths1 = DoubleAmpersand.call(parser.lexer, paths1)
                paths1 = NegationCondition.call(parser, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        return paths0


class ProductionSpecifier(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                paths1 = paths0
                paths1 = Identifier.call(parser.lexer, paths1)
                paths0 = paths1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                paths1 = paths0

                while transmuter_once:  # selection
                    try:  # option 1
                        if lexical in parser.lexer.conditions:
                            paths2 = paths1

                            while transmuter_once:  # selection
                                try:  # option 1
                                    paths3 = paths2
                                    paths3 = Ignore.call(parser.lexer, paths3)
                                    paths2 = paths3
                                    break
                                except TransmuterSymbolMatchError:  # option 1
                                    pass

                                try:  # option 2
                                    paths3 = paths2
                                    paths3 = Optional.call(parser.lexer, paths3)
                                    paths2 = paths3
                                    break
                                except TransmuterSymbolMatchError:  # option 2
                                    pass

                                raise TransmuterSymbolMatchError()  # selection

                            paths1 = paths2
                            break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            paths2 = paths1
                            paths2 = Start.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                try:  # optional
                    paths2 = paths1
                    paths2 = Condition.call(parser, paths2)
                    paths1 = paths2
                except TransmuterSymbolMatchError:  # optional
                    pass

                paths0 = paths1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return paths0


class ProductionPrecedence(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}
        paths0 = Identifier.call(parser.lexer, paths0)
        return paths0


class IterationExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    paths1 = paths0
                    paths1 = PrimaryExpression.call(parser, paths1)

                    while transmuter_once:  # optional selection
                        try:  # option 1
                            paths2 = paths1
                            paths2 = Asterisk.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            paths2 = paths1
                            paths2 = PlusSign.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            paths2 = paths1
                            paths2 = QuestionMark.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            paths2 = paths1
                            paths2 = ExpressionRange.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 4
                            pass

                        break  # optional selection

                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    paths1 = paths0

                    while transmuter_once:  # selection
                        try:  # option 1
                            paths2 = paths1
                            paths2 = LeftCurlyBracket.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            paths2 = paths1
                            paths2 = LeftCurlyBracketSolidus.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    paths1 = SelectionExpression.call(parser, paths1)
                    paths1 = RightCurlyBracket.call(parser.lexer, paths1)
                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return paths0


class PrimaryExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    paths1 = paths0

                    while transmuter_once:  # selection
                        try:  # option 1
                            paths2 = paths1
                            paths2 = OrdChar.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            paths2 = paths1
                            paths2 = QuotedChar.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            paths2 = paths1
                            paths2 = FullStop.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            paths2 = paths1
                            paths2 = BracketExpression.call(parser.lexer, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 4
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    paths1 = paths0
                    paths1 = Identifier.call(parser.lexer, paths1)

                    try:  # optional
                        paths2 = paths1
                        paths2 = Condition.call(parser, paths2)
                        paths1 = paths2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            try:  # option 3
                paths1 = paths0
                paths1 = LeftParenthesis.call(parser.lexer, paths1)
                paths1 = SelectionExpression.call(parser, paths1)
                paths1 = RightParenthesis.call(parser.lexer, paths1)

                if syntactic in parser.lexer.conditions:
                    try:  # optional
                        paths2 = paths1
                        paths2 = Condition.call(parser, paths2)
                        paths1 = paths2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                paths0 = paths1
                break
            except TransmuterSymbolMatchError:  # option 3
                pass

            try:  # option 4
                if syntactic in parser.lexer.conditions:
                    paths1 = paths0

                    while transmuter_once:  # selection
                        try:  # option 1
                            paths2 = paths1
                            paths2 = OptionalExpression.call(parser, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            paths2 = paths1
                            paths2 = IterationExpression.call(parser, paths2)
                            paths1 = paths2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    try:  # optional
                        paths2 = paths1
                        paths2 = Condition.call(parser, paths2)
                        paths1 = paths2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    paths0 = paths1
                    break
            except TransmuterSymbolMatchError:  # option 4
                pass

            raise TransmuterSymbolMatchError()  # selection

        return paths0


class NegationCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while True:  # iteration
            try:
                paths1 = paths0
                paths1 = ExclamationMark.call(parser.lexer, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:
                break  # iteration

        paths0 = PrimitiveCondition.call(parser, paths0)
        return paths0


class OptionalExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                paths1 = paths0
                paths1 = LeftSquareBracket.call(parser.lexer, paths1)
                paths0 = paths1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                paths1 = paths0
                paths1 = LeftSquareBracketSolidus.call(parser.lexer, paths1)
                paths0 = paths1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        paths0 = SelectionExpression.call(parser, paths0)
        paths0 = RightSquareBracket.call(parser.lexer, paths0)
        return paths0


class PrimitiveCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        paths0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                paths1 = paths0
                paths1 = Identifier.call(parser.lexer, paths1)
                paths0 = paths1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                paths1 = paths0
                paths1 = LeftParenthesis.call(parser.lexer, paths1)
                paths1 = DisjunctionCondition.call(parser, paths1)
                paths1 = RightParenthesis.call(parser.lexer, paths1)
                paths0 = paths1
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return paths0


class Parser(TransmuterParser):
    NONTERMINAL_TYPES = {Grammar, Production, ProductionHeader, ProductionBody, Condition, ProductionSpecifiers, ProductionPrecedences, SelectionExpression, DisjunctionCondition, ProductionSpecifierList, ProductionPrecedenceList, SequenceExpression, ConjunctionCondition, ProductionSpecifier, ProductionPrecedence, IterationExpression, PrimaryExpression, NegationCondition, OptionalExpression, PrimitiveCondition}
