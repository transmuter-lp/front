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

from .common import TransmuterConditions, TransmuterMeta, TransmuterPosition, TransmuterException


class TransmuterTerminalTag(metaclass=TransmuterMeta):
    # S0
    STATES_START: "TransmuterLexingState" = 1

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
    def nfa(current_states: "TransmuterLexingState", char: str) -> tuple[bool, "TransmuterLexingState"]:
        raise NotImplementedError()


@dataclass(eq=False)
class TransmuterTerminal:
    start_position: TransmuterPosition
    end_position: TransmuterPosition
    value: str
    tags: set[type[TransmuterTerminalTag]]
    next: "TransmuterTerminal | None" = field(default=None, init=False, repr=False)

    def __repr__(self) -> str:
        return repr((self.start_position, self.end_position, self.value, self.tags))


TransmuterLexingState = int


@dataclass
class TransmuterLexer:
    TERMINAL_TAGS: ClassVar[set[type[TransmuterTerminalTag]]]

    input: str
    filename: str
    conditions: TransmuterConditions
    terminal_tags_ignore: set[type[TransmuterTerminalTag]] = field(init=False, repr=False)
    states_start: dict[type[TransmuterTerminalTag], "TransmuterLexingState"] = field(init=False, repr=False)
    terminal_tags_positives: dict[type[TransmuterTerminalTag], set[type[TransmuterTerminalTag]]] = field(init=False, repr=False)
    terminal_tags_negatives: dict[type[TransmuterTerminalTag], set[type[TransmuterTerminalTag]]] = field(init=False, repr=False)
    start: TransmuterTerminal | None = field(default=None, init=False, repr=False)
    accepted_terminal_tags: dict[frozenset[type[TransmuterTerminalTag]], set[type[TransmuterTerminalTag]]] = field(
        default_factory=dict,
        init=False,
        repr=False
    )

    def __post_init__(self) -> None:
        self.terminal_tags_ignore = set()
        self.states_start = {}
        self.terminal_tags_positives = {}
        self.terminal_tags_negatives = {}

        for terminal_tag in self.TERMINAL_TAGS:
            if terminal_tag.start(self.conditions):
                if terminal_tag.ignore(self.conditions):
                    self.terminal_tags_ignore.add(terminal_tag)

                self.states_start[terminal_tag] = terminal_tag.STATES_START
                self.terminal_tags_positives[terminal_tag] = {tag for tag in terminal_tag.positives(self.conditions) if tag.start(self.conditions)}
                self.terminal_tags_negatives[terminal_tag] = {tag for tag in terminal_tag.negatives(self.conditions) if tag.start(self.conditions)}

    def next_terminal(self, current_terminal: TransmuterTerminal | None) -> TransmuterTerminal | None:
        if not current_terminal:
            if not self.start:
                self.start = self.get_terminal(TransmuterPosition(0, 1, 1))

            return self.start

        if not current_terminal.next:
            current_terminal.next = self.get_terminal(current_terminal.end_position)

        return current_terminal.next

    def get_terminal(self, start_position: TransmuterPosition) -> TransmuterTerminal | None:
        if start_position.index_ == len(self.input):
            return None

        while True:
            current_terminal_tags = set()
            current_position = start_position.copy()
            current_states = self.states_start
            accepted_terminal_tags = current_terminal_tags
            accepted_position = current_position

            while current_states and current_position.index_ < len(self.input):
                char = self.input[current_position.index_]
                current_terminal_tags = set()
                next_states = {}

                for terminal_tag in current_states:
                    state_accept, states = terminal_tag.nfa(current_states[terminal_tag], char)

                    if state_accept:
                        current_terminal_tags.add(terminal_tag)

                    if states:
                        next_states[terminal_tag] = states

                current_states = next_states

                if char != "\n":
                    current_position.column += 1
                else:
                    current_position.line += 1
                    current_position.column = 1

                current_position.index_ += 1

                if current_terminal_tags:
                    accepted_terminal_tags = current_terminal_tags
                    accepted_position = current_position.copy()

            if not accepted_terminal_tags:
                raise TransmuterNoTerminalError(self.filename, start_position)

            initial_accepted_terminal_tags = frozenset(accepted_terminal_tags)

            if initial_accepted_terminal_tags not in self.accepted_terminal_tags:
                self.process_positives_negatives(accepted_terminal_tags)
                accepted_terminal_tags -= self.terminal_tags_ignore
                self.accepted_terminal_tags[initial_accepted_terminal_tags] = accepted_terminal_tags
            else:
                accepted_terminal_tags = self.accepted_terminal_tags[initial_accepted_terminal_tags]

            if accepted_terminal_tags:
                return TransmuterTerminal(
                    start_position,
                    accepted_position,
                    self.input[start_position.index_:accepted_position.index_],
                    accepted_terminal_tags
                )

            if current_position.index_ == len(self.input):
                return None

            start_position = accepted_position

    def process_positives_negatives(self, accepted_terminal_tags: set[type[TransmuterTerminalTag]]) -> None:
        positive_terminal_tags = accepted_terminal_tags
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

        positive_terminal_tags -= negative_terminal_tags


class TransmuterLexicalError(TransmuterException):
    def __init__(self, filename: str, position: TransmuterPosition, description: str) -> None:
        super().__init__(filename, position, "Lexical Error", description)


class TransmuterNoTerminalError(TransmuterLexicalError):
    def __init__(self, filename: str, position: TransmuterPosition) -> None:
        super().__init__(filename, position, "Could not match any terminal.")
