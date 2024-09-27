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
import sys
import logging
import hashlib
import pickle

from typing import List, Set, Any, Optional, Callable, Tuple, Dict
from collections import defaultdict
from cfgnet.vcs.git import Git
from cfgnet.plugins.plugin_manager import PluginManager
from cfgnet.linker.linker_manager import LinkerManager
from cfgnet.conflicts.conflict_detector import ConflictDetector
from cfgnet.network.ignorefile import IgnoreFile
from cfgnet.network.nodes import (
    Node,
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.exporter.exporter import DotExporter, JSONExporter
from cfgnet.utility.util import is_test_file, get_system_files


class Network:
    """Datastructure for a configuration network."""

    def __init__(
        self, project_name: str, root: ProjectNode, cfg: NetworkConfiguration
    ) -> None:
        self.cfg = cfg

        self.project_name: str = project_name
        self.root: ProjectNode = root
        self.root.network = self
        self.project_root: str = root.root_dir

        self.links: Set = set()

        self.nodes = defaultdict(list)
        self.nodes[self.root.id].append(self.root)

        if not os.path.isdir(self.cfg.data_dir_path()):
            os.makedirs(self.cfg.data_dir_path())

        IgnoreFile.configure(cfg.ignorefile_path())

    def find_artifact_node(self, node: Node) -> Optional[ArtifactNode]:
        """
        Find instance of the given node with the same ID.

        :param node: artifact node to be searched for
        :return: Found artifact node or None if node has not been found
        """
        return self._find_node(node, ArtifactNode)

    def find_option_node(self, node: Node) -> Optional[OptionNode]:
        """
        Find instance of the given node with the same ID.

        :param node: option node to be searched for
        :return: Found option node or None if node has not been found
        """
        return self._find_node(node, OptionNode)

    def find_value_node(self, node: Node) -> Optional[ValueNode]:
        """
        Find instance of the given node with the same ID.

        :param node: value node to be searched for
        :return: Found value node or None if node has not been found
        """
        return self._find_node(node, ValueNode)

    # pylint: disable=too-many-return-statements
    def _find_node(self, node: Node, node_type: Any = None) -> Any:
        """
        Find instance of the given node with the same ID.

        :param node: Node to be searched for
        :return: Found node or None if node has not been found
        """
        if node.id not in self.nodes:
            return None

        if node.id in self.nodes:
            if len(self.nodes[node.id]) == 1:
                if node_type:
                    if isinstance(self.nodes[node.id][0], node_type):
                        return self.nodes[node.id][0]
                    return None
                return self.nodes[node.id][0]
            if isinstance(node, OptionNode):
                # multiple option nodes can have the same ID
                # here we can also use other techniques to find the right option
                search_node = self._find_option(node, self.nodes[node.id])
                if node_type:
                    if isinstance(search_node, node_type):
                        return search_node
                    return None
                return search_node

        return None

    @staticmethod
    def _find_option(node: OptionNode, options: List) -> Optional[OptionNode]:
        """
        Try to find the correct option node in a list of option nodes where all have the same ID.

        If multiple options with the same id exist, return the option with the same location.

        :param node: node to be searched
        :param options: list of option nodes with the same ID
        :return: Found option node or None
        """
        for option in options:
            if node.location == option.location:
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

    def validate(self, commit_hash=None) -> Tuple[Set, Network]:
        """
        Detect conflicts with respect to the reference network.

        :return: Set of detected dependency conflicts and the newly created network
        """
        new_network = Network.init_network(cfg=self.cfg)

        conflicts = ConflictDetector.detect(
            ref_network=self,
            new_network=new_network,
            enable_all_conflicts=self.cfg.enable_all_conflicts,
            commit_hash=commit_hash,
        )

        return conflicts, new_network

    def save(self) -> None:
        """Save configuration network of a project into a pickle file."""
        if not os.path.isdir(self.cfg.network_dir_path()):
            os.mkdir(self.cfg.network_dir_path())

        file_name = hashlib.md5(self.project_root.encode()).hexdigest()
        network_file = os.path.join(
            self.cfg.network_dir_path(), file_name + ".pickle"
        )

        with open(network_file, "wb") as pickle_file:
            pickle.dump(self, pickle_file)

    def traverse(self, current: Node, callback: Callable) -> None:
        """
        Traverse the configuration network.

        :param current: Starting point of traversal
        :param callback: Callback called on every visited node
        :return: None
        """
        callback(current)

        if current.children is not None:
            for child in current.children:
                self.traverse(child, callback)

    def export(
        self,
        name: str,
        export_format: str,
        include_unlinked: bool,
    ) -> None:
        """
        Export the configuration network.

        :param name: Name of the file to which the network is to be exported
        :param export_format: Format in which the network is stored, either "dot" or "json"
        :param include_unlinked: If true include all nodes else only linked value nodes
        """
        if not os.path.isdir(self.cfg.export_dir_path()):
            os.mkdir(self.cfg.export_dir_path())

        file_path = os.path.join(self.cfg.export_dir_path(), name)

        with open(file_path, "w+", encoding="utf-8") as export_file:
            if export_format == "dot":
                DotExporter(self).export(export_file, include_unlinked)
            elif export_format == "json":
                JSONExporter(self).export(export_file, include_unlinked)

    def visualize(
        self,
        name: str,
        export_format: str,
        include_unlinked: bool,
    ):
        """
        Visualize the configuration network.

        :param name: Name of the file to which the network is to be exported
        :param export_format: Format in which the network is stored, either "png" or "pdf"
        :param include_unlinked: If true include all nodes else only linked value nodes
        """
        if not os.path.isdir(self.cfg.export_dir_path()):
            os.mkdir(self.cfg.export_dir_path())

        file_path = os.path.join(self.cfg.export_dir_path(), name)

        DotExporter(self).visualize(file_path, export_format, include_unlinked)

    def get_pairs(self) -> Dict:
        """
        Extract all key-value-type pairs for each artifact in the configuration network.

        :return: Dict with key-value-type pairs for each artifact
        """
        artifact_nodes = self.get_nodes(node_type=ArtifactNode)

        artifact_options = {}

        for artifact_node in artifact_nodes:
            artifact_options[artifact_node.name] = artifact_node.get_pairs()

        return artifact_options

    @staticmethod
    def load_network(project_root: str) -> Network:
        """
        Load configuration network of a project from a pickle file.

        :param project_root: Project root of the software repository
        :return: Configuration network
        """
        file_name = hashlib.md5(project_root.encode()).hexdigest()
        network_dir = os.path.join(project_root, ".cfgnet", "network")

        network_file = os.path.join(network_dir, file_name + ".pickle")

        if not os.path.exists(network_file):
            logging.error(
                'No existing reference network for project "%s". Please call "init" first.',
                project_root,
            )
            sys.exit(1)

        with open(network_file, "rb") as pickle_file:
            return pickle.load(pickle_file)

    @staticmethod
    def init_network(cfg: NetworkConfiguration) -> Network:
        """
        Initialize a configuration network.

        :param cfg: network configuration
        :return: configuration network
        """
        repo = Git(project_root=cfg.project_root_abs)
        tracked_files: Set[str] = set(repo.get_tracked_files())

        if cfg.config_files:
            tracked_files.update(cfg.config_files)

        if cfg.system_level:
            system_files = get_system_files()
            tracked_files.update(system_files)

        project_name = cfg.project_name()
        root = ProjectNode(name=project_name, root_dir=cfg.project_root_abs)
        network = Network(project_name=project_name, root=root, cfg=cfg)

        tracked_files = IgnoreFile.filter(tracked_files)
        plugins = PluginManager.get_plugins()

        for file in sorted(tracked_files):
            abs_file_path = os.path.join(cfg.project_root_abs, file)

            if is_test_file(abs_file_path=abs_file_path):
                continue

            plugin = PluginManager.get_responsible_plugin(
                plugins, abs_file_path
            )
            if plugin:
                print("File to parse: ", abs_file_path)
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
