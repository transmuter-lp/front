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
        next_terminals0 = {current_terminal}
        next_terminals0 = Production.call(parser, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = Production.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class Production(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = ProductionHeader.call(parser, next_terminals0)
        next_terminals0 = ProductionBody.call(parser, next_terminals0)
        return next_terminals0


class ProductionHeader(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = Identifier.call(parser.lexer, next_terminals0)

        if lexical in parser.lexer.conditions:
            try:  # optional
                next_terminals1 = next_terminals0
                next_terminals1 = Condition.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:  # optional
                pass

        try:  # optional
            next_terminals1 = next_terminals0
            next_terminals1 = ProductionSpecifiers.call(parser, next_terminals1)
            next_terminals0 = next_terminals1
        except TransmuterSymbolMatchError:  # optional
            pass

        if lexical in parser.lexer.conditions:
            try:  # optional
                next_terminals1 = next_terminals0
                next_terminals1 = ProductionPrecedences.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:  # optional
                pass

        next_terminals0 = Colon.call(parser.lexer, next_terminals0)
        return next_terminals0


class ProductionBody(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = SelectionExpression.call(parser, next_terminals0)
        next_terminals0 = Semicolon.call(parser.lexer, next_terminals0)
        return next_terminals0


class Condition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = CommercialAt.call(parser.lexer, next_terminals0)
        next_terminals0 = DisjunctionCondition.call(parser, next_terminals0)
        return next_terminals0


class ProductionSpecifiers(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = LeftParenthesis.call(parser.lexer, next_terminals0)
        next_terminals0 = ProductionSpecifierList.call(parser, next_terminals0)
        next_terminals0 = RightParenthesis.call(parser.lexer, next_terminals0)
        return next_terminals0


class ProductionPrecedences(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = GreaterThanSign.call(parser.lexer, next_terminals0)
        next_terminals0 = ProductionPrecedenceList.call(parser, next_terminals0)
        return next_terminals0


class SelectionExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = SequenceExpression.call(parser, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                while transmuter_once:  # selection
                    try:  # option 1
                        next_terminals2 = next_terminals1
                        next_terminals2 = VerticalLine.call(parser.lexer, next_terminals2)
                        next_terminals1 = next_terminals2
                        break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            next_terminals2 = next_terminals1
                            next_terminals2 = Solidus.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                next_terminals1 = SequenceExpression.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class DisjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = ConjunctionCondition.call(parser, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = DoubleVerticalLine.call(parser.lexer, next_terminals1)
                next_terminals1 = ConjunctionCondition.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class ProductionSpecifierList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = ProductionSpecifier.call(parser, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = Comma.call(parser.lexer, next_terminals1)
                next_terminals1 = ProductionSpecifier.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class ProductionPrecedenceList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = ProductionPrecedence.call(parser, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = Comma.call(parser.lexer, next_terminals1)
                next_terminals1 = ProductionPrecedence.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class SequenceExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_terminals1 = next_terminals0
                    next_terminals1 = IterationExpression.call(parser, next_terminals1)
                    next_terminals2 = next_terminals1

                    while True:  # iteration
                        try:
                            next_terminals2 = IterationExpression.call(parser, next_terminals2)
                            next_terminals1 = next_terminals2
                        except TransmuterSymbolMatchError:
                            break  # iteration

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    next_terminals1 = next_terminals0
                    next_terminals1 = PrimaryExpression.call(parser, next_terminals1)
                    next_terminals2 = next_terminals1

                    while True:  # iteration
                        try:
                            next_terminals2 = PrimaryExpression.call(parser, next_terminals2)
                            next_terminals1 = next_terminals2
                        except TransmuterSymbolMatchError:
                            break  # iteration

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_terminals0


class ConjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = NegationCondition.call(parser, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = DoubleAmpersand.call(parser.lexer, next_terminals1)
                next_terminals1 = NegationCondition.call(parser, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class ProductionSpecifier(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                next_terminals1 = next_terminals0
                next_terminals1 = Identifier.call(parser.lexer, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_terminals1 = next_terminals0

                while transmuter_once:  # selection
                    try:  # option 1
                        if lexical in parser.lexer.conditions:
                            next_terminals2 = next_terminals1

                            while transmuter_once:  # selection
                                try:  # option 1
                                    next_terminals3 = next_terminals2
                                    next_terminals3 = Ignore.call(parser.lexer, next_terminals3)
                                    next_terminals2 = next_terminals3
                                    break
                                except TransmuterSymbolMatchError:  # option 1
                                    pass

                                try:  # option 2
                                    next_terminals3 = next_terminals2
                                    next_terminals3 = Optional.call(parser.lexer, next_terminals3)
                                    next_terminals2 = next_terminals3
                                    break
                                except TransmuterSymbolMatchError:  # option 2
                                    pass

                                raise TransmuterSymbolMatchError()  # selection

                            next_terminals1 = next_terminals2
                            break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            next_terminals2 = next_terminals1
                            next_terminals2 = Start.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                try:  # optional
                    next_terminals2 = next_terminals1
                    next_terminals2 = Condition.call(parser, next_terminals2)
                    next_terminals1 = next_terminals2
                except TransmuterSymbolMatchError:  # optional
                    pass

                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_terminals0


class ProductionPrecedence(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = Identifier.call(parser.lexer, next_terminals0)
        return next_terminals0


class IterationExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_terminals1 = next_terminals0
                    next_terminals1 = PrimaryExpression.call(parser, next_terminals1)

                    while transmuter_once:  # optional selection
                        try:  # option 1
                            next_terminals2 = next_terminals1
                            next_terminals2 = Asterisk.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = PlusSign.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            next_terminals2 = next_terminals1
                            next_terminals2 = QuestionMark.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            next_terminals2 = next_terminals1
                            next_terminals2 = ExpressionRange.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 4
                            pass

                        break  # optional selection

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    next_terminals1 = next_terminals0

                    while transmuter_once:  # selection
                        try:  # option 1
                            next_terminals2 = next_terminals1
                            next_terminals2 = LeftCurlyBracket.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = LeftCurlyBracketSolidus.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    next_terminals1 = SelectionExpression.call(parser, next_terminals1)
                    next_terminals1 = RightCurlyBracket.call(parser.lexer, next_terminals1)
                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_terminals0


class PrimaryExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_terminals1 = next_terminals0

                    while transmuter_once:  # selection
                        try:  # option 1
                            next_terminals2 = next_terminals1
                            next_terminals2 = OrdChar.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = QuotedChar.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            next_terminals2 = next_terminals1
                            next_terminals2 = FullStop.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            next_terminals2 = next_terminals1
                            next_terminals2 = BracketExpression.call(parser.lexer, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 4
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    next_terminals1 = next_terminals0
                    next_terminals1 = Identifier.call(parser.lexer, next_terminals1)

                    try:  # optional
                        next_terminals2 = next_terminals1
                        next_terminals2 = Condition.call(parser, next_terminals2)
                        next_terminals1 = next_terminals2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            try:  # option 3
                next_terminals1 = next_terminals0
                next_terminals1 = LeftParenthesis.call(parser.lexer, next_terminals1)
                next_terminals1 = SelectionExpression.call(parser, next_terminals1)
                next_terminals1 = RightParenthesis.call(parser.lexer, next_terminals1)

                if syntactic in parser.lexer.conditions:
                    try:  # optional
                        next_terminals2 = next_terminals1
                        next_terminals2 = Condition.call(parser, next_terminals2)
                        next_terminals1 = next_terminals2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 3
                pass

            try:  # option 4
                if syntactic in parser.lexer.conditions:
                    next_terminals1 = next_terminals0

                    while transmuter_once:  # selection
                        try:  # option 1
                            next_terminals2 = next_terminals1
                            next_terminals2 = OptionalExpression.call(parser, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = IterationExpression.call(parser, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    try:  # optional
                        next_terminals2 = next_terminals1
                        next_terminals2 = Condition.call(parser, next_terminals2)
                        next_terminals1 = next_terminals2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 4
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_terminals0


class NegationCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while True:  # iteration
            try:
                next_terminals1 = next_terminals0
                next_terminals1 = ExclamationMark.call(parser.lexer, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        next_terminals0 = PrimitiveCondition.call(parser, next_terminals0)
        return next_terminals0


class OptionalExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                next_terminals1 = next_terminals0
                next_terminals1 = LeftSquareBracket.call(parser.lexer, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_terminals1 = next_terminals0
                next_terminals1 = LeftSquareBracketSolidus.call(parser.lexer, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        next_terminals0 = SelectionExpression.call(parser, next_terminals0)
        next_terminals0 = RightSquareBracket.call(parser.lexer, next_terminals0)
        return next_terminals0


class PrimitiveCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                next_terminals1 = next_terminals0
                next_terminals1 = Identifier.call(parser.lexer, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_terminals1 = next_terminals0
                next_terminals1 = LeftParenthesis.call(parser.lexer, next_terminals1)
                next_terminals1 = DisjunctionCondition.call(parser, next_terminals1)
                next_terminals1 = RightParenthesis.call(parser.lexer, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_terminals0


class Parser(TransmuterParser):
    NONTERMINAL_TYPES = {Grammar, Production, ProductionHeader, ProductionBody, Condition, ProductionSpecifiers, ProductionPrecedences, SelectionExpression, DisjunctionCondition, ProductionSpecifierList, ProductionPrecedenceList, SequenceExpression, ConjunctionCondition, ProductionSpecifier, ProductionPrecedence, IterationExpression, PrimaryExpression, NegationCondition, OptionalExpression, PrimitiveCondition}
