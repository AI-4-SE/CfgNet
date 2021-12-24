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

import yaml
import yaml.reader
from yaml.nodes import MappingNode, ScalarNode, SequenceNode
from yaml.parser import ParserError
from yaml.scanner import ScannerError

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
            name=os.path.basename(abs_file_path),
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        with open(abs_file_path, "r", encoding="utf8") as yaml_file:
            try:
                docs = yaml.compose_all(yaml_file)
                for root_tree in docs:
                    self._iter_tree(root_tree, artifact)
            except ScannerError as error:
                logging.warning(
                    "Invalid YAML file %s: %s", abs_file_path, error.problem
                )
            except ParserError as error:
                logging.warning(
                    "Invalid YAML file %s: %s", abs_file_path, error.problem
                )
            except yaml.reader.ReaderError as error:
                logging.warning(
                    "Invalid YAML file %s: %s", abs_file_path, error
                )
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
        index = 0
        for child in node.value:
            if isinstance(child, MappingNode):
                virtual_option = OptionNode(
                    parent.name + "_" + str(index),
                    node.start_mark.line + 1,
                )
                parent.add_child(virtual_option)

                self._iter_tree(child, virtual_option)
                index += 1
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
            option = OptionNode(key.value, key.start_mark.line + 1)
            parent.add_child(option)

            self._iter_tree(node[1], option)

    @staticmethod
    def _parse_scalar_node(node, parent):
        if node.value != "":
            value = ValueNode(node.value)
            if isinstance(parent, ArtifactNode):
                option = OptionNode("unnamed_option", node.start_mark.line + 1)
                parent.add_child(option)
                option.add_child(value)
            else:
                parent.add_child(value)