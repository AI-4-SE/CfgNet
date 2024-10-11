# This file is part of the CfgNet network module.
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
import re

from typing import List, Optional
import dockerfile
from cfgnet.config_types.config_types import ConfigType

from cfgnet.network.nodes import (
    ArtifactNode,
    OptionNode,
    ProjectNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin


def parse_env(line: str) -> List[str]:
    """
    Get key value pairs for env command.

    :param line: line to parse
    :return: list of key=value pairs
    """
    parts = line.split()
    parts = parts[1:]
    line = " ".join(parts)
    values = re.findall(r"((\w+=\"*[\w\-\_ ]*\")|(\w+=\$?\/?\w+))", line)
    values = [v[0].strip() for v in values]
    return values


class DockerPlugin(Plugin):
    expose_command = re.compile(
        r"(?P<port>[0-9]{2,4})(\/)(?P<protocol>(tcp|udp))"
    )

    def __init__(self):
        super().__init__("docker")
        self.env_vars = {}

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        self.env_vars.clear()
        data = dockerfile.parse_file(abs_file_path)
        # files that are destinations in `ADD` and `COPY`
        destination_files = []

        for cmd in data:
            option = self.create_option(name=cmd.cmd, location=cmd.start_line)
            artifact.add_child(option)

            if cmd.cmd == "FROM":
                if len(cmd.value) == 3:
                    image = ValueNode(cmd.value[0])
                    name = ValueNode(cmd.value[2])
                    option_image = OptionNode(
                        name="image",
                        location=cmd.start_line,
                        config_type=ConfigType.IMAGE,
                    )
                    option_name = OptionNode(
                        name="name",
                        location=cmd.start_line,
                        config_type=ConfigType.NAME,
                    )
                    option.add_child(option_image)
                    option.add_child(option_name)
                    option_image.add_child(image)
                    option_name.add_child(name)
                else:
                    option.add_child(ValueNode(cmd.value[0]))

            if cmd.cmd == "ARG":
                parts = cmd.value[0].split("=")
                if len(parts) == 2:
                    self.env_vars[parts[0]] = parts[1]

            if cmd.cmd == "ENV":
                values = parse_env(cmd.original)
                for value in values:
                    parts = value.split("=")
                    env_var_option = OptionNode(
                        name=parts[0], location=cmd.start_line
                    )
                    option.add_child(env_var_option)
                    value_name = self.check_value_name(parts[1])
                    value_node = ValueNode(value_name)
                    self.env_vars[parts[0]] = value_name
                    env_var_option.add_child(value_node)

            elif cmd.cmd in ["CMD", "ENTRYPOINT", "SH"]:
                exec_command = " ".join(cmd.value)
                exec_command_node = OptionNode(
                    "exec_command",
                    location=option.location,
                    config_type=ConfigType.COMMAND,
                )
                option.add_child(exec_command_node)
                value_name = self.check_value_name(exec_command)
                exec_command_node.add_child(ValueNode(value_name))

                self._add_params(option, cmd.value)

            elif cmd.cmd in ["ADD", "COPY"]:
                src = OptionNode("src", cmd.start_line, ConfigType.PATH)
                option.add_child(src)
                # remove leading `./` or `/`
                src_file = re.sub(r"^(\.)?/", "", cmd.value[-2])
                src_value = self.check_value_name(src_file)
                src.add_child(ValueNode(name=src_value))
                dest = OptionNode("dest", cmd.start_line, ConfigType.PATH)
                option.add_child(dest)
                dest_value = self.check_value_name(cmd.value[-1])
                dest.add_child(ValueNode(name=dest_value))
                destination_files.append(dest_value)
                for flag in cmd.flags:
                    flag_parts = flag.split("=")
                    if "--from" == flag_parts[0]:
                        flag_node = OptionNode(
                            flag_parts[0], cmd.start_line, ConfigType.NAME
                        )
                    else:
                        flag_node = OptionNode(flag_parts[0], cmd.start_line)
                    option.add_child(flag_node)
                    value_name = self.check_value_name(flag_parts[1])
                    flag_node.add_child(ValueNode(value_name))

            elif cmd.cmd == "EXPOSE":
                for value in cmd.value:
                    self._parse_expose(option, value)

            elif cmd.cmd == "WORKDIR":
                value_name = self.check_value_name(cmd.value[0])
                option.add_child(ValueNode(name=value_name))

            elif cmd.cmd == "USER":
                value_name = self.check_value_name(cmd.value[0])
                option.add_child(ValueNode(name=value_name))

            elif cmd.cmd == "VOLUME":
                value_name = self.check_value_name(cmd.value[0])
                option.add_child(ValueNode(name=value_name))

            if not option.children:
                artifact.children.remove(option)

        return artifact

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)

        if file_name == "Dockerfile":
            return True

        return False

    def _parse_expose(self, option: OptionNode, value: str) -> None:
        """Parse EXPOSE option."""
        match = self.expose_command.fullmatch(value)
        if match:
            port = ValueNode(self.check_value_name(match.group("port")))
            protocol = ValueNode(
                self.check_value_name(match.group("protocol"))
            )
            option_port = OptionNode("port", option.location, ConfigType.PORT)
            option_protocol = OptionNode(
                "protocol",
                option.location,
                self.get_config_type("protocol", match.group("protocol")),
            )
            option.add_child(option_port)
            option.add_child(option_protocol)
            option_port.add_child(port)
            option_protocol.add_child(protocol)
        else:
            option.config_type = ConfigType.PORT
            option.add_child(ValueNode(name=self.check_value_name(value)))

    def _add_params(self, option: OptionNode, parameters: List[str]) -> None:
        """Add parameters for CMD and ENTRYPOINT option."""
        param_counter = 0
        if len(parameters) == 1:
            parameters = parameters[0].split(" ")
        for param in parameters:
            config_type = self.get_config_type("", param)
            option_param = OptionNode(
                name="param" + str(param_counter),
                location=option.location,
                config_type=config_type,
            )

            value = re.sub(r"^(\.)?/", "", param)
            option.add_child(option_param)
            option_param.add_child(ValueNode(self.check_value_name(value)))
            param_counter += 1

    def create_option(self, name: str, location: str) -> OptionNode:
        """
        Create option node with corresponding type.

        :return: OptionNode
        """
        if name == "ENV":
            option = OptionNode(
                name=name,
                location=location,
                config_type=ConfigType.ENVIRONMENT,
            )
        elif name == "EXPOSE":
            option = OptionNode(
                name=name, location=location, config_type=ConfigType.PORT
            )
        elif name == "USER":
            option = OptionNode(
                name=name, location=location, config_type=ConfigType.USERNAME
            )
        elif name == "WORKDIR":
            option = OptionNode(
                name=name, location=location, config_type=ConfigType.PATH
            )
        elif name == "RUN":
            option = OptionNode(
                name=name, location=location, config_type=ConfigType.COMMAND
            )
        elif name == "VOLUME":
            option = OptionNode(
                name=name, location=location, config_type=ConfigType.PATH
            )
        else:
            option = OptionNode(name=name, location=location)

        return option

    def check_value_name(self, value_name: str) -> str:
        """
        Check values if they include env or arg values.

        If a value contains env or arg values, replace them with the concrete value.

        :return: value name
        """
        for key, value in self.env_vars.items():
            key_regex = re.compile(r"\$" + key)  # noqa: W605

            if key_regex.search(value_name):
                value_name = value_name.replace("$" + key, value)

        return value_name
