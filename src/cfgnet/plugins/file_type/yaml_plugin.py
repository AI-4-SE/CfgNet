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

import yaml
import yaml.reader
from yaml.nodes import MappingNode, ScalarNode, SequenceNode
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from yaml.composer import ComposerError
from yaml.reader import ReaderError

from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class YAMLPlugin(Plugin):
    def __init__(self, name=None):
        if name is None:
            super().__init__("yaml")
        else:
            super().__init__(name)

    def _parse_config_file(self, abs_file_path, rel_file_path, root):
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        try:
            with open(abs_file_path, "r", encoding="utf8") as yaml_file:
                docs = yaml.compose_all(yaml_file)
                for root_tree in docs:
                    self._iter_tree(root_tree, artifact)
        except (ScannerError, ParserError, ComposerError) as error:
            logging.warning(
                "Invalid YAML file %s: %s", abs_file_path, error.problem
            )
        except (FileNotFoundError, ReaderError) as error:
            logging.warning("Invalid YAML file %s: %s", abs_file_path, error)
        return artifact

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith(".yaml") or abs_file_path.endswith(".yml"):
            return True

        return False

    def _iter_tree(self, node, parent):
        if isinstance(node, MappingNode):
            self._parse_mapping_node(node, parent)

        if isinstance(node, SequenceNode):
            self._parse_sequence_node(node, parent)

        elif isinstance(node, tuple):
            self._parse_tuple(node, parent)

        elif isinstance(node, ScalarNode):
            self._parse_scalar_node(node, parent)

    def _parse_mapping_node(self, node, parent):
        for child in node.value:
            self._iter_tree(child, parent)

    def _parse_sequence_node(self, node, parent):
        # index = 0
        for child in node.value:
            if isinstance(child, MappingNode):
                # offset_option = OptionNode(
                #    "offset:" + str(index),
                #    node.start_mark.line + 1,
                # )
                # parent.add_child(offset_option)

                # self._iter_tree(child, offset_option)
                self._iter_tree(child, parent)
                # index += 1
            else:
                self._iter_tree(child, parent)

    def _parse_tuple(self, node, parent):
        key = node[0]

        if isinstance(key.value, list):
            for list_elem in key.value:
                if isinstance(list_elem, tuple):
                    for tuple_elem in list_elem:
                        self._iter_tree(tuple_elem, parent)
        else:
            config_type = self.get_config_type(key.value)
            option = OptionNode(
                name=key.value,
                location=str(key.start_mark.line + 1),
                config_type=config_type,
            )
            parent.add_child(option)

            self._iter_tree(node[1], option)

    def _parse_scalar_node(self, node, parent):
        # empty values are possible, but need str tag
        if node.value != "" or (
            node.value == "" and node.tag == "tag:yaml.org,2002:str"
        ):
            name = node.value if node.value != "" else ""

            name = node.value

            value = ValueNode(name=name)
            if isinstance(parent, ArtifactNode):
                option = OptionNode("unnamed_option", node.start_mark.line + 1)
                parent.add_child(option)
                option.add_child(value)
            else:
                parent.add_child(value)
