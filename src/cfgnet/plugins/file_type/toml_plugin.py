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
from typing import List
import toml
from toml import TomlDecodeError
from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class TomlPlugin(Plugin):
    def __init__(self, name=None):
        if name is None:
            super().__init__("toml")
        else:
            super().__init__(name)
        self.excluded_keys: List[str] = []

    def _parse_config_file(self, abs_file_path, rel_file_path, root):
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        with open(abs_file_path, "r", encoding="utf-8") as file:
            line_number_dict = {}
            lineno = 1
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    line_number_dict[line] = lineno
                lineno += 1

        with open(abs_file_path, "r", encoding="utf-8") as file:
            try:
                data = toml.load(file)
                self._iter_data(data, line_number_dict, artifact)

            except TomlDecodeError as error:
                logging.warning(
                    "Invalid Toml file %s: %s", abs_file_path, error
                )

        return artifact

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith(".toml"):
            return True

        return False

    def _iter_data(self, data, line_number_dict, parent):
        for argument, value in data.items():
            lineno = None

            for line in line_number_dict.keys():
                if argument in line:
                    lineno = line_number_dict[line]
                    del line_number_dict[line]
                    break

            if argument not in self.excluded_keys:
                config_type = self.get_config_type(argument)
                option = OptionNode(
                    name=argument,
                    location=str(lineno),
                    config_type=config_type,
                )
                parent.add_child(option)

                if isinstance(value, dict):
                    self._iter_data(value, line_number_dict, option)
                elif isinstance(value, list):
                    value_node = ValueNode(name=str(value))
                    option.add_child(value_node)
                else:
                    name = value
                    option.add_child(ValueNode(name))
