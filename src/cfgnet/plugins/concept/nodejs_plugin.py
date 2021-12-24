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
import os
import logging

from typing import Union, Optional, Dict, List
from cfgnet.network.network import (
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin
from cfgnet.config_types.config_types import ConfigType

EXCLUDE_KEYS = ["keywords", "description"]


class NodejsPlugin(Plugin):
    def __init__(self):
        super().__init__("nodejs")
        self.current_config_type = ConfigType.UNKNOWN

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith("package.json"):
            return True
        return False

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        artifact = ArtifactNode(
            name=os.path.basename(abs_file_path),
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        try:
            # store line and line number in a dict
            with open(abs_file_path, "r", encoding="utf-8") as json_file:
                line_number_dict = {}
                lineno = 1
                for line in json_file:
                    line = line.strip()
                    if len(line) > 0:
                        line_number_dict[line] = lineno
                    lineno += 1

            with open(abs_file_path, "r", encoding="utf-8") as json_file:
                json_object = json.load(json_file)
                self._parse_json_object(
                    json_object=json_object,
                    parent=artifact,
                    line_number_dict=line_number_dict,
                )

        except json.JSONDecodeError as error:
            logging.warning(
                'Failed to parse json file "%s" due to "%s"',
                rel_file_path,
                error,
            )

        return artifact

    def _parse_json_object(
        self,
        json_object: Union[Dict, List],
        parent: Union[ArtifactNode, OptionNode],
        line_number_dict: Dict,
    ) -> None:
        if isinstance(json_object, dict):
            for key in json_object:
                if key not in EXCLUDE_KEYS:
                    self.current_config_type = self.get_config_type(key)
                    option = OptionNode(
                        name=key,
                        location=self._get_line_number(line_number_dict, key),
                    )
                    parent.add_child(option)
                    child = json_object[key]

                    self._parse_json_object(child, option, line_number_dict)
                    if not option.children:
                        parent.children.remove(option)
            return

        if isinstance(json_object, list):
            for item in json_object:
                if isinstance(item, (dict, list)):
                    self._parse_json_object(item, parent, line_number_dict)

                else:
                    virtual_option_name = f"{parent.name}/{item}"
                    virtual_option = OptionNode(
                        name=virtual_option_name,
                        location=self._get_line_number(
                            line_number_dict, parent.name
                        ),
                    )
                    parent.add_child(virtual_option)
                    value = ValueNode(
                        name=item, config_type=self.current_config_type
                    )
                    virtual_option.add_child(value)

        else:
            value = ValueNode(
                name=json_object, config_type=self.current_config_type
            )
            if not isinstance(parent, ArtifactNode):
                parent.add_child(value)

    @staticmethod
    def _get_line_number(lines_dict: Dict, name: str) -> str:
        """
        Get line number of an option.

        :param lines_dict: Dictionary containing lines and corresponding line numbers
        :param: name: name of option
        :return: line number of option
        """
        line = next(filter(lambda x: f'"{name}"' in x, lines_dict.keys()))
        return lines_dict[line]

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:
        """
        Find config type based on option name.

        :param option_name: name of option
        :return: config type
        """
        if option_name in (
            "version",
            "dependencies",
            "devDependencies",
            "engines",
        ):
            return ConfigType.VERSION_NUMBER
        if option_name in ("main", "files", "man"):
            return ConfigType.FILEPATH
        if option_name in ("scripts", "bin"):
            return ConfigType.COMMAND
        if option_name == "name":
            return ConfigType.NAME
        if option_name == "url":
            return ConfigType.URL
        if option_name == "email":
            return ConfigType.EMAIL
        if option_name in ("repository", "author", "funding", "type"):
            return ConfigType.UNKNOWN
        return self.current_config_type
