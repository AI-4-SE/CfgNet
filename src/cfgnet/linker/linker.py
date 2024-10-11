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
from typing import List, Optional, TYPE_CHECKING
from cfgnet.linker.link import Link
from cfgnet.linker.static_blacklist import StaticBlackList
from cfgnet.network.nodes import ValueNode
from cfgnet.config_types.config_type_inferer import ConfigTypeInferer

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class Linker(abc.ABC):
    """Helper class for establishing links while constructing a network."""

    name: str = ""

    def __init__(self):
        self.network: Optional["Network"] = None
        self.enable_internal_links: Optional[bool] = None
        self.target_nodes: List = None
        self.static_blacklist = StaticBlackList()
        self.inferer = ConfigTypeInferer()

    @abc.abstractmethod
    def create_links(self) -> None:
        """Call for each linker to create links based on a specific linker criterion."""

    @abc.abstractmethod
    def _find_target_nodes(self):
        """Find all nodes for which a linker is_responsible."""

    @abc.abstractmethod
    def _find_matches(self, node):
        """Find all matches for node with a given linker criterion."""

    @abc.abstractmethod
    def _check_config_types(
        self, node_a: ValueNode, node_b: ValueNode
    ) -> bool:
        """
        Check config types of given nodes before creating a link.

        :param node_a: First node to be linked to the second
        :param node_b: Second node to be linked to the first
        :return: True if config types meet specific condition else False
        """

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
