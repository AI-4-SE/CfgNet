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
import logging
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

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(
                    node.targets[0], ast.Name
                ):
                    key = node.targets[0]
                    settings[key] = node.value

        for key, value in settings.items():
            if isinstance(value, ast.Constant):
                self.__parse_constant(artifact, key, value)
            elif isinstance(value, ast.Name):
                dict_id = value.id
                match = next(
                    filter(lambda x: x.id == dict_id, settings.keys())
                )
                item = settings[match]
                if isinstance(item, ast.List):
                    self.__parse_list(artifact, key, item)
                else:
                    logging.warning(
                        'Failed to parse ast type "%s".', type(value)
                    )
            elif isinstance(value, ast.BinOp):
                self.__parse_operation(artifact, key, value)
            elif isinstance(value, ast.List):
                self.__parse_list(artifact, key, value)
            elif isinstance(value, ast.Dict):
                self.__parse_dict(artifact, key, value)
            else:
                logging.warning('Failed to parse ast type "%s".', type(value))

        return artifact

    def __parse_constant(self, parent, key, value) -> None:
        config_type = self.get_config_type(option_name=key.id)
        option_node = OptionNode(
            name=key.id, location=key.lineno, config_type=config_type
        )
        parent.add_child(option_node)
        value_node = ValueNode(name=ast.literal_eval(value))
        option_node.add_child(value_node)

    def __parse_operation(self, parent, key, value) -> None:
        config_type = self.get_config_type(option_name=key.id)
        option_node = OptionNode(
            name=key.id, location=key.lineno, config_type=config_type
        )
        parent.add_child(option_node)
        value_node = ValueNode(name=ast.unparse(value))
        option_node.add_child(value_node)

    def __parse_list(self, parent, key, value) -> None:
        config_type = self.get_config_type(option_name=key.id)
        option_node = OptionNode(
            name=key.id, location=key.lineno, config_type=config_type
        )
        parent.add_child(option_node)
        value_node = ValueNode(name=ast.unparse(value))
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
            if isinstance(option_value, ast.Constant):
                config_type = self.get_config_type(
                    option_name=ast.literal_eval(option)
                )
                sub_option_node = OptionNode(
                    name=ast.literal_eval(option),
                    location=key.lineno,
                    config_type=config_type,
                )
                option_node.add_child(sub_option_node)
                value_node = ValueNode(name=ast.literal_eval(option_value))
                sub_option_node.add_child(value_node)

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:  # noqa: C901
        """
        Find config type based on option name.

        Option types included from: https://docs.djangoproject.com/en/4.2/ref/settings/.

        :param option_name: name of option
        :return: config type
        """
        option_name = option_name.lower()

        if option_name.endswith(("loaction", "path", "dir", "paths", "root")):
            return ConfigType.PATH

        if option_name.endswith("version"):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith("url"):
            return ConfigType.URL

        if option_name.endswith(("timeout", "seconds")):
            return ConfigType.TIME

        if option_name.endswith("domain"):
            return ConfigType.DOMAIN_NAME

        if option_name.endswith("password"):
            return ConfigType.PASSWORD

        if option_name.endswith("user"):
            return ConfigType.USERNAME

        if option_name.endswith("host"):
            return ConfigType.HOST

        if option_name.endswith("port"):
            return ConfigType.PORT

        if option_name.endswith(("language_code", "languages")):
            return ConfigType.LANGUAGE

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

        if option_name.endswith(("size")):
            return ConfigType.SIZE

        if option_name.endswith(("format")):
            return ConfigType.PATTERN

        if option_name.endswith(("email")):
            return ConfigType.EMAIL

        if option_name.endswith(("permissions")):
            return ConfigType.PERMISSION

        if option_name.endswith(("message_level")):
            return ConfigType.MODE

        if option_name.endswith(("id")):
            return ConfigType.ID

        if option_name.endswith(
            (
                "backend",
                "csrf_failure_view",
                "engine",
                "default_auto_field",
                "default_exception_reporter",
                "default_file_storage",
                "form_renderer",
                "logging_config",
                "test_runner",
                "backends",
                "auth_user_model",
                "password_hashers",
                "message_storage",
                "session_serializer",
                "staticfiles_storage",
                "file_upload_handlers",
            )
        ):
            return ConfigType.CLASS

        return ConfigType.UNKNOWN
