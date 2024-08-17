# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2021, 2023, 2024  Natan Junges <natanajunges@gmail.com>
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

from dataclasses import dataclass, field
from typing import ClassVar

from .common import fset, TransmuterConditions, TransmuterPosition, TransmuterException


class TransmuterTerminalTag:
    STATES_START: int

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return True

    @staticmethod
    def ignore(conditions: TransmuterConditions) -> bool:
        return False

    @staticmethod
    def positives(conditions: TransmuterConditions) -> set[type["TransmuterTerminalTag"]]:
        return set()

    @staticmethod
    def negatives(conditions: TransmuterConditions) -> set[type["TransmuterTerminalTag"]]:
        return set()

    @staticmethod
    def nfa(current_states: int, char: str) -> tuple[bool, int]:
        raise NotImplementedError()


@dataclass(eq=False)
class TransmuterTerminal:
    start_position: TransmuterPosition
    end_position: TransmuterPosition
    value: str
    tags: fset[type[TransmuterTerminalTag]]
    next: "TransmuterTerminal | None" = field(default=None, init=False, repr=False)


@dataclass
class TransmuterLexer:
    TERMINAL_TAGS: ClassVar[fset[type[TransmuterTerminalTag]]]

    input: str
    filename: str
    conditions: TransmuterConditions
    terminal_tags_ignore: fset[type[TransmuterTerminalTag]] = field(init=False, repr=False)
    states_start: dict[type[TransmuterTerminalTag], int] = field(init=False, repr=False)
    terminal_tags_positives: dict[type[TransmuterTerminalTag], fset[type[TransmuterTerminalTag]]] = field(init=False, repr=False)
    terminal_tags_negatives: dict[type[TransmuterTerminalTag], fset[type[TransmuterTerminalTag]]] = field(init=False, repr=False)
    start: TransmuterTerminal | None = field(default=None, init=False, repr=False)
    accepted_terminal_tags: dict[fset[type[TransmuterTerminalTag]], fset[type[TransmuterTerminalTag]]] = field(
        default_factory=dict,
        init=False,
        repr=False
    )

    def __post_init__(self):
        terminal_tags_ignore = set()
        self.states_start = {}
        self.terminal_tags_positives = {}
        self.terminal_tags_negatives = {}

        for terminal_tag in self.TERMINAL_TAGS:
            if terminal_tag.start(self.conditions):
                if terminal_tag.ignore(self.conditions):
                    terminal_tags_ignore.add(terminal_tag)

                self.states_start[terminal_tag] = terminal_tag.STATES_START
                self.terminal_tags_positives[terminal_tag] = fset({
                    tag for tag in terminal_tag.positives(self.conditions) if tag.start(self.conditions)
                })
                self.terminal_tags_negatives[terminal_tag] = fset({
                    tag for tag in terminal_tag.negatives(self.conditions) if tag.start(self.conditions)
                })

        self.terminal_tags_ignore = fset(terminal_tags_ignore)

    def next_terminal(self, current_terminal: TransmuterTerminal | None) -> TransmuterTerminal | None:
        if not current_terminal:
            if not self.start:
                self.start = self.get_terminal(TransmuterPosition(0, 1, 1))

            return self.start

        if not current_terminal.next:
            current_terminal.next = self.get_terminal(current_terminal.end_position)

        return current_terminal.next

    def get_terminal(self, start_position: TransmuterPosition) -> TransmuterTerminal | None:
        while True:
            accepted_terminal_tags = fset()
            accepted_position = start_position
            current_terminal_tags = set()
            current_position = start_position
            current_states = self.states_start

            while current_states:
                if current_position.index_ == len(self.input):
                    if accepted_terminal_tags - self.terminal_tags_ignore:
                        break

                    return None

                current_terminal_tags, current_states = self.nfa(current_states, self.input[current_position.index_])
                current_position = TransmuterPosition(
                    current_position.index_ + 1,
                    current_position.line + (0 if self.input[current_position.index_] != "\n" else 1),
                    current_position.column + 1 if self.input[current_position.index_] != "\n" else 1
                )

                if current_terminal_tags:
                    accepted_terminal_tags = fset(current_terminal_tags)
                    accepted_position = current_position

            if not accepted_terminal_tags:
                raise TransmuterNoTerminalError(self.filename, start_position)

            if accepted_terminal_tags not in self.accepted_terminal_tags:
                accepted_terminal_tags = self.process_positives_negatives(accepted_terminal_tags)
                self.accepted_terminal_tags[accepted_terminal_tags] = accepted_terminal_tags
            else:
                accepted_terminal_tags = self.accepted_terminal_tags[accepted_terminal_tags]

            if accepted_terminal_tags - self.terminal_tags_ignore:
                return TransmuterTerminal(
                    start_position,
                    accepted_position,
                    self.input[start_position.index_:accepted_position.index_],
                    accepted_terminal_tags - self.terminal_tags_ignore
                )

            start_position = accepted_position

    def process_positives_negatives(self, accepted_terminal_tags: fset[type[TransmuterTerminalTag]]) -> fset[type[TransmuterTerminalTag]]:
        positive_terminal_tags = set(accepted_terminal_tags)
        current_positive_terminal_tags = positive_terminal_tags

        while True:
            next_positive_terminal_tags = set()

            for terminal_tag in current_positive_terminal_tags:
                next_positive_terminal_tags |= self.terminal_tags_positives[terminal_tag]

            next_positive_terminal_tags -= positive_terminal_tags

            if not next_positive_terminal_tags:
                break

            positive_terminal_tags |= next_positive_terminal_tags
            current_positive_terminal_tags = next_positive_terminal_tags

        negative_terminal_tags = set()

        for terminal_tag in positive_terminal_tags:
            negative_terminal_tags |= self.terminal_tags_negatives[terminal_tag]

        current_negative_terminal_tags = negative_terminal_tags

        while True:
            next_negative_terminal_tags = set()

            for terminal_tag in current_negative_terminal_tags:
                next_negative_terminal_tags |= self.terminal_tags_negatives[terminal_tag]

            next_negative_terminal_tags -= negative_terminal_tags

            if not next_negative_terminal_tags:
                break

            negative_terminal_tags |= next_negative_terminal_tags
            current_negative_terminal_tags = next_negative_terminal_tags

        return fset(positive_terminal_tags - negative_terminal_tags)

    def nfa(
        self, current_states: dict[type[TransmuterTerminalTag], int], char: str
    ) -> tuple[set[type[TransmuterTerminalTag]], dict[type[TransmuterTerminalTag], int]]:
        current_terminal_tags = set()
        next_states = {}

        for terminal_tag in current_states:
            state_accept, states = terminal_tag.nfa(current_states[terminal_tag], char)

            if state_accept:
                current_terminal_tags.add(terminal_tag)

            if states:
                next_states[terminal_tag] = states

        return (current_terminal_tags, next_states)


class TransmuterLexicalError(TransmuterException):
    def __init__(self, filename: str, position: TransmuterPosition, description: str) -> None:
        super().__init__(filename, position, "Lexical Error", description)


class TransmuterNoTerminalError(TransmuterLexicalError):
    def __init__(self, filename: str, position: TransmuterPosition) -> None:
        super().__init__(filename, position, "Could not match any terminal.")
