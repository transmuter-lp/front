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
from ..syntactic import (
    TransmuterNonterminalType,
    TransmuterEPN,
    TransmuterParsingState,
    TransmuterBSR,
)


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

    def __repr__(self) -> str:
        return repr((self.type_, self.start_terminal, self.end_terminal))


@dataclass
class TransmuterNonterminalTreeNode(TransmuterTreeNode):
    type_: type[TransmuterNonterminalType]
    children: list[TransmuterTreeNode] = field(
        default_factory=list, init=False, repr=False
    )

    def __repr__(self) -> str:
        return repr(
            (self.type_, self.start_terminal, self.end_terminal, self.children)
        )


@dataclass
class TransmuterBSRTreeGenerator(TransmuterBSRVisitor):
    tree: TransmuterNonterminalTreeNode | None = field(
        default=None, init=False, repr=False
    )
    parents: list[TransmuterNonterminalTreeNode] = field(
        default_factory=list, init=False, repr=False
    )

    def top_before(self) -> None:
        self.tree = None
        self.parents = []

    def descend(self, epns: list[TransmuterEPN]) -> list[TransmuterEPN]:
        parent = self.parents.pop(0) if self.parents else None
        assert epns[0].state.end_terminal

        if epns[0].type_:
            node = TransmuterNonterminalTreeNode(
                epns[0].type_,
                epns[0].state.start_terminal,
                epns[0].state.end_terminal,
            )

            if parent:
                if parent.children and (
                    not parent.children[0].start_terminal
                    or node.start_terminal
                    and parent.children[0].start_terminal.start_position.index_
                    < node.start_terminal.start_position.index_
                ):
                    parent.children.insert(1, node)
                else:
                    parent.children.insert(0, node)
            else:
                self.tree = node

            parent = node

        assert parent

        if self.bsr.left_children(epns[0]):
            self.parents.append(parent)

        if self.bsr.right_children(epns[0]):
            self.parents.append(parent)
        elif epns[0].state.split_terminal != epns[0].state.end_terminal:
            assert issubclass(epns[0].state.string[-1], TransmuterTerminalTag)
            parent.children.insert(
                0,
                TransmuterTerminalTreeNode(
                    epns[0].state.string[-1],
                    epns[0].state.split_terminal,
                    epns[0].state.end_terminal,
                ),
            )

        return epns

    def bottom(self) -> bool:
        return False


@dataclass
class TransmuterTreeVisitor:
    tree: TransmuterNonterminalTreeNode

    def visit(self) -> None:
        descend_queue: list[TransmuterTreeNode] = [self.tree]
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
    new_tree: TransmuterNonterminalTreeNode | None = field(
        init=False, repr=False
    )

    def __post_init__(self) -> None:
        self.new_tree = self.tree

    def top_before(self) -> None:
        self.new_tree = None

    def apply(self) -> None:
        if self.new_tree:
            self.tree = self.new_tree


@dataclass
class TransmuterTreeBSRGenerator(TransmuterTreeVisitor):
    bsr: TransmuterBSR = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.bsr = TransmuterBSR()

    def top_before(self) -> None:
        if self.bsr.start or self.bsr.epns:
            self.bsr = TransmuterBSR()

        self.bsr.start = (self.tree.type_, None, self.tree.end_terminal)

    def descend(self, node: TransmuterTreeNode) -> TransmuterTreeNode | None:
        if isinstance(node, TransmuterNonterminalTreeNode):
            string = tuple(child.type_ for child in node.children)
            epn = TransmuterEPN(
                node.type_,
                TransmuterParsingState(
                    string,
                    node.start_terminal,
                    (
                        node.children[-1].start_terminal
                        if node.children
                        else node.start_terminal
                    ),
                    node.end_terminal,
                ),
            )
            self.bsr.add(epn)

            for i in range(len(node.children) - 1):
                epn = TransmuterEPN(
                    None,
                    TransmuterParsingState(
                        string[: i + 1],
                        node.start_terminal,
                        node.children[i].start_terminal,
                        node.children[i].end_terminal,
                    ),
                )
                self.bsr.add(epn)

        return node

    def bottom(self) -> bool:
        return False
