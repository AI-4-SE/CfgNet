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
from typing import Optional, Dict
import flatdict
import yaml
from cfgnet.network.nodes import (
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin
from cfgnet.config_types.config_types import ConfigType


class SpringPlugin(Plugin):
    application_yaml_regex = re.compile(r"application(.(dev|prod)+)?.yml")
    application_properties_regex = re.compile(
        r"application(.(dev|prod)+)?.properties"
    )
    # bootstrap_yaml_regex = re.compile(r"bootstrap(.(dev|prod)+)?.yml")
    # bootstrap_properties_regex = re.compile(r"bootstrap(.(dev|prod)+)?.properties")

    def __init__(self):
        super().__init__("spring")

    def is_responsible(self, abs_file_path):
        if self.application_yaml_regex.search(abs_file_path):
            return True
        if self.application_properties_regex.search(abs_file_path):
            return True
        return False

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        if abs_file_path.endswith(".yml"):
            artifact = ArtifactNode(
                file_path=abs_file_path,
                rel_file_path=rel_file_path,
                concept_name=self.concept_name,
                project_root=root,
            )

            self._parse_yml_file(
                abs_file_path=abs_file_path,
                rel_file_path=rel_file_path,
                artifact=artifact,
            )

            return artifact

        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        self._parse_properties_file(
            abs_file_path=abs_file_path,
            rel_file_path=rel_file_path,
            artifact=artifact,
        )

        return artifact

    def _parse_properties_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        artifact: ArtifactNode,
    ):
        """Parse spring properties files."""
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
            return

        for section_name in config:
            if section_name == "DEFAULT":
                continue

            section = config[section_name]

            if len(section.keys()) == 0:
                continue

            if section_name == "dummy_section":
                parent = artifact

            for option in section.keys():
                config_type = self.get_config_type(option_name=option)
                option_node = OptionNode(
                    name=option,
                    location=self.get_line_number(
                        option_name=option, line_dict=line_dict
                    ),
                    config_type=config_type,
                )
                parent.add_child(option_node)

                value = section[option]
                if value:
                    while value.startswith("\n"):
                        value = value[1:]

                    value = re.sub(r"\\\n\s*", "", value)

                    value_node = ValueNode(value)
                    option_node.add_child(value_node)

                else:
                    logging.warning('Empty value in file "%s"', rel_file_path)
                    parent.children.remove(option_node)

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

    # pylint: disable=broad-except
    def _parse_yml_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        artifact: ArtifactNode,
    ):
        """Parse spring yml files."""
        with open(abs_file_path, "r", encoding="utf-8") as file:
            line_number_dict = {}
            lineno = 1
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    line_number_dict[line] = lineno
                lineno += 1

        try:
            with open(abs_file_path, encoding="utf-8") as yaml_file:
                parsed_yaml = yaml.load(yaml_file, Loader=yaml.FullLoader)
                yaml_dict = flatdict.FlatDict(parsed_yaml, ".")
                if len(yaml_dict) != 0:
                    for key, values in yaml_dict.items():
                        if isinstance(values, list):
                            yaml_dict[key] = ", ".join(values)
        except Exception as error:
            logging.warning(
                'Failed to parse yml file "%s"'
                '" with spring parser due to "%s"',
                rel_file_path,
                str(error),
            )
            return

        for key, value in yaml_dict.items():
            line_number = self.get_line_number(
                option_name=key.split(".")[-1], line_dict=line_number_dict
            )
            config_type = self.get_config_type(key)
            option = OptionNode(
                name=key, location=line_number, config_type=config_type
            )
            artifact.add_child(option)
            value = ValueNode(name=value)
            option.add_child(value)

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name.endswith(
            (
                ".show-sql",
                ".cache",
                ".trace",
                ".await-termination",
                ".pool.allow-core-thread-timeout",
                ".wait-for-jobs-to-complete-on-shutdown",
                ".auto-startup",
                ".use-code-as-default-message",
                ".fallback-to-system-locale",
                ".always-use-message-format",
                ".register-shutdown-hook",
                ".log-startup-info",
                ".lazy-initialization",
                ".allow-circular-references",
                ".allow-bean-definition-overriding",
                ".unique-names",
                ".use-legacy-processing",
                ".log-request-details",
                ".ignore",
                ".image.invert",
                "debug",
                ".clean-history-on-start",
                ".register-shutdown-hook",
                ".aop.auto",
                ".proxy-target-class",
                ".enabled",
            )
        ):
            return ConfigType.BOOLEAN

        if option_name.endswith(
            (
                "size",
                ".max-file-size",
                ".total-size-cap",
                ".image.width",
                ".max-in-memory-size",
                ".image.height",
                ".pool.size",
                ".max-history",
                ".core-size",
                ".pool.max-size",
            )
        ):
            return ConfigType.SIZE

        if option_name.endswith(
            (
                "platform",
                "-name",
                ".database",
                ".authentication-database",
                ".provider",
                ".scheduler-name",
                ".jmx-name",
                ".name",
                ".jmx.server",
                ".active",
                ".basenames",
                ".profiles.default",
            )
        ):
            return ConfigType.NAME

        if option_name.endswith(
            (
                ".location",
                ".file",
                ".jdbc.schema",
                ".config",
                ".path",
                ".image",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith(
            (".default-domain", ".host", ".uri", "url", "-uri")
        ):
            return ConfigType.URL

        if option_name.endswith(
            (
                ".timeout-per-shutdown-phase",
                ".startup-delay",
                "pool.keep-alive",
                ".await-termination-period",
            )
        ):
            return ConfigType.TIME

        if option_name.endswith(".port"):
            return ConfigType.PORT

        if option_name.endswith(".username"):
            return ConfigType.USERNAME

        if option_name.endswith(".password"):
            return ConfigType.PASSWORD

        if option_name.endswith(".mail"):
            return ConfigType.EMAIL

        return super().get_config_type(option_name, value)
