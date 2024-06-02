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
from ..lexical import TransmuterTerminal
from ..syntactic import transmuter_once, TransmuterNonterminalType, TransmuterParser, TransmuterSymbolMatchError
from .common import lexical, syntactic
from .lexical import Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, GreaterThanSign, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, Ignore, Optional, Start, Asterisk, PlusSign, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket


class Grammar(TransmuterNonterminalType):
    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return True

    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(Production, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = parser.call(Production, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class Production(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(ProductionHeader, next_terminals0)
        next_terminals0 = parser.call(ProductionBody, next_terminals0)
        return next_terminals0


class ProductionHeader(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(Identifier, next_terminals0)

        if lexical in parser.lexer.conditions:
            try:  # optional
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(Condition, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:  # optional
                pass

        try:  # optional
            next_terminals1 = next_terminals0
            next_terminals1 = parser.call(ProductionSpecifiers, next_terminals1)
            next_terminals0 = next_terminals1
        except TransmuterSymbolMatchError:  # optional
            pass

        if lexical in parser.lexer.conditions:
            try:  # optional
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(ProductionPrecedences, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:  # optional
                pass

        next_terminals0 = parser.call(Colon, next_terminals0)
        return next_terminals0


class ProductionBody(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(SelectionExpression, next_terminals0)
        next_terminals0 = parser.call(Semicolon, next_terminals0)
        return next_terminals0


class Condition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(CommercialAt, next_terminals0)
        next_terminals0 = parser.call(DisjunctionCondition, next_terminals0)
        return next_terminals0


class ProductionSpecifiers(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(LeftParenthesis, next_terminals0)
        next_terminals0 = parser.call(ProductionSpecifierList, next_terminals0)
        next_terminals0 = parser.call(RightParenthesis, next_terminals0)
        return next_terminals0


class ProductionPrecedences(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(GreaterThanSign, next_terminals0)
        next_terminals0 = parser.call(ProductionPrecedenceList, next_terminals0)
        return next_terminals0


class SelectionExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(SequenceExpression, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                while transmuter_once:  # selection
                    try:  # option 1
                        next_terminals2 = next_terminals1
                        next_terminals2 = parser.call(VerticalLine, next_terminals2)
                        next_terminals1 = next_terminals2
                        break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(Solidus, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                next_terminals1 = parser.call(SequenceExpression, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class DisjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(ConjunctionCondition, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = parser.call(DoubleVerticalLine, next_terminals1)
                next_terminals1 = parser.call(ConjunctionCondition, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class ProductionSpecifierList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(ProductionSpecifier, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = parser.call(Comma, next_terminals1)
                next_terminals1 = parser.call(ProductionSpecifier, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_terminals0


class ProductionPrecedenceList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}
        next_terminals0 = parser.call(ProductionPrecedence, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = parser.call(Comma, next_terminals1)
                next_terminals1 = parser.call(ProductionPrecedence, next_terminals1)
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
                    next_terminals1 = parser.call(IterationExpression, next_terminals1)
                    next_terminals2 = next_terminals1

                    while True:  # iteration
                        try:
                            next_terminals2 = parser.call(IterationExpression, next_terminals2)
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
                    next_terminals1 = parser.call(PrimaryExpression, next_terminals1)
                    next_terminals2 = next_terminals1

                    while True:  # iteration
                        try:
                            next_terminals2 = parser.call(PrimaryExpression, next_terminals2)
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
        next_terminals0 = parser.call(NegationCondition, next_terminals0)
        next_terminals1 = next_terminals0

        while True:  # iteration
            try:
                next_terminals1 = parser.call(DoubleAmpersand, next_terminals1)
                next_terminals1 = parser.call(NegationCondition, next_terminals1)
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
                next_terminals1 = parser.call(Identifier, next_terminals1)
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
                                    next_terminals3 = parser.call(Ignore, next_terminals3)
                                    next_terminals2 = next_terminals3
                                    break
                                except TransmuterSymbolMatchError:  # option 1
                                    pass

                                try:  # option 2
                                    next_terminals3 = next_terminals2
                                    next_terminals3 = parser.call(Optional, next_terminals3)
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
                            next_terminals2 = parser.call(Start, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                try:  # optional
                    next_terminals2 = next_terminals1
                    next_terminals2 = parser.call(Condition, next_terminals2)
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
        next_terminals0 = parser.call(Identifier, next_terminals0)
        return next_terminals0


class IterationExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_terminals1 = next_terminals0
                    next_terminals1 = parser.call(PrimaryExpression, next_terminals1)

                    while transmuter_once:  # optional selection
                        try:  # option 1
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(Asterisk, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(PlusSign, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(QuestionMark, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(ExpressionRange, next_terminals2)
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
                            next_terminals2 = parser.call(LeftCurlyBracket, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(LeftCurlyBracketSolidus, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    next_terminals1 = parser.call(SelectionExpression, next_terminals1)
                    next_terminals1 = parser.call(RightCurlyBracket, next_terminals1)
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
                            next_terminals2 = parser.call(OrdChar, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(QuotedChar, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(FullStop, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(BracketExpression, next_terminals2)
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
                    next_terminals1 = parser.call(Identifier, next_terminals1)

                    try:  # optional
                        next_terminals2 = next_terminals1
                        next_terminals2 = parser.call(Condition, next_terminals2)
                        next_terminals1 = next_terminals2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    next_terminals0 = next_terminals1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            try:  # option 3
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(LeftParenthesis, next_terminals1)
                next_terminals1 = parser.call(SelectionExpression, next_terminals1)
                next_terminals1 = parser.call(RightParenthesis, next_terminals1)

                if syntactic in parser.lexer.conditions:
                    try:  # optional
                        next_terminals2 = next_terminals1
                        next_terminals2 = parser.call(Condition, next_terminals2)
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
                            next_terminals2 = parser.call(OptionalExpression, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_terminals2 = next_terminals1
                            next_terminals2 = parser.call(IterationExpression, next_terminals2)
                            next_terminals1 = next_terminals2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    try:  # optional
                        next_terminals2 = next_terminals1
                        next_terminals2 = parser.call(Condition, next_terminals2)
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
                next_terminals1 = parser.call(ExclamationMark, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:
                break  # iteration

        next_terminals0 = parser.call(PrimitiveCondition, next_terminals0)
        return next_terminals0


class OptionalExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(LeftSquareBracket, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(LeftSquareBracketSolidus, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        next_terminals0 = parser.call(SelectionExpression, next_terminals0)
        next_terminals0 = parser.call(RightSquareBracket, next_terminals0)
        return next_terminals0


class PrimitiveCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_terminal: TransmuterTerminal | None) -> set[TransmuterTerminal]:
        next_terminals0 = {current_terminal}

        while transmuter_once:  # selection
            try:  # option 1
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(Identifier, next_terminals1)
                next_terminals0 = next_terminals1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_terminals1 = next_terminals0
                next_terminals1 = parser.call(LeftParenthesis, next_terminals1)
                next_terminals1 = parser.call(DisjunctionCondition, next_terminals1)
                next_terminals1 = parser.call(RightParenthesis, next_terminals1)
                next_terminals0 = next_terminals1
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_terminals0


class Parser(TransmuterParser):
    NONTERMINAL_TYPES = {Grammar, Production, ProductionHeader, ProductionBody, Condition, ProductionSpecifiers, ProductionPrecedences, SelectionExpression, DisjunctionCondition, ProductionSpecifierList, ProductionPrecedenceList, SequenceExpression, ConjunctionCondition, ProductionSpecifier, ProductionPrecedence, IterationExpression, PrimaryExpression, NegationCondition, OptionalExpression, PrimitiveCondition}
