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

import toml

from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class TomlPlugin(Plugin):
    def __init__(self):
        super().__init__("toml")

    def _parse_config_file(self, abs_file_path, rel_file_path, concept_root):
        file_name = os.path.basename(abs_file_path)
        artifact = ArtifactNode(
            file_name, abs_file_path, rel_file_path, concept_root
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
            data = toml.load(file)
            self._iter_data(data, line_number_dict, artifact)

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

            option = OptionNode(argument, lineno)
            parent.add_child(option)

            if isinstance(value, dict):
                self._iter_data(value, line_number_dict, option)
            elif isinstance(value, list):
                index = 0
                for entry in value:
                    if isinstance(entry, dict):
                        virtual_option = OptionNode(
                            option.name + "_" + str(index), lineno
                        )
                        option.add_child(virtual_option)
                        self._iter_data(
                            entry, line_number_dict, virtual_option
                        )
                        index += 1
                    else:
                        option.add_child(ValueNode(entry))
            else:
                option.add_child(ValueNode(value))
