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

from .common import TransmuterCondition, TransmuterPosition, TransmuterException


class TransmuterTerminalTag:
    STATES_START: set[int]

    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return True

    @staticmethod
    def ignore(conditions: set[type[TransmuterCondition]]) -> bool:
        return False

    @staticmethod
    def positives(conditions: set[type[TransmuterCondition]]) -> set[type["TransmuterTerminalTag"]]:
        return set()

    @staticmethod
    def negatives(conditions: set[type[TransmuterCondition]]) -> set[type["TransmuterTerminalTag"]]:
        return set()


@dataclass(eq=False)
class TransmuterTerminal:
    start_position: TransmuterPosition
    end_position: TransmuterPosition
    tags: set[type[TransmuterTerminalTag]]
    value: str
    next: "TransmuterTerminal | None" = field(default=None, init=False, repr=False)


@dataclass
class TransmuterLexer:
    STATE_ACCEPT: ClassVar[int] = 0
    TERMINAL_TAGS: ClassVar[set[type[TransmuterTerminalTag]]]

    input: str
    filename: str
    conditions: set[type[TransmuterCondition]]
    terminal_tags_ignore: set[type[TransmuterTerminalTag]] = field(init=False, repr=False)
    accepted_terminal_tags: dict[frozenset[type[TransmuterTerminalTag]], set[type[TransmuterTerminalTag]]] = field(
        default_factory=dict,
        init=False,
        repr=False
    )
    states_start: set[int] = field(init=False, repr=False)
    start: TransmuterTerminal | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.terminal_tags_ignore = {terminal_tag for terminal_tag in self.TERMINAL_TAGS if terminal_tag.ignore(self.conditions)}
        self.states_start = set()

        for terminal_tag in self.TERMINAL_TAGS:
            if terminal_tag.start(self.conditions):
                self.states_start |= terminal_tag.STATES_START

    def next_terminal(self, current_terminal: TransmuterTerminal | None) -> TransmuterTerminal | None:
        if current_terminal is None:
            if self.start is None:
                self.start = self.get_terminal(TransmuterPosition(0, 1, 1))

            return self.start

        if current_terminal.next is None:
            current_terminal.next = self.get_terminal(current_terminal.end_position)

        return current_terminal.next

    def get_terminal(self, start_position: TransmuterPosition) -> TransmuterTerminal | None:
        while True:
            accepted_terminal_tags = set()
            accepted_position = start_position
            current_terminal_tags = set()
            current_position = start_position
            current_states = self.states_start

            while current_states:
                if self.STATE_ACCEPT in current_states:
                    accepted_terminal_tags = current_terminal_tags
                    accepted_position = current_position

                if current_position.index_ == len(self.input):
                    if accepted_terminal_tags - self.terminal_tags_ignore:
                        break

                    return None

                current_terminal_tags, current_states = self.nfa(self.input[current_position.index_], current_states)
                current_position = TransmuterPosition(
                    current_position.index_ + 1,
                    current_position.line + (0 if self.input[current_position.index_] != "\n" else 1),
                    current_position.column + 1 if self.input[current_position.index_] != "\n" else 1
                )

            if not accepted_terminal_tags:
                raise TransmuterNoTerminalError(self.filename, start_position)

            initial_accepted_terminal_tags = frozenset(accepted_terminal_tags)

            if initial_accepted_terminal_tags not in self.accepted_terminal_tags:
                self.process_positives_negatives(accepted_terminal_tags)
                self.accepted_terminal_tags[initial_accepted_terminal_tags] = accepted_terminal_tags
            else:
                accepted_terminal_tags = self.accepted_terminal_tags[initial_accepted_terminal_tags]

            if accepted_terminal_tags - self.terminal_tags_ignore:
                return TransmuterTerminal(
                    start_position,
                    accepted_position,
                    accepted_terminal_tags - self.terminal_tags_ignore,
                    self.input[start_position.index_:accepted_position.index_]
                )

            start_position = accepted_position

    def process_positives_negatives(self, accepted_terminal_tags: set[type[TransmuterTerminalTag]]) -> None:
        current_accepted_terminal_tags = accepted_terminal_tags

        while True:
            next_accepted_terminal_tags = set()

            for terminal_tag in current_accepted_terminal_tags:
                next_accepted_terminal_tags |= {tag for tag in terminal_tag.positives(self.conditions) if tag.start(self.conditions)}

            next_accepted_terminal_tags -= accepted_terminal_tags

            if len(next_accepted_terminal_tags) == 0:
                break

            accepted_terminal_tags |= next_accepted_terminal_tags
            current_accepted_terminal_tags = next_accepted_terminal_tags

        negative_terminal_tags = set()

        for terminal_tag in accepted_terminal_tags:
            negative_terminal_tags |= {tag for tag in terminal_tag.negatives(self.conditions) if tag.start(self.conditions)}

        current_negative_terminal_tags = negative_terminal_tags

        while True:
            next_negative_terminal_tags = set()

            for terminal_tag in current_negative_terminal_tags:
                next_negative_terminal_tags |= {tag for tag in terminal_tag.negatives(self.conditions) if tag.start(self.conditions)}

            next_negative_terminal_tags -= negative_terminal_tags

            if len(next_negative_terminal_tags) == 0:
                break

            negative_terminal_tags |= next_negative_terminal_tags
            current_negative_terminal_tags = next_negative_terminal_tags

        accepted_terminal_tags -= negative_terminal_tags

    def nfa(self, char: str, current_states: set[int]) -> tuple[set[type[TransmuterTerminalTag]], set[int]]:
        raise NotImplementedError()


class TransmuterLexicalError(TransmuterException):
    def __init__(self, filename: str, position: TransmuterPosition, description: str) -> None:
        super().__init__(filename, position, "Lexical Error", description)


class TransmuterNoTerminalError(TransmuterLexicalError):
    def __init__(self, filename: str, position: TransmuterPosition) -> None:
        super().__init__(filename, position, "Could not match any terminal.")
