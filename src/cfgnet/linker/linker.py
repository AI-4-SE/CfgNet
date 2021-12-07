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

"""Package for linking nodes."""

import abc
from typing import List, Any, Optional, TYPE_CHECKING
from cfgnet.linker.link import Link
from cfgnet.linker.static_blacklist import StaticBlackList
from cfgnet.network.nodes import ValueNode

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class Linker(abc.ABC):
    """Helper class for establishing links while constructing a network."""

    name: str = ""

    def __init__(self):
        self.network: Optional["Network"] = None
        self.target_nodes: List = None
        self._static_blacklist = StaticBlackList()

    def create_links(self) -> None:
        """
        Call for each linker to create links based on a specific linker criterion.

        :param node: Node that has been added to the network
        :return: None
        """
        self.target_nodes = self._find_target_nodes()

        for node in self.target_nodes:
            self._create_links(node)

    def _create_links(self, node: Any) -> None:
        """Create links using nodes for which the corresponding linker is responsible."""
        # discard empty values
        if not node.name:
            return

        # discard words from static blacklist
        if self.network:
            if self.network.cfg.enable_static_blacklist:
                if node.name in self._static_blacklist.values:
                    return

        # find all matches with the given linker criterion
        matches = self._find_matches(node)

        # add link for all matches
        for match in matches:
            self._add_link(node, match)

    def _add_link(self, node_a: ValueNode, node_b: ValueNode):
        """
        Establish a link between the two given nodes.

        :param node_a: First node to be linked to the second.
        :param node_b: Second node to be linked to the first.
        :return: None
        """
        link = Link(node_a, node_b)
        if self.network:
            self.network.links.add(link)

    @abc.abstractmethod
    def _find_target_nodes(self):
        """Find all nodes for which a linker is_responsible."""

    @abc.abstractmethod
    def _find_matches(self, node):
        """Find all matches for node with a given linker criterion."""
