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
import os
import re

from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class ConfigParserPlugin(Plugin):
    def __init__(self):
        super().__init__("configparser")

    def _parse_config_file(self, abs_file_path, rel_file_path, root):
        file_name = os.path.basename(abs_file_path)

        artifact = ArtifactNode(file_name, abs_file_path, rel_file_path, root)

        with open(abs_file_path, "r", encoding="utf-8") as config_file:
            file_content = config_file.read()

        try:
            dummy_section = "[dummy_section]\n"
            config = configparser.ConfigParser(
                interpolation=None, allow_no_value=True
            )
            config.read_string(dummy_section + file_content)
        except configparser.Error as error:
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
                section_node = OptionNode(
                    section_name, "section: " + section_name
                )
                artifact.add_child(section_node)
                parent = section_node

            for option in section.keys():

                option_node = OptionNode(
                    option,
                    "section: " + section_name + ", option: " + option,
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

                    value_node = ValueNode(value)
                    option_node.add_child(value_node)

                else:
                    logging.warning('Empty value in file "%s"', rel_file_path)
                    parent.children.remove(option_node)

        return artifact

    def is_responsible(self, abs_file_path):
        return re.match(r".*\.(ini|properties)$", abs_file_path)
