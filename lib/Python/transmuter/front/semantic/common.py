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

from dataclasses import dataclass, field

from ..syntactic import TransmuterEPN, TransmuterBSR


@dataclass
class TransmuterBSRVisitor:
    bsr: TransmuterBSR

    def visit(self) -> None:
        if not self.bsr.start or not self.bsr.epns[self.bsr.start]:
            return

        descend_queue = [list(self.bsr.epns[self.bsr.start])]
        ascend_stack = []
        self.top_before()

        while descend_queue:
            epns = descend_queue.pop(0)
            epns = self.descend(epns)

            if not epns:
                continue

            ascend_stack.append(epns)

            for epn in epns:
                left_children = list(self.bsr.left_children(epn))
                right_children = list(self.bsr.right_children(epn))

                if left_children:
                    descend_queue.append(left_children)

                if right_children:
                    descend_queue.append(right_children)

        if not self.bottom():
            return

        while ascend_stack:
            epns = ascend_stack.pop()
            self.ascend(epns)

        self.top_after()

    def top_before(self) -> None:
        pass

    def descend(self, epns: list[TransmuterEPN]) -> list[TransmuterEPN]:
        return epns

    def bottom(self) -> bool:
        return True

    def ascend(self, epns: list[TransmuterEPN]) -> None:
        pass

    def top_after(self) -> None:
        pass


@dataclass
class TransmuterBSRTransformer(TransmuterBSRVisitor):
    new_bsr: TransmuterBSR = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.new_bsr = self.bsr

    def top_before(self) -> None:
        self.new_bsr = TransmuterBSR()
        self.new_bsr.start = self.bsr.start

    def apply(self) -> None:
        self.bsr.epns = self.new_bsr.epns
        self.bsr.start = self.new_bsr.start
        self.new_bsr = self.bsr


class TransmuterBSRPruner(TransmuterBSRTransformer):
    def descend(self, epns: list[TransmuterEPN]) -> list[TransmuterEPN]:
        for epn in epns:
            self.new_bsr.add(epn)

        return epns

    def bottom(self) -> bool:
        return False


class TransmuterBSRDisambiguator(TransmuterBSRTransformer):
    def descend(self, epns: list[TransmuterEPN]) -> list[TransmuterEPN]:
        epn = self.disambiguate(epns) if len(epns) > 1 else epns[0]
        self.new_bsr.add(epn)
        return [epn]

    def bottom(self) -> bool:
        return False

    def disambiguate(self, epns: list[TransmuterEPN]) -> TransmuterEPN:
        raise NotImplementedError()
