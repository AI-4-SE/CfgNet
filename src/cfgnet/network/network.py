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

import os
import logging

from typing import List, Set, Any, Optional, Callable
from collections import defaultdict
from cfgnet.vcs.git import Git
from cfgnet.plugins.plugin_manager import PluginManager
from cfgnet.linker.linker_manager import LinkerManager
from cfgnet.network.nodes import Node, ProjectNode, OptionNode
from cfgnet.network.network_configuration import NetworkConfiguration


class Network:
    """Datastructure for a configuration network."""

    def __init__(
        self, project_name: str, root: ProjectNode, cfg: NetworkConfiguration
    ) -> None:
        self.cfg = cfg

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
        if node.id not in self.nodes:
            return None

        if node.id in self.nodes:
            if len(self.nodes[node.id]) == 1:
                return self.nodes[node.id][0]
            if isinstance(node, OptionNode):
                # multiple option nodes can have the same ID
                # here we can also use other techniques to find the right option
                return self._find_option(node, self.nodes[node.id])

        return None

    @staticmethod
    def _find_option(node: OptionNode, options: List) -> Optional[OptionNode]:
        """
        Try to find the correct option node in a list of option nodes where all have the same ID.

        :param node: node to be searched
        :param options: list of option nodes with the same ID
        :return: Found option node or None
        """
        child = node.children[0]
        for option in options:
            if child in option.children:
                return option

        return None

    def get_nodes(self, node_type: Any) -> List[Any]:
        """
        Return nodes from the network according to the entered node type.

        :param node_type: Type of node that should be returned
        :return: List of nodes
        """
        return [
            node
            for nodes in self.nodes.values()
            for node in nodes
            if isinstance(node, node_type)
        ]

    def create_links(self) -> None:
        """Create links between nodes using the available linker."""

    # (TODO remove when implmeneted) pylint: disable=no-self-use
    def validate(self):
        """Validate a network against the current state of the project dir."""
        conflicts: List[Any] = []  # TODO Change `Any` to `Conflict`
        return conflicts

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
    def init_network(cfg: NetworkConfiguration) -> Network:
        """
        Initialize a configuration network.

        :project_root: Project root of the software repository
        :return: Configuration network
        """
        repo = Git(project_root=cfg.project_root_abs)
        tracked_files = set(repo.get_tracked_files())

        # TODO: Filter files using the ignore file

        project_name = os.path.basename(cfg.project_root_abs)
        root = ProjectNode(name=project_name, root_dir=cfg.project_root_abs)
        network = Network(project_name=project_name, root=root, cfg=cfg)

        for file in tracked_files:
            abs_file_path = os.path.join(cfg.project_root_abs, file)
            plugin = PluginManager.get_responsible_plugin(abs_file_path)

            if plugin:
                try:
                    plugin.parse_file(
                        abs_file_path=abs_file_path,
                        rel_file_path=file,
                        root=root,
                    )
                except UnicodeDecodeError as error:
                    logging.warning(
                        "%s: %s (%s)",
                        plugin.__class__.__name__,
                        error.reason,
                        file,
                    )

        LinkerManager.apply_linkers(network)

        return network
