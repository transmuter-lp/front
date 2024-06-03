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
from ..syntactic import transmuter_once, TransmuterNonterminalType, TransmuterParsingState, TransmuterParser, TransmuterSymbolMatchError
from .common import lexical, syntactic
from .lexical import Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, GreaterThanSign, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, Ignore, Optional, Start, Asterisk, PlusSign, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket


class Grammar(TransmuterNonterminalType):
    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return True

    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Production, next_states0)
        next_states1 = next_states0

        while True:  # iteration
            try:
                next_states1 = parser.call(Production, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_states0


class Production(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionHeader, next_states0)
        next_states0 = parser.call(ProductionBody, next_states0)
        return next_states0


class ProductionHeader(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Identifier, next_states0)

        if lexical in parser.lexer.conditions:
            try:  # optional
                next_states1 = next_states0
                next_states1 = parser.call(Condition, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:  # optional
                pass

        try:  # optional
            next_states1 = next_states0
            next_states1 = parser.call(ProductionSpecifiers, next_states1)
            next_states0 = next_states1
        except TransmuterSymbolMatchError:  # optional
            pass

        if lexical in parser.lexer.conditions:
            try:  # optional
                next_states1 = next_states0
                next_states1 = parser.call(ProductionPrecedences, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:  # optional
                pass

        next_states0 = parser.call(Colon, next_states0)
        return next_states0


class ProductionBody(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(SelectionExpression, next_states0)
        next_states0 = parser.call(Semicolon, next_states0)
        return next_states0


class Condition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(CommercialAt, next_states0)
        next_states0 = parser.call(DisjunctionCondition, next_states0)
        return next_states0


class ProductionSpecifiers(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(LeftParenthesis, next_states0)
        next_states0 = parser.call(ProductionSpecifierList, next_states0)
        next_states0 = parser.call(RightParenthesis, next_states0)
        return next_states0


class ProductionPrecedences(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(GreaterThanSign, next_states0)
        next_states0 = parser.call(ProductionPrecedenceList, next_states0)
        return next_states0


class SelectionExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(SequenceExpression, next_states0)
        next_states1 = next_states0

        while True:  # iteration
            try:
                while transmuter_once:  # selection
                    try:  # option 1
                        next_states2 = next_states1
                        next_states2 = parser.call(VerticalLine, next_states2)
                        next_states1 = next_states2
                        break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            next_states2 = next_states1
                            next_states2 = parser.call(Solidus, next_states2)
                            next_states1 = next_states2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                next_states1 = parser.call(SequenceExpression, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_states0


class DisjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ConjunctionCondition, next_states0)
        next_states1 = next_states0

        while True:  # iteration
            try:
                next_states1 = parser.call(DoubleVerticalLine, next_states1)
                next_states1 = parser.call(ConjunctionCondition, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_states0


class ProductionSpecifierList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionSpecifier, next_states0)
        next_states1 = next_states0

        while True:  # iteration
            try:
                next_states1 = parser.call(Comma, next_states1)
                next_states1 = parser.call(ProductionSpecifier, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_states0


class ProductionPrecedenceList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionPrecedence, next_states0)
        next_states1 = next_states0

        while True:  # iteration
            try:
                next_states1 = parser.call(Comma, next_states1)
                next_states1 = parser.call(ProductionPrecedence, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_states0


class SequenceExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_states1 = next_states0
                    next_states1 = parser.call(IterationExpression, next_states1)
                    next_states2 = next_states1

                    while True:  # iteration
                        try:
                            next_states2 = parser.call(IterationExpression, next_states2)
                            next_states1 = next_states2
                        except TransmuterSymbolMatchError:
                            break  # iteration

                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    next_states1 = next_states0
                    next_states1 = parser.call(PrimaryExpression, next_states1)
                    next_states2 = next_states1

                    while True:  # iteration
                        try:
                            next_states2 = parser.call(PrimaryExpression, next_states2)
                            next_states1 = next_states2
                        except TransmuterSymbolMatchError:
                            break  # iteration

                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_states0


class ConjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(NegationCondition, next_states0)
        next_states1 = next_states0

        while True:  # iteration
            try:
                next_states1 = parser.call(DoubleAmpersand, next_states1)
                next_states1 = parser.call(NegationCondition, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        return next_states0


class ProductionSpecifier(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # selection
            try:  # option 1
                next_states1 = next_states0
                next_states1 = parser.call(Identifier, next_states1)
                next_states0 = next_states1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_states1 = next_states0

                while transmuter_once:  # selection
                    try:  # option 1
                        if lexical in parser.lexer.conditions:
                            next_states2 = next_states1

                            while transmuter_once:  # selection
                                try:  # option 1
                                    next_states3 = next_states2
                                    next_states3 = parser.call(Ignore, next_states3)
                                    next_states2 = next_states3
                                    break
                                except TransmuterSymbolMatchError:  # option 1
                                    pass

                                try:  # option 2
                                    next_states3 = next_states2
                                    next_states3 = parser.call(Optional, next_states3)
                                    next_states2 = next_states3
                                    break
                                except TransmuterSymbolMatchError:  # option 2
                                    pass

                                raise TransmuterSymbolMatchError()  # selection

                            next_states1 = next_states2
                            break
                    except TransmuterSymbolMatchError:  # option 1
                        pass

                    try:  # option 2
                        if syntactic in parser.lexer.conditions:
                            next_states2 = next_states1
                            next_states2 = parser.call(Start, next_states2)
                            next_states1 = next_states2
                            break
                    except TransmuterSymbolMatchError:  # option 2
                        pass

                    raise TransmuterSymbolMatchError()  # selection

                try:  # optional
                    next_states2 = next_states1
                    next_states2 = parser.call(Condition, next_states2)
                    next_states1 = next_states2
                except TransmuterSymbolMatchError:  # optional
                    pass

                next_states0 = next_states1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_states0


class ProductionPrecedence(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Identifier, next_states0)
        return next_states0


class IterationExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_states1 = next_states0
                    next_states1 = parser.call(PrimaryExpression, next_states1)

                    while transmuter_once:  # optional selection
                        try:  # option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(Asterisk, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(PlusSign, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            next_states2 = next_states1
                            next_states2 = parser.call(QuestionMark, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            next_states2 = next_states1
                            next_states2 = parser.call(ExpressionRange, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 4
                            pass

                        break  # optional selection

                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    next_states1 = next_states0

                    while transmuter_once:  # selection
                        try:  # option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(LeftCurlyBracket, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(LeftCurlyBracketSolidus, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    next_states1 = parser.call(SelectionExpression, next_states1)
                    next_states1 = parser.call(RightCurlyBracket, next_states1)
                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_states0


class PrimaryExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # selection
            try:  # option 1
                if lexical in parser.lexer.conditions:
                    next_states1 = next_states0

                    while transmuter_once:  # selection
                        try:  # option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(OrdChar, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(QuotedChar, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        try:  # option 3
                            next_states2 = next_states1
                            next_states2 = parser.call(FullStop, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 3
                            pass

                        try:  # option 4
                            next_states2 = next_states1
                            next_states2 = parser.call(BracketExpression, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 4
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                if syntactic in parser.lexer.conditions:
                    next_states1 = next_states0
                    next_states1 = parser.call(Identifier, next_states1)

                    try:  # optional
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                        next_states1 = next_states2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 2
                pass

            try:  # option 3
                next_states1 = next_states0
                next_states1 = parser.call(LeftParenthesis, next_states1)
                next_states1 = parser.call(SelectionExpression, next_states1)
                next_states1 = parser.call(RightParenthesis, next_states1)

                if syntactic in parser.lexer.conditions:
                    try:  # optional
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                        next_states1 = next_states2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                next_states0 = next_states1
                break
            except TransmuterSymbolMatchError:  # option 3
                pass

            try:  # option 4
                if syntactic in parser.lexer.conditions:
                    next_states1 = next_states0

                    while transmuter_once:  # selection
                        try:  # option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(OptionalExpression, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 1
                            pass

                        try:  # option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(IterationExpression, next_states2)
                            next_states1 = next_states2
                            break
                        except TransmuterSymbolMatchError:  # option 2
                            pass

                        raise TransmuterSymbolMatchError()  # selection

                    try:  # optional
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                        next_states1 = next_states2
                    except TransmuterSymbolMatchError:  # optional
                        pass

                    next_states0 = next_states1
                    break
            except TransmuterSymbolMatchError:  # option 4
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_states0


class NegationCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while True:  # iteration
            try:
                next_states1 = next_states0
                next_states1 = parser.call(ExclamationMark, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:
                break  # iteration

        next_states0 = parser.call(PrimitiveCondition, next_states0)
        return next_states0


class OptionalExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # selection
            try:  # option 1
                next_states1 = next_states0
                next_states1 = parser.call(LeftSquareBracket, next_states1)
                next_states0 = next_states1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_states1 = next_states0
                next_states1 = parser.call(LeftSquareBracketSolidus, next_states1)
                next_states0 = next_states1
                break
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        next_states0 = parser.call(SelectionExpression, next_states0)
        next_states0 = parser.call(RightSquareBracket, next_states0)
        return next_states0


class PrimitiveCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # selection
            try:  # option 1
                next_states1 = next_states0
                next_states1 = parser.call(Identifier, next_states1)
                next_states0 = next_states1
                break
            except TransmuterSymbolMatchError:  # option 1
                pass

            try:  # option 2
                next_states1 = next_states0
                next_states1 = parser.call(LeftParenthesis, next_states1)
                next_states1 = parser.call(DisjunctionCondition, next_states1)
                next_states1 = parser.call(RightParenthesis, next_states1)
                next_states0 = next_states1
            except TransmuterSymbolMatchError:  # option 2
                pass

            raise TransmuterSymbolMatchError()  # selection

        return next_states0


class Parser(TransmuterParser):
    NONTERMINAL_TYPES = {Grammar, Production, ProductionHeader, ProductionBody, Condition, ProductionSpecifiers, ProductionPrecedences, SelectionExpression, DisjunctionCondition, ProductionSpecifierList, ProductionPrecedenceList, SequenceExpression, ConjunctionCondition, ProductionSpecifier, ProductionPrecedence, IterationExpression, PrimaryExpression, NegationCondition, OptionalExpression, PrimitiveCondition}
