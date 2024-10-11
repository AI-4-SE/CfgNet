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

from typing import Optional
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


class HadoopPlugin(Plugin):
    def __init__(self, name=None):
        if name is None:
            super().__init__("hadoop")
        else:
            super().__init__(name)

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        try:
            tree = ET.parse(abs_file_path)
            tree_root = tree.getroot()

            # Remove namespace prefixes
            for elem in tree_root.getiterator():
                if elem.tag is not ET.Comment:
                    elem.tag = ET.QName(elem).localname
            # Remove unused namespace declarations
            ET.cleanup_namespaces(tree_root)

            option_root = OptionNode(
                tree_root.tag,
                tree_root.sourceline,
                self.get_config_type(tree_root.tag),
            )
            artifact.add_child(option_root)
            for child in tree_root:
                if child.tag is not ET.Comment:
                    self.parse_tree(child, parent_node=option_root)

        except ET.Error as error:
            logging.warning(
                'Failed to parse xml file "%s" due to %s', rel_file_path, error
            )

        return artifact

    def is_responsible(self, abs_file_path: str) -> bool:
        return abs_file_path.endswith(".json")

    def parse_tree(self, subtree: _Element, parent_node: Node):
        name = subtree.tag

        if name:
            if name == "property":
                config_type = self.get_config_type(name)
                property_option = OptionNode(
                    name, subtree.sourceline, config_type
                )
                parent_node.add_child(property_option)

                property_name = None
                property_value = None

                # Capture property details
                for child in subtree:
                    if child.tag == "name":
                        property_name = child.text.strip()
                    elif child.tag == "value":
                        property_value = child.text.strip()

                if property_name:
                    print(property_name, config_type)
                    option = OptionNode(
                        property_name, subtree.sourceline, ConfigType.UNKNOWN
                    )
                    property_option.add_child(option)

                    # Add the value node, under the property name
                    if property_value:
                        config_type = self.get_config_type(
                            property_name, property_value
                        )
                        option_value = OptionNode(
                            "value", subtree.sourceline, config_type
                        )
                        option.add_child(option_value)
                        value_node = ValueNode(name=property_value)
                        option_value.add_child(value_node)

                    # Add the description node, under the property name
                    # if property_description:
                    #    option_desc = OptionNode(
                    #        "description",
                    #        subtree.sourceline,
                    #        ConfigType.NAME,
                    #    )
                    #    option.add_child(option_desc)
                    #    description_node = ValueNode(name=property_description)
                    #    option_desc.add_child(description_node)

            else:
                config_type = self.get_config_type(name)
                option = OptionNode(name, subtree.sourceline, config_type)
                parent_node.add_child(option)

                value_name = subtree.text.strip()

                if value_name:
                    value_node = ValueNode(name=value_name)
                    option.add_child(value_node)
                else:
                    for child in subtree:
                        if child.tag is not ET.Comment:
                            self.parse_tree(child, option)

            # remove option nodes without children
            if not option.children:
                parent_node.children.remove(option)
