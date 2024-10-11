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
import ast
from typing import Optional
from cfgnet.plugins.plugin import Plugin
from cfgnet.network.nodes import (
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.config_types.config_types import ConfigType


class DjangoPlugin(Plugin):
    def __init__(self):
        super().__init__("django")

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith("settings.py"):
            return True
        return False

    # pylint: disable=W0640
    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        """
        Parse the file to extract configuration options and values.

        :param abs_file_path: Absolute path to the file
        :param rel_file_path: Relative path to the file
        :param root: The ArtifactNode will be appended to this ProjectNode
        :return: ArtifactNode that will be added to the configuration network
        """
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        with open(abs_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        tree = ast.parse(content, filename=abs_file_path)

        settings = {}

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(
                    node.targets[0], ast.Name
                ):
                    key = node.targets[0]
                    settings[key] = node.value

            if isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Name)
                    and node.value is not None
                ):
                    key = node.target
                    settings[key] = node.value

        for key, value in settings.items():
            if not key.id.isupper():
                continue
            if isinstance(value, ast.Dict):
                self.__parse_dict(artifact, key, value)
            else:
                self.__parse(artifact, key, value)

        return artifact

    def __parse(self, parent, key, value) -> None:
        config_type = self.get_config_type(option_name=ast.unparse(key))
        option_node = OptionNode(
            name=ast.unparse(key).replace("'", ""),
            location=key.lineno,
            config_type=config_type,
        )
        parent.add_child(option_node)
        value_node = ValueNode(name=ast.unparse(value).replace("'", ""))
        option_node.add_child(value_node)

    def __parse_dict(self, parent, key, value) -> None:
        option_name = ast.unparse(key).replace("'", "")
        config_type = self.get_config_type(option_name=option_name)
        option_node = OptionNode(
            name=option_name, location=key.lineno, config_type=config_type
        )
        parent.add_child(option_node)

        for option, option_value in zip(value.keys, value.values):
            if isinstance(option_value, ast.Dict):
                self.__parse_dict(option_node, option, option_value)
            else:
                self.__parse(option_node, option, option_value)

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(("location")):
            return ConfigType.PATH

        if option_name.endswith("file_upload_max_memory_size"):
            return ConfigType.SIZE

        if option_name.endswith(("timeout", "seconds")):
            return ConfigType.TIME

        if option_name.endswith(("name", "time_zone")):
            return ConfigType.NAME

        if option_name.endswith(
            (
                "age",
                "max_number_fields",
                "max_number_files",
                "day_of_week",
                "number_grouping",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith(("format")):
            return ConfigType.TYPE

        return super().get_config_type(option_name, value)
