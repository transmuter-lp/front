# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
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

import builtins

from ...semantic.common import TransmuterNonterminalTreeNode
from ..semantic import (
    LexicalSimplePattern,
    LexicalWildcardPattern,
    LexicalRangePattern,
    LexicalBracketPattern,
    LexicalState,
)
from .common import (
    AetherCommonFileFold,
    AetherConditionFold,
    AetherLexicalFileFold,
)


def _escape_identifier(value: str) -> str:
    if (
        value
        in (
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "case",
            "class",
            "Conditions",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "False",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "in",
            "import",
            "is",
            "lambda",
            "Lexer",
            "match",
            "None",
            "nonlocal",
            "not",
            "or",
            "Parser",
            "pass",
            "raise",
            "return",
            "TransmuterCondition",
            "TransmuterConditions",
            "TransmuterInternalError",
            "TransmuterLexer",
            "TransmuterLexingState",
            "TransmuterNonterminalType",
            "TransmuterParser",
            "TransmuterParsingState",
            "transmuter_selection",
            "TransmuterTerminalTag",
            "True",
            "try",
            "type",
            "while",
            "with",
            "yield",
        )
        or value in builtins.__dict__
    ):
        return f"{value}_"

    return value


def _escape_char(value: str) -> str:
    if value == '"':
        return '\\"'

    if len(value) == 2 and value[0] == "\\" and value[1] in " $()*+.;?[^{|":
        return value[1]

    return value


class CommonFileFold(AetherCommonFileFold):
    def fold_file(self, conditions: list[str]) -> str:
        return f"from transmuter.front.common import TransmuterConditions, TransmuterCondition\n\n\nclass Conditions(TransmuterConditions):\n    {'\n    '.join(conditions)}"

    def fold_condition(self, name: str) -> str:
        return f"{_escape_identifier(name)} = TransmuterCondition()"


class ConditionFold(AetherConditionFold):
    def fold_disjunction(
        self, node: TransmuterNonterminalTreeNode, children: list[str]
    ) -> str:
        return " or ".join(children)

    def fold_conjunction(
        self, node: TransmuterNonterminalTreeNode, children: list[str]
    ) -> str:
        return " and ".join(children)

    def fold_negation(
        self, node: TransmuterNonterminalTreeNode, child: str
    ) -> str:
        assert len(node.children) > 0
        assert isinstance(node.children[-1], TransmuterNonterminalTreeNode)

        if len(node.children[-1].children) == 1:
            return child.replace(" in ", " not in ", 1)

        return f"not {child}"

    def fold_primitive(
        self, node: TransmuterNonterminalTreeNode, child: str
    ) -> str:
        if len(node.children) == 1:
            return f"Conditions.{_escape_identifier(child)} in conditions"

        return f"({child})"


