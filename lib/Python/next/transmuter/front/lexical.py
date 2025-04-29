# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2021, 2023, 2024  Natan Junges <natanajunges@gmail.com>
# Copyright (C) 2024, 2025  The Transmuter Project
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

from dataclasses import dataclass, field
from typing import ClassVar

from .common import (
    TransmuterConditions,
    TransmuterMeta,
    TransmuterPosition,
    TransmuterException,
)

TransmuterLexingState = int


class TransmuterTerminalTag(metaclass=TransmuterMeta):
    STATES_START: TransmuterLexingState = 1

    @staticmethod
    def start(conditions: TransmuterConditions) -> bool:
        return True

    @staticmethod
    def ignore(conditions: TransmuterConditions) -> bool:
        return False

    @staticmethod
    def positives(
        conditions: TransmuterConditions,
    ) -> set[type["TransmuterTerminalTag"]]:
        return set()

    @staticmethod
    def negatives(
        conditions: TransmuterConditions,
    ) -> set[type["TransmuterTerminalTag"]]:
        return set()

    @staticmethod
    def nfa(
        current_states: TransmuterLexingState, char: str
    ) -> tuple[bool, TransmuterLexingState]:
        raise NotImplementedError()


@dataclass(eq=False)
class TransmuterTerminal:
    tags: set[type[TransmuterTerminalTag]]
    value: str
    start_position: TransmuterPosition
    end_position: TransmuterPosition
    next: "TransmuterTerminal | None" = field(default=None, init=False)

    def __repr__(self) -> str:
        return repr(
            (self.tags, self.value, self.start_position, self.end_position)
        )


@dataclass
class _TransmuterLexerCache:
    states_start: dict[type[TransmuterTerminalTag], TransmuterLexingState] = (
        field(default_factory=dict, init=False, repr=False)
    )
    terminal_tags_ignore: set[type[TransmuterTerminalTag]] = field(
        default_factory=set, init=False, repr=False
    )
    terminal_tags_positives: dict[
        type[TransmuterTerminalTag], set[type[TransmuterTerminalTag]]
    ] = field(default_factory=dict, init=False, repr=False)
    terminal_tags_negatives: dict[
        type[TransmuterTerminalTag], set[type[TransmuterTerminalTag]]
    ] = field(default_factory=dict, init=False, repr=False)
    accepted_terminal_tags: dict[
        frozenset[type[TransmuterTerminalTag]],
        set[type[TransmuterTerminalTag]],
    ] = field(default_factory=dict, init=False, repr=False)
    nfas: dict[
        tuple[type[TransmuterTerminalTag], TransmuterLexingState, str],
        tuple[bool, TransmuterLexingState],
    ] = field(default_factory=dict, init=False, repr=False)


