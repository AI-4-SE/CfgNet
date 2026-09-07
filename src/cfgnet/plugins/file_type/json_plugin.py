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

from typing import Union, Optional, Dict, List
from cfgnet.network.nodes import (
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin


class JsonPlugin(Plugin):
    def __init__(self, name=None, threshold=524288):
        if name is None:
            super().__init__("json", threshold=threshold)
        else:
            super().__init__(name, threshold=threshold)

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith(".json"):
            return True
        return False

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> Optional[ArtifactNode]:
        try:
            with open(abs_file_path, "r", encoding="utf-8") as json_file:
                line_number_dict = {}
                lineno = 1
                for line in json_file:
                    line = line.strip()
                    line = line.replace("\\\\", "\\")
                    if len(line) > 0:
                        line_number_dict[line] = lineno
                    lineno += 1

            with open(abs_file_path, "r", encoding="utf-8") as json_file:
                json_object = json.load(json_file)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            logging.warning(
                'Failed to parse json file "%s" due to "%s"',
                rel_file_path,
                error,
            )
            return None

        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )
        self._parse_json_object(
            json_object=json_object,
            parent=artifact,
            line_number_dict=line_number_dict,
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
                config_type = self.get_config_type(key)
                option = OptionNode(
                    name=key,
                    location=self._get_line_number(line_number_dict, key),
                    config_type=config_type,
                )
                parent.add_child(option)
                child = json_object[key]

                self._parse_json_object(child, option, line_number_dict)
                if not option.children:
                    parent.children.remove(option)
            return

        if isinstance(json_object, list):
            if not isinstance(parent, ArtifactNode):
                if any(isinstance(item, dict) for item in json_object):
                    for item in json_object:
                        self._parse_json_object(item, parent, line_number_dict)
                else:
                    parent.add_child(ValueNode(name=str(json_object)))
            return
        if not isinstance(parent, ArtifactNode):
            value = ValueNode(name=json_object)
            parent.add_child(value)

    @staticmethod
    def _get_line_number(lines_dict: Dict, name: str) -> str:
        """
        Get line number of an option.

        :param lines_dict: Dictionary containing lines and corresponding line numbers
        :param: name: name of option
        :return: line number of option
        """
        try:
            line = next(filter(lambda x: f'"{name}"' in x, lines_dict.keys()))
            return lines_dict[line]
        except StopIteration:
            return "unknown"
