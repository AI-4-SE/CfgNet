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

from __future__ import annotations
from typing import List, Set, Any, Optional, Callable
from collections import defaultdict
from cfgnet.network.nodes import Node, ProjectNode


class Network:
    """Datastructure for a configuration network."""

    def __init__(self, project_name: str, root: ProjectNode) -> None:
        self.project_name: str = project_name
        self.root: ProjectNode = root
        self.root.network = self

        self.links: Set = set()

        self.nodes = defaultdict(list)
        self.nodes[self.root.id].append(self.root)

    def find_node(self, node: Node) -> Optional[Node]:
        """
        Find instance of the given node with the same ID.

        :param node: Node to be searched for
        :return: Found node or None if node has not been found
        """

    def get_nodes(self, node_type: Any) -> List[Any]:
        """
        Return nodes from the network according to the entered node type.

        :param node_type: Type of node that should be returned
        :return: List of nodes
        """

    def create_links(self) -> None:
        """Create links between nodes using the available linker."""

    def validate(self, network: Network):
        """Validate a network against a modified version of it."""

    def save_network(self) -> None:
        """Save configuration network of a project into a pickle file."""

    @staticmethod
    def load_network(project_root: str) -> Network:
        """
        Load configuration network of a project from a pickle file.

        :project_root: Project root of the software repository
        :return: Configuration network
        """

    @staticmethod
    def traverse(current: Node, callback: Callable) -> None:
        """
        Traverse the configuration network.

        :param current: Starting point of traversal
        :param callback: Callback called on every visited node
        :return: None
        """

    @staticmethod
    def init_network(project_root: str) -> Network:
        """
        Initialize a configuration network.

        :project_root: Project root of the software repository
        :return: Configuration network
        """
