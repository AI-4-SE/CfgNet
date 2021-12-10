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
from typing import List

from cfgnet.network.nodes import ValueNode
from cfgnet.linker.linker import Linker


class EqualityLinker(Linker):
    """Equality-based Linker."""

    def create_links(self) -> None:
        self.target_nodes = self._find_target_nodes()

        for node in self.target_nodes:
            if not node.name:
                return

            # discard words from static blacklist
            if self.network:
                if self.network.cfg.enable_static_blacklist:
                    if node.name in self.static_blacklist.values:
                        return

            # find all matches with the given linker criterion
            matches = self._find_matches(node)

            # add link for all matches
            for match in matches:
                self._add_link(node, match)

    def _find_target_nodes(self):
        return [
            node
            for node in self.network.get_nodes(ValueNode)
            if node.type != bool
        ]

    def _find_matches(self, node: ValueNode) -> List[ValueNode]:

        target_nodes = self._filter_target_nodes(node)

        return [
            value_node
            for value_node in target_nodes
            if value_node.name == node.name and node is not value_node
        ]

    def _filter_target_nodes(self, node) -> List[ValueNode]:
        """Filter target nodes to avoid links within the same maven file."""
        artifact_name = node.id.split("::::")[1]

        if "pom.xml" in artifact_name:
            return list(
                filter(
                    lambda node: artifact_name not in node.id.split("::::")[1],
                    self.target_nodes,
                )
            )

        return self.target_nodes
