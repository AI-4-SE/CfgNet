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

from cfgnet.exceptions.exceptions import (
    InvalidNetworkStateException,
    NetworkConstructionException,
)


class Node:
    """
    Base class of a node in the network.

    Members:
        * name -- name of the node
        * parent -- parent node
        * children -- list of children of this node
        * id -- identifier of a node that represents the path from the root
        * network -- configuration network of a node
    """

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

        self.id = name
        self.network = None

    def __str__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_child(self, node):
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

    def get_id_from_hierarchy(self):
        """
        Get node id as a concatenation of the node's hierarchy.

        Used for network validity check. Should always match the actual
        node id.
        """
        return (
            self.parent.get_id_from_hierarchy() + "::::"
            if self.parent is not None
            else ""
        ) + self.id.split("::::")[-1]

    def integrity(self):
        """
        Check the integrity of the subnetwork from this node.

        Returns True iff:
            * node IDs match paths,
            * node IDs are unique,
            * there are no option nodes without children, and
            * children of option nodes are either all options or all values,
              i.e. neither empty nor a mix of options and values.

        Otherwise, raises an InvalidNetworkStateException.
        """
        self._traverse(self, Node._node_integrity_check)
        return True

    def _traverse(self, current, callback):
        """
        Traverse network.

        :param current: Starting point of traversal
        :param callback: Callback called on every visited node
        :return: None
        """
        callback(current)

        if current.children is not None:
            for child in current.children:
                self._traverse(child, callback)

    def _node_integrity_check(self):
        """Perform integrity checks on a single node."""
        self._check_if_id_matches_hierarchy()
        self._check_if_prevalue_nodes_are_unique()
        if isinstance(self, OptionNode):
            self._check_option_node_children()

    def _check_if_id_matches_hierarchy(self):
        """
        Check if the node ID matches the hierarchy in the network.

        If the ID does not match the hierarchy, a InvalidNetworkStateException
        is raised.
        """
        if self.id != self.get_id_from_hierarchy():
            raise InvalidNetworkStateException(
                "Node ID does not match hierarchy"
            )

    def _check_option_node_children(self):
        """
        Check if the rules for option node children apply.

        Every option node must have at least one child and all children have to
        be of the same type (either OptionNode or ValueNode). If any of those
        rules is violated, a InvalidNetworkStateException is raised.
        """
        # check if options nodes have children
        self._check_if_option_node_has_children()
        self._check_if_option_node_children_have_same_type()

    def _check_if_option_node_has_children(self):
        """Raise InvalidNetworkStateException if node does not have children."""
        if not self.children:
            message = (
                'Problem with node "'
                + str(self)
                + ":\nOptionNode must have children"
            )
            raise InvalidNetworkStateException(message)

    def _check_if_option_node_children_have_same_type(self):
        """
        Check if all children of option nodes are of the same type.

        If they have different types, raise InvalidNetworkStateException.
        """
        if not (
            all(isinstance(child, OptionNode) for child in self.children)
            or all(isinstance(child, ValueNode) for child in self.children)
        ):
            raise InvalidNetworkStateException(
                "OptionNode child types may not be mixed"
            )

    def _check_if_prevalue_nodes_are_unique(self):
        if self.children is not None:
            prevalue_nodes_list = [
                child.id
                for child in self.children
                if isinstance(child, OptionNode) and child.prevalue_node
            ]
            prevalue_nodes_set = set(prevalue_nodes_list)
            if len(prevalue_nodes_list) != len(prevalue_nodes_set):
                if isinstance(self, OptionNode):
                    message = (
                        'Problems with children of node "'
                        + str(self)
                        + ":\nNode IDs of prevalue nodes must be unique"
                    )
                else:
                    message = (
                        'Problems with children of node "'
                        + self.id
                        + '"'
                        + ":\nNode IDs of prevalue nodes must be unique"
                    )
                raise InvalidNetworkStateException(message)


class ProjectNode(Node):
    """
    Root node of a configuration network.

    A root node represents the whole software system.

    Members:
    root_dir -- root directory of the software system
    """

    def __init__(self, name, root_dir):
        super().__init__(name)
        self.root_dir = root_dir

    def add_child(self, node):
        if not isinstance(node, ConceptNode):
            raise NetworkConstructionException(
                "Project nodes accept concept nodes only."
            )

        super().add_child(node)


class ConceptNode(Node):
    """Represent used software or more abstract concepts like source code."""

    def add_child(self, node):
        if not isinstance(node, ArtifactNode) and not isinstance(
            node, ConceptNode
        ):
            raise NetworkConstructionException(
                "Concept nodes accept concept nodes and artifact nodes only."
            )

        super().add_child(node)


class ArtifactNode(Node):
    """Represent configuration artifacts."""

    def __init__(self, name, file_path, rel_file_path, concept_root=None):
        super().__init__(rel_file_path)
        self.file_path = file_path
        self.rel_file_path = rel_file_path
        if concept_root is not None:
            concept_root.add_child(self)
        self._add_file_name_option()

    def get_nodes(self, artifact=None, node_type=None):
        """Return all value nodes of an artifact."""
        nodes = []
        node_type = ValueNode if node_type is None else node_type
        current = artifact if artifact is not None else self
        self._traverse_artifact_node(nodes, current, node_type)
        return nodes

    def _traverse_artifact_node(self, nodes, current, node_type):
        if isinstance(current, node_type):
            nodes.append(current)
        if current.children is not None:
            for child in current.children:
                self._traverse_artifact_node(nodes, child, node_type)

    def add_child(self, node):
        if not isinstance(node, ArtifactNode) and not isinstance(
            node, OptionNode
        ):
            raise NetworkConstructionException(
                "Artifact nodes accept artifact nodes and option nodes only."
            )

        super().add_child(node)

    def _add_file_name_option(self):
        """Add default option to the artifact node."""
        option = OptionNode(name="file", location="file_path")
        self.add_child(option)
        value = ValueNode(self.rel_file_path)
        option.add_child(value)


class OptionNode(Node):
    """
    Option nodes refer to commands or lines of code in an artifact.

    Members:
    display_option_id -- option id used when conflicts are printed
    location -- location of node, i.e. line number or path
    """

    def __init__(self, name, location):
        # super().__init__(str(location) + "::" + name)
        super().__init__(name)
        self.display_option_id = name
        self.location = location
        self.prevalue_node = False

    def __str__(self):
        return self.id + "(location: " + str(self.location) + ")"

    def add_child(self, node):
        if not isinstance(node, OptionNode) and not isinstance(
            node, ValueNode
        ):
            raise NetworkConstructionException(
                "Option nodes accept option nodes and Value nodes only."
            )

        if isinstance(node, OptionNode):
            node.display_option_id = (
                self.display_option_id + "::" + node.display_option_id
            )

        if isinstance(node, ValueNode):
            self.prevalue_node = True

        super().add_child(node)


class ValueNode(Node):
    """
    Value nodes represent actual parameters associated to an option node.

    This parameter should be the name of the value node.

    Members:
    type -- data type of the stored value
    """

    def __init__(self, name):
        super().__init__(str(name))

    def __eq__(self, other):
        return self.name == other.name

    # pylint: disable=useless-super-delegation
    def __hash__(self):
        """Make ValueNode hashable."""
        return super().__hash__()

    def add_child(self, node):
        raise NetworkConstructionException(
            "Value nodes do not accept children."
        )
