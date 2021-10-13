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

import lxml.etree as ET

from cfgnet.network.nodes import ArtifactNode, Node, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class XmlPlugin(Plugin):
    """Plugin for parsing XML files."""

    def __init__(self, file_size_threshold=40_000):
        super().__init__("xml", file_size_threshold)

    def _parse_config_file(self, abs_file_path, rel_file_path, concept_root):
        """
        Create an artifact node from information given in an XML file.

        :param abs_file_path: absolute file path to the XML file
        :param rel_file_path: relative file path to the XML file
        :param concept_root: concept node that gets this artifact node as child
        :param content: content of an XML file (alternative to the json file)
        :return: artifact node
        """
        file_name = os.path.basename(abs_file_path)
        artifact = ArtifactNode(
            file_name, abs_file_path, rel_file_path, concept_root
        )

        # try to parse XML file
        try:
            xml_tree = ET.parse(abs_file_path)
            tree_root = xml_tree.getroot()

            self.parse_tree(
                tree_root, parent_node=artifact, rel_file_path=rel_file_path
            )

        except ET.ParseError as error:
            logging.warning(
                'Failed to parse XML file "%s" due to "%s"',
                rel_file_path,
                error,
            )

        return artifact

    def is_responsible(self, abs_file_path):
        file_name = os.path.basename(abs_file_path)
        if file_name.endswith(".xml"):
            return True

        return False

    def parse_tree(self, subtree_root, parent_node: Node, rel_file_path):
        if subtree_root.tag is not ET.Comment:
            current_node = OptionNode(
                subtree_root.tag, subtree_root.sourceline
            )
            parent_node.add_child(current_node)

            current_attribs = subtree_root.attrib
            for key in current_attribs:
                option_node = OptionNode(key, subtree_root.sourceline)
                current_node.add_child(option_node)

                value = current_attribs[key]
                value_node = ValueNode(value)
                option_node.add_child(value_node)

            text = subtree_root.text
            if text:
                text = text.strip()
                if text:
                    if current_attribs:
                        dummy_option = OptionNode(
                            "<" + subtree_root.tag + ">",
                            subtree_root.sourceline,
                        )
                        current_node.add_child(dummy_option)
                    else:
                        dummy_option = current_node
                    value_node = ValueNode(text)
                    dummy_option.add_child(value_node)

            ambiguous_children = self._ambiguous_children(subtree_root)
            for child in subtree_root:
                if child.tag not in ambiguous_children:
                    self.parse_tree(child, current_node, rel_file_path)

            if not current_node.children:
                current_node.parent.children.remove(current_node)

    @staticmethod
    def _ambiguous_children(root):
        """Return tags of children that are not unique."""
        child_tags = [child.tag for child in root]
        ambiguous_tags = []
        while child_tags:
            current_tag = child_tags[0]
            child_tags.remove(current_tag)
            if current_tag in child_tags:
                ambiguous_tags.append(current_tag)
        return ambiguous_tags
