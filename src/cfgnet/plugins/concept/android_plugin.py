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

from typing import Optional
from lxml import etree as ET
from lxml.etree import _Element, _Comment

from cfgnet.config_types.config_types import ConfigType
from cfgnet.network.nodes import (
    ArtifactNode,
    Node,
    OptionNode,
    ProjectNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin


class AndroidPlugin(Plugin):
    def __init__(self):
        super().__init__("android")
        self.lines = None

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return file_name == "AndroidManifest.xml"

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

        with open(abs_file_path, "r", encoding="utf-8") as src:
            self.lines = src.readlines()

        try:
            tree = ET.parse(abs_file_path)
            root = tree.getroot()

            self.parse_tree(root, parent_node=artifact)

        except ET.Error as error:
            logging.warning(
                'Failed to parse xml file "%s" due to %s', rel_file_path, error
            )

        return artifact

    def parse_tree(self, element: _Element, parent_node: Node):
        option_name = element.tag
        config_type = self.get_config_type(option_name=option_name)
        parent_option = OptionNode(
            option_name, str(element.sourceline), config_type
        )
        parent_node.add_child(parent_option)

        for attr_name, attr_value in element.attrib.items():
            key = attr_name.split("}")[-1]
            config_type = self.get_config_type(key)
            line_number = self.find_attribute_line(key, attr_value, self.lines)

            if not line_number:
                line_number = str(element.sourceline)

            option = OptionNode(key, line_number, config_type)
            parent_option.add_child(option)
            value_node = ValueNode(attr_value)
            option.add_child(value_node)

        for child in element:
            if not isinstance(child, _Comment):
                self.parse_tree(child, parent_option)

    def find_attribute_line(
        self, attr_name, attr_value, lines
    ) -> Optional[str]:
        for i in range(len(lines) - 1):
            if attr_name in lines[i] and attr_value in lines[i]:
                return str(i + 1)
        return None

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name in ("maxrecents", "maxaspectratio", "priority"):
            return ConfigType.NUMBER

        if option_name.endswith(("version", "versioncode")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith(("package", "name", "label", "description")):
            return ConfigType.NAME

        if option_name.endswith(("mode")):
            return ConfigType.TYPE

        if option_name.endswith(("enabled", "exported", "required")):
            return ConfigType.BOOLEAN

        if option_name.startswith(("allow")):
            return ConfigType.BOOLEAN

        if option_name.endswith(("size", "height", "width")):
            return ConfigType.SIZE

        if option_name.endswith(("host")):
            return ConfigType.IP_ADDRESS

        if option_name.endswith(("port")):
            return ConfigType.PORT

        if option_name.endswith(("path", "location")):
            return ConfigType.PATH

        if option_name.startswith(("path")):
            return ConfigType.PATH

        if option_name.endswith(("type", "level")):
            return ConfigType.TYPE

        return super().get_config_type(option_name, value)
