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

"""Datastructure for nodes of a configuration network."""

from __future__ import annotations
from typing import List, Any, Optional, Union, TYPE_CHECKING
from cfgnet.config_types.config_types import ConfigType
from cfgnet.config_types.config_type_inferer import ConfigTypeInferer
from cfgnet.exceptions.exceptions import NetworkConstructionException

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class Node:
    """
    Base class of a node in the network.

    Parameters
    ----------
    name: str
        name of a node.
    parent: str
        Parent of a node.
    children: bool
        List of children nodes.
    id: Optional[ProjectNode]
        ID of a node.
    network: Optional[Network]
        Network in which a node is contained.

    """

    def __init__(self, name: str, parent: Optional[Node] = None):
        self.name: str = name
        self.parent: Optional[Node] = parent
        self.children: List[Any] = []

        self.id: str = name
        self.network: Optional["Network"] = None

    def __str__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_child(self, node) -> None:
        """
        Add a child to this node.

        :parameter node: The node that should be added to this node.
        """
        node.parent = self
        node.id = self.id + "::::" + str(node.id)
        node.network = self.network

        self.children.append(node)

        if self.network is not None:
            self.network.nodes[node.id].append(node)


class ProjectNode(Node):
    """
    Root node of a network that represents the whole software system.

    Parameters
    ----------
    root_dir: str
        Root directory of the project.

    """

    def __init__(self, name: str, root_dir: str):
        super().__init__(name)
        self.root_dir: str = root_dir

    def add_child(self, node: ArtifactNode) -> None:
        if not isinstance(node, ArtifactNode):
            raise NetworkConstructionException(
                "Project nodes accept concept nodes only."
            )

        super().add_child(node)


class ArtifactNode(Node):
    """
    Artifact nodes model existing configuration artifacts.

    Parameters
    ----------
    file_path: str
        Absolute file path of the file.
    rel_file_path: str
        Relative file path of the file.
    concept_name: bool
        Name of the concept of the file.
    project_root: Optional[ProjectNode]
        Project node of the network.

    """

    def __init__(
        self,
        file_path: str,
        rel_file_path: str,
        concept_name: str,
        project_root=None,
    ):
        super().__init__(rel_file_path)
        self.file_path: str = file_path
        self.rel_file_path: str = rel_file_path
        self.concept_name: str = concept_name

        if project_root is not None:
            project_root.add_child(self)

        self._add_file_name_option()

    def get_nodes(
        self,
        artifact: Optional[ArtifactNode] = None,
        node_type: Optional[Any] = None,
    ) -> List[Any]:
        """Return all value nodes of an artifact."""
        nodes: List[Node] = []
        node_type = ValueNode if node_type is None else node_type
        current = artifact if artifact is not None else self
        self._traverse_artifact_node(nodes, current, node_type)
        return nodes

    def _traverse_artifact_node(
        self, nodes: List[Node], current: Node, node_type
    ) -> None:
        if isinstance(current, node_type):
            nodes.append(current)
        if current.children is not None:
            for child in current.children:
                self._traverse_artifact_node(nodes, child, node_type)

    def add_child(self, node: OptionNode) -> None:
        if not isinstance(node, OptionNode):
            raise NetworkConstructionException(
                "Artifact nodes accept artifact nodes and option nodes only."
            )

        super().add_child(node)

    def _add_file_name_option(self) -> None:
        """Add default option to the artifact node."""
        option = OptionNode(
            name="file", location="file_path", config_type=ConfigType.PATH
        )
        self.add_child(option)
        value = ValueNode(name=self.rel_file_path)
        option.add_child(value)

    def get_pairs(self) -> List:
        """Get all option-value-type pairs from the artifact."""
        value_nodes = self.get_nodes(node_type=ValueNode)
        return [
            {
                "option": x.get_options(),
                "value": x.name,
                "type": x.config_type.name,
            }
            for x in value_nodes
        ]


class OptionNode(Node):
    """
    Option nodes refer to commands or lines of code in an artifact.

    Parameters
    ----------
    display_option_id: str
        Option ID for nested options.
    location: int
        Line number of the option.
    prevalue_node: bool
        Indicates whether the option is a prevalue node.
    config_type: ConfigType
        Type of configuration option/value.

    """

    def __init__(
        self,
        name: str,
        location: str,
        config_type: ConfigType = ConfigType.UNKNOWN,
    ):
        super().__init__(name)
        self.display_option_id: str = name
        self.location: str = location
        self.prevalue_node: bool = False
        self.config_type = config_type

    def __str__(self):
        return self.id + "(location: " + str(self.location) + ")"

    def add_child(self, node: Union[OptionNode, ValueNode]) -> None:
        if not isinstance(node, OptionNode) and not isinstance(
            node, ValueNode
        ):
            raise NetworkConstructionException(
                "Option nodes accept option nodes and Value nodes only."
            )

        # if config type is unknown then the child node inherits type from parent
        if node.config_type == ConfigType.UNKNOWN:
            node.config_type = self.config_type

        if isinstance(node, OptionNode):
            node.display_option_id = (
                self.display_option_id + "::" + node.display_option_id
            )

        if isinstance(node, ValueNode):
            self.prevalue_node = True
            if node.config_type == ConfigType.UNKNOWN:
                node.config_type = ConfigTypeInferer().get_config_type(
                    option_name=self.name, value=node.name
                )

        super().add_child(node)


class ValueNode(Node):
    """
    Value nodes represent actual parameters associated to an option node.

    Parameters
    ----------
    config_type: ConfigType
        Type of configuration option/value.
    possible_values: Dict[Tuple, Str]
        Dictionary of possible values for a source code config option computed
        using a control flow graph and constant propagation.

    """

    def __init__(self, name: str):
        super().__init__(str(name))
        self.config_type = ConfigType.UNKNOWN

    def __eq__(self, other):
        return self.name == other.name

    # pylint: disable=useless-super-delegation
    def __hash__(self):
        """Make ValueNode hashable."""
        return super().__hash__()

    def get_options(self) -> str:
        """
        Get names of all option nodes of the value node.

        :return: String of concatenated option names
        """
        option_nodes = []
        parent = self.parent
        while isinstance(parent, OptionNode):
            option_nodes.append(parent.name)
            parent = parent.parent

        if len(option_nodes) > 1:
            return ".".join(option_nodes[::-1])

        return option_nodes[0]

    def add_child(self, node: Node) -> None:
        raise NetworkConstructionException(
            "Value nodes do not accept children."
        )
