# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2024  Natan Junges <natanajunges@gmail.com>
# Copyright (C) 2024  The Transmuter Project
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

from ..common import TransmuterConditions
from ..syntactic import transmuter_selection, TransmuterNonterminalType, TransmuterParsingState, TransmuterParser, TransmuterSymbolMatchError
from .common import Conditions
from .lexical import Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, PlusSign, HyphenMinus, Ignore, Start, Asterisk, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket


class Grammar(TransmuterNonterminalType):
    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return True

    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Production, next_states0)

        while True:
            next_states1 = next_states0

            try:
                next_states1 = parser.call(Production, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1

        return next_states0


class Production(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionHeader, next_states0)
        next_states0 = parser.call(ProductionBody, next_states0)
        return next_states0


class ProductionHeader(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Identifier, next_states0)

        if Conditions.lexical in parser.lexer.conditions:
            next_states1 = next_states0

            try:
                next_states1 = parser.call(Condition, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1

        try:
            next_states1 = next_states0
            next_states1 = parser.call(ProductionSpecifiers, next_states1)
        except TransmuterSymbolMatchError:
            pass
        else:
            next_states0 = next_states1

        next_states0 = parser.call(Colon, next_states0)
        return next_states0


class ProductionBody(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(SelectionExpression, next_states0)
        next_states0 = parser.call(Semicolon, next_states0)
        return next_states0


class Condition(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(CommercialAt, next_states0)
        next_states0 = parser.call(DisjunctionCondition, next_states0)
        return next_states0


class ProductionSpecifiers(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(LeftParenthesis, next_states0)
        next_states0 = parser.call(ProductionSpecifierList, next_states0)
        next_states0 = parser.call(RightParenthesis, next_states0)
        return next_states0


class SelectionExpression(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(SequenceExpression, next_states0)

        while True:
            next_states1 = next_states0

            try:
                for _ in transmuter_selection:
                    try:
                        next_states2 = next_states1
                        next_states2 = parser.call(VerticalLine, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2
                        break

                    if Conditions.syntactic in parser.lexer.conditions:
                        next_states2 = next_states1

                        try:
                            next_states2 = parser.call(Solidus, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                    raise TransmuterSymbolMatchError()

                next_states1 = parser.call(SequenceExpression, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1

        return next_states0


class DisjunctionCondition(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ConjunctionCondition, next_states0)

        while True:
            next_states1 = next_states0

            try:
                next_states1 = parser.call(DoubleVerticalLine, next_states1)
                next_states1 = parser.call(ConjunctionCondition, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1

        return next_states0


class ProductionSpecifierList(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionSpecifier, next_states0)

        while True:
            next_states1 = next_states0

            try:
                next_states1 = parser.call(Comma, next_states1)
                next_states1 = parser.call(ProductionSpecifier, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1

        return next_states0


class SequenceExpression(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        for _ in transmuter_selection:
            if Conditions.lexical in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(IterationExpression, next_states1)

                    while True:
                        next_states2 = next_states1

                        try:
                            next_states2 = parser.call(IterationExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            break

                        next_states1 = next_states2
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            if Conditions.syntactic in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(PrimaryExpression, next_states1)

                    while True:
                        next_states2 = next_states1

                        try:
                            next_states2 = parser.call(PrimaryExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            break

                        next_states1 = next_states2
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            raise TransmuterSymbolMatchError()

        return next_states0


class ConjunctionCondition(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(NegationCondition, next_states0)

        while True:
            next_states1 = next_states0

            try:
                next_states1 = parser.call(DoubleAmpersand, next_states1)
                next_states1 = parser.call(NegationCondition, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1

        return next_states0


class ProductionSpecifier(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        for _ in transmuter_selection:
            if Conditions.lexical in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    for _ in transmuter_selection:
                        try:
                            next_states2 = next_states1

                            for _ in transmuter_selection:
                                try:
                                    next_states3 = next_states2
                                    next_states3 = parser.call(PlusSign, next_states3)
                                except TransmuterSymbolMatchError:
                                    pass
                                else:
                                    next_states2 = next_states3
                                    break

                                try:
                                    next_states3 = next_states2
                                    next_states3 = parser.call(HyphenMinus, next_states3)
                                except TransmuterSymbolMatchError:
                                    pass
                                else:
                                    next_states2 = next_states3
                                    break

                                raise TransmuterSymbolMatchError()

                            next_states2 = parser.call(Identifier, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(Ignore, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        raise TransmuterSymbolMatchError()
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            if Conditions.syntactic in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(Start, next_states1)
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            raise TransmuterSymbolMatchError()

        try:
            next_states1 = next_states0
            next_states1 = parser.call(Condition, next_states1)
        except TransmuterSymbolMatchError:
            pass
        else:
            next_states0 = next_states1

        return next_states0


class IterationExpression(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        for _ in transmuter_selection:
            if Conditions.lexical in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(PrimaryExpression, next_states1)

                    for _ in transmuter_selection:
                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(Asterisk, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(PlusSign, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(QuestionMark, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(ExpressionRange, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        break
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            if Conditions.syntactic in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    for _ in transmuter_selection:
                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(LeftCurlyBracket, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(LeftCurlyBracketSolidus, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        raise TransmuterSymbolMatchError()

                    next_states1 = parser.call(SelectionExpression, next_states1)
                    next_states1 = parser.call(RightCurlyBracket, next_states1)
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            raise TransmuterSymbolMatchError()

        return next_states0


class PrimaryExpression(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        for _ in transmuter_selection:
            if Conditions.lexical in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    for _ in transmuter_selection:
                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(OrdChar, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(QuotedChar, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(FullStop, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(BracketExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        raise TransmuterSymbolMatchError()
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            if Conditions.syntactic in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(Identifier, next_states1)

                    try:
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            try:
                next_states1 = next_states0
                next_states1 = parser.call(LeftParenthesis, next_states1)
                next_states1 = parser.call(SelectionExpression, next_states1)
                next_states1 = parser.call(RightParenthesis, next_states1)

                if Conditions.syntactic in parser.lexer.conditions:
                    next_states2 = next_states1

                    try:
                        next_states2 = parser.call(Condition, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break

            if Conditions.syntactic in parser.lexer.conditions:
                next_states1 = next_states0

                try:
                    for _ in transmuter_selection:
                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(OptionalExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        try:
                            next_states2 = next_states1
                            next_states2 = parser.call(IterationExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break

                        raise TransmuterSymbolMatchError()

                    try:
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break

            raise TransmuterSymbolMatchError()

        return next_states0


class NegationCondition(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while True:
            next_states1 = next_states0

            try:
                next_states1 = parser.call(ExclamationMark, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1

        next_states0 = parser.call(PrimitiveCondition, next_states0)
        return next_states0


class OptionalExpression(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        for _ in transmuter_selection:
            try:
                next_states1 = next_states0
                next_states1 = parser.call(LeftSquareBracket, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break

            try:
                next_states1 = next_states0
                next_states1 = parser.call(LeftSquareBracketSolidus, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break

            raise TransmuterSymbolMatchError()

        next_states0 = parser.call(SelectionExpression, next_states0)
        next_states0 = parser.call(RightSquareBracket, next_states0)
        return next_states0


class PrimitiveCondition(TransmuterNonterminalType):
    @staticmethod
    def descend(parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        for _ in transmuter_selection:
            try:
                next_states1 = next_states0
                next_states1 = parser.call(Identifier, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break

            try:
                next_states1 = next_states0
                next_states1 = parser.call(LeftParenthesis, next_states1)
                next_states1 = parser.call(DisjunctionCondition, next_states1)
                next_states1 = parser.call(RightParenthesis, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break

            raise TransmuterSymbolMatchError()

        return next_states0


class Parser(TransmuterParser):
    NONTERMINAL_TYPES = {Grammar, Production, ProductionHeader, ProductionBody, Condition, ProductionSpecifiers, SelectionExpression, DisjunctionCondition, ProductionSpecifierList, SequenceExpression, ConjunctionCondition, ProductionSpecifier, IterationExpression, PrimaryExpression, NegationCondition, OptionalExpression, PrimitiveCondition}
