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

import logging
import os

from typing import Optional, Tuple, List
from lxml import etree as ET
from lxml.etree import _Element

from cfgnet.config_types.config_types import ConfigType
from cfgnet.network.nodes import (
    ArtifactNode,
    Node,
    OptionNode,
    ProjectNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin

TAGS_CONTAINING_LISTS = {
    "goal",
    "exclude",
    "include",
    "arg",
    "pattern",
    "class",
    "package",
    "ignoredResourcePattern",
}


class MavenPlugin(Plugin):
    def __init__(self):
        super().__init__("maven")

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        file_name = os.path.basename(abs_file_path)

        artifact = ArtifactNode(
            name=file_name,
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        try:
            maven_tree = ET.parse(abs_file_path)
            tree_root = maven_tree.getroot()

            # Remove namespace prefixes
            for elem in tree_root.getiterator():
                if elem.tag is not ET.Comment:
                    elem.tag = ET.QName(elem).localname
            # Remove unused namespace declarations
            ET.cleanup_namespaces(tree_root)

            option_root = OptionNode(tree_root.tag, tree_root.sourceline)
            artifact.add_child(option_root)
            for child in tree_root:
                if child.tag is not ET.Comment:
                    self.parse_tree(child, parent_node=option_root)

        except ET.Error as error:
            logging.warning(
                'Failed to parse xml file "%s" due to %s', rel_file_path, error
            )

        self._add_executable_name(artifact)

        return artifact

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)

        if file_name == "pom.xml":
            return True

        return False

    def parse_tree(self, subtree_root: _Element, parent_node: Node):
        name = self._make_name(subtree_root)
        if name:
            option = OptionNode(name, subtree_root.sourceline)
            parent_node.add_child(option)

            self._add_attribs(subtree_root, option)

            text = subtree_root.text
            if text:
                text = text.strip()
                if text:

                    config_type = self.get_config_type(option.name)

                    name = (
                        f"{option.name}:{text}"
                        if config_type == ConfigType.VERSION_NUMBER
                        else text
                    )

                    value_node = ValueNode(name=name)
                    option.add_child(value_node)

            for child in subtree_root:
                if child.tag is not ET.Comment:
                    self.parse_tree(child, option)

            # remove option nodes without children
            if not option.children:
                parent_node.children.remove(option)

    @staticmethod
    def _add_attribs(subtree_root: _Element, current_node: OptionNode):
        current_attribs = subtree_root.attrib
        for key in current_attribs:
            option = OptionNode(key, subtree_root.sourceline)
            current_node.add_child(option)
            value = current_attribs[key]

            config_type = MavenPlugin.get_config_type(option.name)

            name = (
                f"{option.name}:{value}"
                if config_type == ConfigType.VERSION_NUMBER
                else value
            )

            value_node = ValueNode(name=name)
            option.add_child(value_node)

    # pylint: disable=too-many-return-statements
    @staticmethod
    def _make_name(current_item: _Element) -> str:
        """
        Construct a name for an option node to avoid ambiguous option nodes.

        :param current_item: lxml etree element that should be inserted as an option node
        :return: constructed name
        """
        name_element = current_item.find("id")
        if name_element is not None:
            if name_element.text is not None:
                return current_item.tag + "_" + name_element.text

        name_element = current_item.find("groupId")
        if name_element is not None:
            item_artifact_id = current_item.find("artifactId")
            if item_artifact_id is not None:
                return (
                    current_item.tag
                    + "_"
                    + name_element.text
                    + "/"
                    + item_artifact_id.text
                )

            return current_item.tag + "_" + name_element.text

        item_artifact_id = current_item.find("artifactId")
        if item_artifact_id is not None:
            return current_item.tag + "_" + item_artifact_id.text

        name_element = current_item.find("name")
        if name_element is not None:
            return current_item.tag + "_" + name_element.text

        name_element = current_item.find("key")
        if name_element is not None:
            return current_item.tag + "_" + name_element.text

        if current_item.tag == "notifier":
            name_element = current_item.find("type")
            if name_element is not None:
                return current_item.tag + "_" + name_element.text

        if current_item.tag in TAGS_CONTAINING_LISTS:
            if current_item.text is not None:
                return current_item.tag + "_" + current_item.text

        return current_item.tag

    def _add_executable_name(self, artifact: ArtifactNode) -> None:
        try:
            option_nodes: List[OptionNode] = artifact.get_nodes(
                node_type=OptionNode
            )
            project_option: OptionNode = next(
                filter(lambda node: node.name == "project", option_nodes)
            )
            project_option_children: List[OptionNode] = project_option.children
            artifactid_node: OptionNode = next(
                filter(
                    lambda node: node.name == "artifactId",
                    project_option_children,
                )
            )
            artifactid = artifactid_node.children[0].name
            artifactid_location = str(artifactid_node.location)

            version, version_location = self._get_version_for_executable_name(
                project_option
            )
            (
                packaging,
                packaging_location,
            ) = self._get_packaging_for_executable_name(project_option)

            location = self.merge_executable_name_locations(
                artifactid_location, version_location, packaging_location
            )

            executable_name_prefix = "target/"

            executable_name = f"{artifactid}{version}.{packaging}"

            option_node = OptionNode("ExecutableName", location)
            value_node = ValueNode(executable_name_prefix + executable_name)

            artifact.add_child(option_node)
            option_node.add_child(value_node)

            if version != "":
                executable_name_no_version = f"{artifactid}.{packaging}"
                option_node_no_version = OptionNode(
                    "ExecutableNameNoVersion", location
                )
                artifact.add_child(option_node_no_version)
                option_node_no_version.add_child(
                    ValueNode(
                        executable_name_prefix + executable_name_no_version
                    )
                )

        except StopIteration:
            logging.warning(
                "Failed to add executable name to artifact %s",
                artifact.rel_file_path,
            )

    @staticmethod
    def merge_executable_name_locations(
        artifactid_location: str,
        version_location: Optional[str],
        packaging_location: Optional[str],
    ) -> str:
        location = artifactid_location
        if version_location and packaging_location:
            location += ", " + version_location + ", and " + packaging_location
        elif version_location and not packaging_location:
            location += " and " + version_location
        elif not version_location and packaging_location:
            location += " and " + packaging_location
        return location

    @staticmethod
    def _get_version_for_executable_name(
        project_option_node: OptionNode,
    ) -> Tuple[str, Optional[str]]:
        try:
            version_node = next(
                filter(
                    lambda node: node.name == "version",
                    project_option_node.children,
                )
            )

            name = version_node.children[0].name.split(":")[-1]

            return (
                "-" + name,
                str(version_node.location),
            )
        except StopIteration:
            return "", None

    @staticmethod
    def _get_packaging_for_executable_name(
        project_option_node: OptionNode,
    ) -> Tuple[str, Optional[str]]:
        try:
            packaging_node = next(
                filter(
                    lambda node: node.name == "packaging",
                    project_option_node.children,
                )
            )
            return (
                packaging_node.children[0].name,
                str(packaging_node.location),
            )
        except StopIteration:
            return "jar", None

    @staticmethod
    def get_config_type(name: str) -> ConfigType:
        """
        Get config type based on the option name.

        :param name: option name
        :return: ConfigType
        """
        if name in ("modelVersion", "version"):
            return ConfigType.VERSION_NUMBER

        # TODO: Check for other config types

        return ConfigType.UNKNOWN
