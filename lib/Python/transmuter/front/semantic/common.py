# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2024  The Transmuter Project
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

from ..lexical import TransmuterTerminalTag, TransmuterTerminal
from ..syntactic import TransmuterNonterminalType, TransmuterEPN, TransmuterBSR


@dataclass
class TransmuterBSRVisitor:
    bsr: TransmuterBSR

    def visit(self) -> bool:
        if self.bsr.start and self.bsr.epns[self.bsr.start]:
            descend_queue = [list(self.bsr.epns[self.bsr.start])]
            ascend_stack = []

            if not self.top_before():
                return True

            while descend_queue:
                epns = descend_queue.pop(0)
                ascend_stack.append(epns)

                for epn in epns:
                    left_children = list(self.bsr.left_children(epn))
                    right_children = list(self.bsr.right_children(epn))

                    if left_children:
                        descend_queue.append(left_children)

                    if right_children:
                        descend_queue.append(right_children)

                if not self.descend(epns):
                    break

            if not self.bottom():
                return True

            while ascend_stack:
                epns = ascend_stack.pop()

                if not self.ascend(epns):
                    break

            return self.top_after()

    def top_before(self) -> bool:
        return True

    def descend(self, epns: list[TransmuterEPN]) -> bool:
        return True

    def bottom(self) -> bool:
        return True

    def ascend(self, epns: list[TransmuterEPN]) -> bool:
        return True

    def top_after(self) -> bool:
        return True

@dataclass
class TransmuterBSRPruner(TransmuterBSRVisitor):
    epns: dict[
        tuple[
            type[TransmuterNonterminalType] | tuple[type[TransmuterTerminalTag | TransmuterNonterminalType], ...],
            TransmuterTerminal | None,
            TransmuterTerminal | None
        ],
        set[TransmuterEPN]
    ] = field(default_factory=dict, init=False, repr=False)

    def descend(self, epns: list[TransmuterEPN]) -> bool:
        self.epns, self.bsr.epns = self.bsr.epns, self.epns

        for epn in epns:
            self.bsr.add(epn)

        self.epns, self.bsr.epns = self.bsr.epns, self.epns
        return True

    def bottom(self) -> bool:
        self.bsr.epns = self.epns
        self.epns = {}
        return False
