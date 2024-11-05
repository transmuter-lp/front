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

from ..lexical import TransmuterTerminalTag, TransmuterTerminal
from ..syntactic import TransmuterNonterminalType, TransmuterEPN, TransmuterBSR


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


@dataclass
class TransmuterTreeNode:
    type_: type[TransmuterTerminalTag | TransmuterNonterminalType]
    start_terminal: TransmuterTerminal | None
    end_terminal: TransmuterTerminal


@dataclass
class TransmuterTerminalTreeNode(TransmuterTreeNode):
    type_: type[TransmuterTerminalTag]


@dataclass
class TransmuterNonterminalTreeNode(TransmuterTreeNode):
    type_: type[TransmuterNonterminalType]
    children: list[TransmuterTreeNode] = field(
        default_factory=list, init=False, repr=False
    )


@dataclass
class TransmuterTreeVisitor:
    tree: TransmuterTreeNode

    def visit(self) -> None:
        descend_queue = [self.tree]
        ascend_stack = []
        self.top_before()

        while descend_queue:
            node = descend_queue.pop(0)
            node_opt = self.descend(node)

            if not node_opt:
                continue

            node = node_opt
            ascend_stack.append(node)

            if isinstance(node, TransmuterNonterminalTreeNode):
                descend_queue.extend(node.children)

        if not self.bottom():
            return

        while ascend_stack:
            node = ascend_stack.pop()
            self.ascend(node)

        self.top_after()

    def top_before(self) -> None:
        pass

    def descend(self, node: TransmuterTreeNode) -> TransmuterTreeNode | None:
        return node

    def bottom(self) -> bool:
        return True

    def ascend(self, node: TransmuterTreeNode) -> None:
        pass

    def top_after(self) -> None:
        pass


@dataclass
class TransmuterTreeTransformer(TransmuterTreeVisitor):
    new_tree: TransmuterTreeNode | None = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.new_tree = self.tree

    def top_before(self) -> None:
        self.new_tree = None

    def apply(self) -> None:
        if self.new_tree:
            self.tree = self.new_tree
