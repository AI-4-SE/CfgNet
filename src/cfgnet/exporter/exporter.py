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

from json import dumps
from typing import Dict, Set, TYPE_CHECKING, TextIO
from graphviz import Digraph
from cfgnet.network.nodes import Node

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class DotExporter:
    _dot: Digraph
    _dot_exported_nodes: Set

    def __init__(self, network: "Network"):
        self.network = network

    def export(self, file: TextIO, include_unlinked: bool) -> None:
        """
        Export the network graph in the DOT graph description language.

        Edges between linked configuration nodes will be drawn in red.

        :param file: file to export the network graph
        :param include_unlinked: if true include all value nodes, else only linked nodes
        """
        self._create_digraph(include_unlinked)
        if self._dot:
            file.write(self._dot.source)

    def visualize(
        self,
        name: str,
        export_format: str,
        include_unlinked: bool,
    ) -> None:
        """
        Visualize the configuration network using the given format.

        :param data_dir: directory to store the graph
        :param format: format to visualize the network
        :param include_unlinked: if true include all value nodes, else only linked nodes
        """
        self._create_digraph(include_unlinked)
        if self._dot:
            self._dot.render(
                filename=name,
                format=export_format,
                cleanup=True,
            )

    def _create_digraph(self, include_unlinked: bool):
        """Create the Digraph of configuration network."""
        self._dot_exported_nodes = set()
        self._dot = Digraph(strict=True)
        self._dot.attr(overlap="false")
        for link in self.network.links:
            id_a = self._dot_add_node(link.node_a)
            id_b = self._dot_add_node(link.node_b)
            self._dot.edge(
                id_a, id_b, constraint="false", color="red", dir="none"
            )
        if include_unlinked:
            self.network.traverse(self.network.root, self._dot_add_node)

    def _dot_add_node(self, node: Node):
        id_node = self._dot_node_id(node)
        if id_node in self._dot_exported_nodes:
            return id_node
        self._dot_exported_nodes.add(id_node)
        self._dot.node(id_node, str(node.name)[:24])
        if node.parent is not None:
            id_parent = self._dot_node_id(node.parent)
            self._dot_add_node(node.parent)
            self._dot.edge(id_parent, id_node)
        return id_node

    @staticmethod
    def _dot_node_id(node: Node):
        return f"node_{hash(node)}"


class JSONExporter:
    _json_export_cache: Dict

    def __init__(self, network: "Network"):
        self.network = network

    def export(self, file: TextIO, include_unlinked: bool):
        """
        Export the entire network graph to JSON, for visualizing with D3.js.

        Links have a "type" property that is "link" for linked configuration
        nodes and "network" for links that constitute the network hierarchy.

        :param file: file to export the network graph
        :param include_unlinked: if true include all value nodes, else only linked nodes
        """
        self._json_export_cache = {
            "nodes": {},
            "links": [],
        }
        for link in self.network.links:
            id_a = self._json_add_node(link.node_a)
            id_b = self._json_add_node(link.node_b)
            self._json_export_cache["links"].append(
                {"source": id_a, "target": id_b, "type": "link"}
            )
        if include_unlinked:
            self.network.traverse(self.network.root, self._json_add_node)

        self._json_export_cache["nodes"] = list(
            self._json_export_cache["nodes"].values()
        )
        file.write(dumps(self._json_export_cache, indent=4))

    def _json_add_node(self, node: Node):
        if node.id in self._json_export_cache["nodes"]:
            return self._json_export_cache["nodes"][node.id]["id"]

        id_json = len(self._json_export_cache["nodes"])
        self._json_export_cache["nodes"].update(
            {
                node.id: {
                    "id": id_json,
                    "id_cfgnet": node.id,
                    "label": node.name,
                    "type": type(node).__name__,
                }
            }
        )
        if node.parent is not None:
            id_json_parent = self._json_add_node(node.parent)
            self._json_export_cache["links"].append(
                {
                    "source": id_json_parent,
                    "target": id_json,
                    "type": "network",
                }
            )

        return id_json
