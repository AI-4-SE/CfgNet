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

import json
import logging
import os

from cfgnet.network.nodes import ArtifactNode, Node, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class JsonPlugin(Plugin):
    """Plugin for parsing json files."""

    def __init__(self, file_size_threshold=40_000):
        super().__init__("json", file_size_threshold)

    def _parse_config_file(self, abs_file_path, rel_file_path, concept_root):
        """
        Create an artifact node from information given in a json file.

        :param abs_file_path: absolute file path to the json file
        :param rel_file_path: relative file path to the json file
        :param concept_root: concept node that gets this artifact node as child
        :param content: content of a json file (alternative to the json file)
        :return: artifact node
        """
        file_name = os.path.basename(abs_file_path)
        artifact = ArtifactNode(
            file_name, abs_file_path, rel_file_path, concept_root
        )

        # try to parse json file
        try:
            with open(abs_file_path, "r", encoding="utf-8") as json_file:
                file_content = json_file.read().strip()
                if file_content:
                    json_file.seek(0)  # go back to file start after read()
                    json_object = json.load(json_file)
                    self.parse_json_object(
                        json_object, artifact, rel_file_path
                    )
                else:
                    logging.warning('Empty json file "%s"', rel_file_path)
        except json.JSONDecodeError as error:
            logging.warning(
                'Failed to parse json file "%s" due to "%s"',
                rel_file_path,
                error,
            )
        return artifact

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith(".json"):
            return True
        return False

    def parse_json_object(self, json_object, parent: Node, loc: str):
        """
        Parse a json object (dictionary, list or value) to a subtree of a configuration network.

        :param json_object: json object (dictionary, list, number, boolean or None)
        :param parent: root node of the subtree
        :param loc: location (needed for creating an option node)
        """
        if isinstance(json_object, dict):
            for key in json_object:
                option_node = OptionNode(key, location=loc)
                parent.add_child(option_node)
                sub_dict = json_object[key]
                self.parse_json_object(sub_dict, option_node, loc)
                if not option_node.children:
                    parent.children.remove(option_node)
            return

        if isinstance(json_object, list):
            for item in json_object:
                if isinstance(item, (dict, list)):
                    self.parse_json_object(item, parent, loc)

                else:
                    value_node = ValueNode(item)
                    self._add_value_node(parent, value_node)

        else:
            value_node = ValueNode(json_object)
            self._add_value_node(parent, value_node)

    @staticmethod
    def _add_value_node(parent, value_node):
        if isinstance(parent, ArtifactNode):
            logging.warning(
                'Skip parsing of file %s as it was trying add value nodes to an artifact node."',
                parent.file_path,
            )
            return
        parent.add_child(value_node)
