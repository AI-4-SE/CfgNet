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
import configparser
import logging
import re
from collections import OrderedDict
from typing import List, Dict

from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)


class ConfigParserPlugin(Plugin):
    def __init__(self, name=None):
        if name is None:
            super().__init__("configparser")
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
            line_dict = {}
            lineno = 1
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    line_dict[line] = lineno
                lineno += 1

        with open(abs_file_path, "r", encoding="utf-8") as config_file:
            file_content = config_file.read()

        try:
            if self.concept_name == "php":
                config = configparser.RawConfigParser(
                    dict_type=MultiOrderedDict, strict=False
                )
                config.read_string(file_content)
            else:
                dummy_section = "[dummy_section]\n"
                config = configparser.ConfigParser(
                    interpolation=None, allow_no_value=True
                )
                config.read_string(dummy_section + file_content)
        except (AttributeError, configparser.Error) as error:
            logging.warning(
                'Failed to parse ini file "%s"'
                '" with configparser due to "%s"',
                rel_file_path,
                str(error),
            )
            return artifact

        for section_name in config:
            # configparser always adds a DEFAULT section which is empty
            # and we don't need it
            if section_name == "DEFAULT":
                continue

            section = config[section_name]

            # skip empty sections
            if len(section.keys()) == 0:
                continue

            # the dummy section that we had to create should not
            # become a node in our network
            if section_name == "dummy_section":
                parent = artifact
            else:
                line_number = (
                    self.get_line_number(
                        option_name=section_name, line_dict=line_dict
                    ),
                )
                section_node = OptionNode(
                    name=section_name, location=line_number
                )
                artifact.add_child(section_node)
                parent = section_node

            for option in section.keys():
                if option in self.excluded_keys:
                    continue
                config_type = self.get_config_type(option_name=option)
                line_number = self.get_line_number(
                    option_name=option, line_dict=line_dict
                )
                option_node = OptionNode(
                    name=option,
                    location=line_number,
                    config_type=config_type,
                )
                parent.add_child(option_node)

                value = section[option]
                if value:
                    while value.startswith("\n"):
                        # remove \n at beginning of value:
                        value = value[1:]

                    # remove backslash followed by newline and
                    # (if present) whitespace
                    value = re.sub(r"\\\n\s*", "", value)
                    value = value.replace('"', "")

                    # check if value is a list
                    value_parts = value.split(",")
                    if len(value_parts) > 1:
                        value_parts = [x.strip() for x in value_parts]
                        value = str(value_parts)

                    value_node = ValueNode(name=value)
                    option_node.add_child(node=value_node)

                else:
                    logging.warning('Empty value in file "%s"', rel_file_path)
                    parent.children.remove(option_node)

        return artifact

    def is_responsible(self, abs_file_path):
        return re.match(r".*\.(ini|properties)$", abs_file_path)

    def get_line_number(self, option_name: str, line_dict: Dict) -> str:
        """
        Get line number from line dictionary.

        :param option_name: option name in line
        :param line_dict: dictionary of lines
        :return: line number as string
        """
        for line in line_dict.keys():
            if option_name in line:
                lineno = line_dict[line]
                del line_dict[line]
                return str(lineno)
        return "Unknown"