@dataclass
class _TransmuterLexerStore:
    current_position: TransmuterPosition = field(init=False, repr=False)
    current_states: dict[
        type[TransmuterTerminalTag], TransmuterLexingState
    ] = field(default_factory=dict, init=False, repr=False)
    current_positive_terminal_tags: set[type[TransmuterTerminalTag]] = field(
        default_factory=set, init=False, repr=False
    )
    current_negative_terminal_tags: set[type[TransmuterTerminalTag]] = field(
        default_factory=set, init=False, repr=False
    )
    next_states: dict[type[TransmuterTerminalTag], TransmuterLexingState] = (
        field(default_factory=dict, init=False, repr=False)
    )
    next_terminal_tags: set[type[TransmuterTerminalTag]] = field(
        default_factory=set, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self.current_position = TransmuterPosition("", 0, 1, 1)


@dataclass
class TransmuterLexer:
    TERMINAL_TAGS: ClassVar[list[type[TransmuterTerminalTag]]]

    filename: str
    input: str
    conditions: TransmuterConditions
    start_position: TransmuterPosition = field(init=False, repr=False)
    _start: TransmuterTerminal | None = field(
        default=None, init=False, repr=False
    )
    _cache: _TransmuterLexerCache = field(
        default_factory=_TransmuterLexerCache, init=False, repr=False
    )
    _store: _TransmuterLexerStore = field(
        default_factory=_TransmuterLexerStore, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self.start_position = TransmuterPosition(self.filename, 0, 1, 1)

        for terminal_tag in self.TERMINAL_TAGS:
            if terminal_tag.start(self.conditions):
                self._cache.states_start[terminal_tag] = (
                    terminal_tag.STATES_START
                )

                if terminal_tag.ignore(self.conditions):
                    self._cache.terminal_tags_ignore.add(terminal_tag)

                self._cache.terminal_tags_positives[terminal_tag] = {
                    tag
                    for tag in terminal_tag.positives(self.conditions)
                    if tag.start(self.conditions)
                }
                self._cache.terminal_tags_negatives[terminal_tag] = {
                    tag
                    for tag in terminal_tag.negatives(self.conditions)
                    if tag.start(self.conditions)
                }

    def next_terminal(
        self, current_terminal: TransmuterTerminal | None
    ) -> TransmuterTerminal | None:
        if current_terminal is None:
            if self._start is None:
                self._start = self._get_terminal(self.start_position)

                if self._start is None:
                    return None

                # Since in _get_terminal the start position object is
                # copied instead of being used directly, we need to
                # update the original one
                self.start_position.update(self._start.start_position)
                self._start.start_position = self.start_position

            return self._start

        if current_terminal.next is None:
            current_terminal.next = self._get_terminal(
                current_terminal.end_position
            )

        return current_terminal.next

    def _get_terminal(
        self, start_position: TransmuterPosition
    ) -> TransmuterTerminal | None:
        if start_position.index_ == len(self.input):
            return None

        start_position = start_position.copy()
        self._store.current_position.update(start_position)
        self._store.current_states.clear()
        self._store.current_states.update(self._cache.states_start)
        accepted_position = start_position.copy()
        accepted_terminal_tags: set[type[TransmuterTerminalTag]] = set()

        while True:
            while len(
                self._store.current_states
            ) > 0 and self._store.current_position.index_ < len(self.input):
                char = self.input[self._store.current_position.index_]
                self._process_nfas(char)
                self._store.current_position.index_ += 1

                if char != "\n":
                    self._store.current_position.column += 1
                else:
                    self._store.current_position.line += 1
                    self._store.current_position.column = 1

                if len(self._store.next_terminal_tags) > 0:
                    accepted_terminal_tags, self._store.next_terminal_tags = (
                        self._store.next_terminal_tags,
                        accepted_terminal_tags,
                    )
                    # next_terminal_tags is always empty after use
                    self._store.next_terminal_tags.clear()
                    accepted_position.update(self._store.current_position)

                self._store.current_states, self._store.next_states = (
                    self._store.next_states,
                    self._store.current_states,
                )
                # next_states is always empty after use
                self._store.next_states.clear()

            if len(accepted_terminal_tags) == 0:
                raise TransmuterNoTerminalError(start_position)

            initial_accepted_terminal_tags = frozenset(accepted_terminal_tags)

            if (
                initial_accepted_terminal_tags
                not in self._cache.accepted_terminal_tags
            ):
                self._process_positives_negatives(accepted_terminal_tags)
                accepted_terminal_tags -= self._cache.terminal_tags_ignore
                self._cache.accepted_terminal_tags[
                    initial_accepted_terminal_tags
                ] = accepted_terminal_tags.copy()
            else:
                accepted_terminal_tags.clear()
                accepted_terminal_tags.update(
                    self._cache.accepted_terminal_tags[
                        initial_accepted_terminal_tags
                    ]
                )

            if len(accepted_terminal_tags) > 0:
                return TransmuterTerminal(
                    accepted_terminal_tags,
                    self.input[
                        start_position.index_ : accepted_position.index_
                    ],
                    start_position,
                    accepted_position,
                )

            if self._store.current_position.index_ == len(self.input):
                return None

            # Skip ignored terminal and restart
            start_position.update(accepted_position)
            self._store.current_position.update(accepted_position)
            assert len(self._store.current_states) == 0
            self._store.current_states.update(self._cache.states_start)

    def _process_nfas(self, char: str) -> None:
        for terminal_tag, current_states in self._store.current_states.items():
            if (terminal_tag, current_states, char) not in self._cache.nfas:
                state_accept, states = terminal_tag.nfa(current_states, char)
                self._cache.nfas[terminal_tag, current_states, char] = (
                    state_accept,
                    states,
                )
            else:
                state_accept, states = self._cache.nfas[
                    terminal_tag, current_states, char
                ]

            if state_accept:
                self._store.next_terminal_tags.add(terminal_tag)

            if states != 0:
                self._store.next_states[terminal_tag] = states

    def _process_positives_negatives(
        self, positive_terminal_tags: set[type[TransmuterTerminalTag]]
    ) -> None:
        self._store.current_positive_terminal_tags.clear()
        self._store.current_positive_terminal_tags.update(
            positive_terminal_tags
        )

        while True:
            for terminal_tag in self._store.current_positive_terminal_tags:
                self._store.next_terminal_tags |= (
                    self._cache.terminal_tags_positives[terminal_tag]
                )

            self._store.next_terminal_tags -= positive_terminal_tags

            if len(self._store.next_terminal_tags) == 0:
                # next_terminal_tags is always empty after use
                break

            positive_terminal_tags |= self._store.next_terminal_tags
            (
                self._store.current_positive_terminal_tags,
                self._store.next_terminal_tags,
            ) = (
                self._store.next_terminal_tags,
                self._store.current_positive_terminal_tags,
            )
            self._store.next_terminal_tags.clear()

        # Reuse set for efficiency
        negative_terminal_tags = self._store.current_positive_terminal_tags
        negative_terminal_tags.clear()

        for terminal_tag in positive_terminal_tags:
            negative_terminal_tags |= self._cache.terminal_tags_negatives[
                terminal_tag
            ]

        self._store.current_negative_terminal_tags.clear()
        self._store.current_negative_terminal_tags.update(
            negative_terminal_tags
        )

        while True:
            for terminal_tag in self._store.current_negative_terminal_tags:
                self._store.next_terminal_tags |= (
                    self._cache.terminal_tags_negatives[terminal_tag]
                )

            self._store.next_terminal_tags -= negative_terminal_tags

            if len(self._store.next_terminal_tags) == 0:
                # next_terminal_tags is always empty after use
                break

            negative_terminal_tags |= self._store.next_terminal_tags
            (
                self._store.current_negative_terminal_tags,
                self._store.next_terminal_tags,
            ) = (
                self._store.next_terminal_tags,
                self._store.current_negative_terminal_tags,
            )
            self._store.next_terminal_tags.clear()

        positive_terminal_tags -= negative_terminal_tags


class TransmuterLexicalError(TransmuterException):
    def __init__(self, position: TransmuterPosition, description: str) -> None:
        super().__init__(position, "Lexical Error", description)


class TransmuterNoTerminalError(TransmuterLexicalError):
    def __init__(self, position: TransmuterPosition) -> None:
        super().__init__(position, "Could not match any terminal.")
