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
import os
from yaml.nodes import MappingNode
from cfgnet.network.nodes import OptionNode, ValueNode
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin


class ElasticsearchPlugin(YAMLPlugin):
    def __init__(self):
        super().__init__("elasticsearch")

    def is_responsible(self, abs_file_path):
        file_name = os.path.basename(abs_file_path)
        return file_name == "elasticsearch.yml"

    def _parse_sequence_node(self, node, parent):

        if isinstance(node.value, list):
            value_list = []
            for child in node.value:
                value_list.append(child.value)

            value_node = ValueNode(name=str(value_list))
            parent.add_child(value_node)

        else:
            index = 0
            for child in node.value:
                if isinstance(child, MappingNode):
                    offset_option = OptionNode(
                        "offset:" + str(index),
                        node.start_mark.line + 1,
                    )
                    parent.add_child(offset_option)

                    self._iter_tree(child, offset_option)
                    index += 1
                else:
                    self._iter_tree(child, parent)

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:  # noqa: C901
        """
        Find config type based on option name.

        :param option_name: name of option
        :return: config type
        """
        return ConfigType.UNKNOWN