class LexicalFileFold(AetherLexicalFileFold):
    def fold_file(
        self, terminal_tag_names: list[str], terminal_tags: list[str]
    ) -> str:
        return f"from transmuter.front.lexical import TransmuterTerminalTag, TransmuterLexer\nfrom .common import Conditions\n\n\n{'\n\n\n'.join(terminal_tags)}\n\n\nclass Lexer(TransmuterLexer):\n    TERMINAL_TAGS = [{', '.join(_escape_identifier(t) for t in terminal_tag_names)}]"

    def fold_terminal_tag(
        self,
        name: str,
        states_start: str | None,
        start: str | None,
        ignore: str | None,
        positives: str | None,
        negatives: str | None,
        nfa: str,
    ) -> str:
        terminal_tag = (
            f"class {_escape_identifier(name)}(TransmuterTerminalTag):\n"
        )

        if states_start is not None:
            terminal_tag += f"    {states_start}\n\n"

        if start is not None:
            terminal_tag += f"{self.indent(start)}\n\n"

        if ignore is not None:
            terminal_tag += f"{self.indent(ignore)}\n\n"

        if positives is not None:
            terminal_tag += f"{self.indent(positives)}\n\n"

        if negatives is not None:
            terminal_tag += f"{self.indent(negatives)}\n\n"

        terminal_tag += f"{self.indent(nfa)}"
        return terminal_tag

    def fold_states_start(self, value: list[int]) -> str:
        return f"STATES_START = {' | '.join(f'1 << {s}' for s in value)}"

    def fold_start(self, value: str) -> str:
        return f"@staticmethod\ndef start(conditions):\n    return {value}"

    def fold_ignore(self, value: str | None) -> str:
        return f"@staticmethod\ndef ignore(conditions):\n    return {value if value is not None else 'True'}"

    def fold_positives(
        self, static_positives: str, conditional_positives: list[str]
    ) -> str:
        positives = f"@staticmethod\ndef positives(conditions):\n    {static_positives}\n"

        if len(conditional_positives) > 0:
            positives += (
                f"\n{self.indent('\n\n'.join(conditional_positives))}\n\n"
            )

        positives += "    return positives"
        return positives

    def fold_negatives(
        self, static_negatives: str, conditional_negatives: list[str]
    ) -> str:
        negatives = f"@staticmethod\ndef negatives(conditions):\n    {static_negatives}\n"

        if len(conditional_negatives) > 0:
            negatives += (
                f"\n{self.indent('\n\n'.join(conditional_negatives))}\n\n"
            )

        negatives += "    return negatives"
        return negatives

    def fold_nfa(self, states: list[str]) -> str:
        return f"@staticmethod\ndef nfa(current_states, char):\n    state_accept = False\n    next_states = 0\n\n{self.indent('\n\n'.join(states))}\n\n    return state_accept, next_states"

    def fold_static_positives(self, value: list[str]) -> str:
        if len(value) == 0:
            return "positives = set()"

        return f"positives = {{{', '.join(_escape_identifier(p) for p in value)}}}"

    def fold_conditional_positive(self, value: str, condition: str) -> str:
        return (
            f"if {condition}:\n    positives.add({_escape_identifier(value)})"
        )

    def fold_static_negatives(self, value: list[str]) -> str:
        if len(value) == 0:
            return "negatives = set()"

        return f"negatives = {{{', '.join(_escape_identifier(p) for p in value)}}}"

    def fold_conditional_negative(self, value: str, condition: str) -> str:
        return (
            f"if {condition}:\n    negatives.add({_escape_identifier(value)})"
        )

    def fold_state(self, index: int, value: LexicalState) -> str:
        state = f"if 1 << {index} & current_states{' and ' if not isinstance(value.pattern, LexicalWildcardPattern) else ''}"

        if isinstance(value.pattern, LexicalSimplePattern):
            state += f'char == "{_escape_char(value.pattern.char)}"'
        elif isinstance(value.pattern, LexicalBracketPattern):
            patterns = []
            i = 0

            while i < len(value.pattern.patterns):
                pattern = value.pattern.patterns[i]

                if isinstance(pattern, LexicalSimplePattern):
                    if i + 1 < len(value.pattern.patterns) and isinstance(
                        value.pattern.patterns[i + 1], LexicalSimplePattern
                    ):
                        patterns.append(
                            f'char in "{_escape_char(pattern.char)}{_escape_char(value.pattern.patterns[i + 1].char)}'
                        )
                        j = i + 2

                        while j < len(value.pattern.patterns) and isinstance(
                            value.pattern.patterns[j], LexicalSimplePattern
                        ):
                            patterns[-1] += _escape_char(
                                value.pattern.patterns[j].char
                            )
                            j += 1

                        patterns[-1] += '"'
                        i = j
                        continue

                    patterns.append(f'char == "{_escape_char(pattern.char)}"')
                else:
                    assert isinstance(pattern, LexicalRangePattern)
                    patterns.append(
                        f'"{_escape_char(pattern.first_char)}" <= char <= "{_escape_char(pattern.last_char)}"'
                    )

                i += 1

            if len(patterns) > 1:
                if value.pattern.negative_match:
                    state += "not "

                state += f"({' or '.join(patterns)})"
            else:
                assert len(patterns) == 1

                if value.pattern.negative_match:
                    if patterns[0].startswith("char in"):
                        state += patterns[0].replace(
                            "char in", "char not in", 1
                        )
                    elif patterns[0].startswith("char =="):
                        state += patterns[0].replace("char ==", "char !=", 1)
                    else:
                        state += f"not {patterns[0]}"
                else:
                    state += patterns[0]

        state += ":"

        if value.state_accept:
            state += "\n    state_accept = True"

        if len(value.next_states_indexes) > 0:
            state += f"\n    next_states |= {' | '.join(f'1 << {n}' for n in value.next_states_indexes)}"

        return state
