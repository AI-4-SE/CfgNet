# This file is part of the CfgNet module.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import List, Any, Tuple, Optional
from cfgnet.network.nodes import Node, ArtifactNode, OptionNode, ValueNode


class Link:
    """Datastructure for network links between Value or artifact nodes."""

    node_a: ValueNode
    artifact_a: ArtifactNode
    option_stack_a: List[OptionNode]

    node_b: ValueNode
    artifact_b: ArtifactNode
    option_stack_b: List[OptionNode]

    def __init__(self, node_a: ValueNode, node_b: ValueNode):
        if node_b.id < node_a.id:
            node_a, node_b = node_b, node_a

        self.node_a = node_a
        (
            self.artifact_a,
            self.option_stack_a,
        ) = self._determine_components(node_a)

        self.node_b = node_b
        (
            self.artifact_b,
            self.option_stack_b,
        ) = self._determine_components(node_b)

    @staticmethod
    def _determine_components(
        node: Node,
    ) -> Tuple[ArtifactNode, List[OptionNode]]:
        """
        Backtrace parent node information.

        :param node: Node to collect information about
        :return: Concept node, artifact node, option node stack
        """
        artifact: Optional[ArtifactNode] = None
        option_stack: List[OptionNode] = []

        current: Any = node
        while True:
            if isinstance(current, OptionNode):
                option_stack.insert(0, current)
            elif isinstance(current, ArtifactNode):
                artifact = current
                break

            current = current.parent

        return artifact, option_stack

    def is_node_involved(self, node: Node) -> bool:
        """
        Check if a node is involved in a link.

        :param node: node that should be involved in a link
        :return: true if node is involved in a link, else false
        """
        return node in (self.node_a, self.node_b)

    def __hash__(self):
        obj_hash = hash("|".join([self.node_a.id, self.node_b.id]))
        return obj_hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        return f"{self.node_a} <-> {self.node_b}"
