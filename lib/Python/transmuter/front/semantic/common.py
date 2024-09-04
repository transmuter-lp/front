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

from ..syntactic import TransmuterEPN, TransmuterBSR


@dataclass
class TransmuterBSRVisitor:
    bsr: TransmuterBSR

    def visit(self) -> bool:
        if not self.bsr.start or not self.bsr.epns[self.bsr.start]:
            return True

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
class TransmuterBSRTransformer(TransmuterBSRVisitor):
    new_bsr: TransmuterBSR = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.new_bsr = self.bsr

    def top_before(self) -> bool:
        self.new_bsr = TransmuterBSR()
        self.new_bsr.start = self.bsr.start
        return True


class TransmuterBSRPruner(TransmuterBSRTransformer):
    def descend(self, epns: list[TransmuterEPN]) -> bool:
        for epn in epns:
            self.new_bsr.add(epn)

        return True

    def bottom(self) -> bool:
        return False
