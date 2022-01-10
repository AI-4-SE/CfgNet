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

from typing import List, Any, Optional
from cfgnet.config_types.config_types import ConfigType

from cfgnet.network.nodes import (
    ArtifactNode,
    OptionNode,
    ProjectNode,
    ValueNode,
)
from cfgnet.plugins.plugin import Plugin


COMMANDS = ["from", "env", "expose", "add", "copy", "cmd", "entrypoint"]


class Command:
    cmd: str
    start_line: str
    value: List[Any]

    def __init__(self, cmd, start_line, value):
        self.cmd = cmd
        self.start_line = start_line
        self.value = value

    def __str__(self):
        return f"{self.cmd}:{self.value}"


def parse_string(content: str) -> List[Command]:
    data: List[Command] = []
    line_no = 0
    for line in content.splitlines():
        line_no += 1
        line = line.strip()
        if line.startswith("#") or len(line) == 0:
            continue  # TODO: support parser directives

        # get command and its values
        parts = line.split()
        command = parts[0].lower()
        values = parts[1:]

        # if there is no cmd, add line to the last created cmd
        if command not in COMMANDS:
            last_cmd = data[-1]
            if last_cmd.cmd == "env":
                values = parse_env(line)
                last_cmd.value += values
                continue

        # parse env command
        if command == "env":
            line = " ".join(values)
            values = parse_env(line)

        # parse entrypoint and cmd command
        if command in ("entrypoint", "cmd"):
            # remove brackets at the beginning and end
            if values[0].startswith("[") and values[-1].endswith("]"):
                without_brackets = " ".join(values)[1:-1]
                params = without_brackets.replace(" ", "").split(",")
                values = [p.replace('"', "") for p in params]

        cmd = Command(cmd=command, start_line=line_no, value=values)

        data.append(cmd)

    return data


def parse_env(line: str) -> List[str]:
    """
    Get key value pairs for env command.

    :param line: line to parse
    :return: list of key=value pairs
    """
    values = re.findall(r"(\w+=\"*[\w\d\-\_ ]*\"*)", line)
    values = [v.strip() for v in values]
    return values


def parse_file(abs_file_path: str) -> List[Command]:
    with open(abs_file_path, "r", encoding="utf-8") as file:
        return parse_string(file.read())


class DockerPlugin(Plugin):
    expose_command = re.compile(
        r"(?P<port>[0-9]{2,4})(\/)(?P<protocol>(tcp|udp))"
    )

    def __init__(self):
        super().__init__("docker")

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        file_name = os.path.basename(abs_file_path)

        artifact = ArtifactNode(
            name=file_name,
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        data = parse_file(abs_file_path)
        # files that are destinations in `ADD` and `COPY`
        destination_files = []

        for cmd in data:
            option = OptionNode(cmd.cmd, cmd.start_line)
            artifact.add_child(option)

            if cmd.cmd == "from":
                if len(cmd.value) == 3:
                    image = ValueNode(
                        cmd.value[0], config_type=ConfigType.IMAGE
                    )
                    name = ValueNode(cmd.value[2])
                    option_image = OptionNode("image", cmd.start_line)
                    option_name = OptionNode("name", cmd.start_line)
                    option.add_child(option_image)
                    option.add_child(option_name)
                    option_image.add_child(image)
                    option_name.add_child(name)
                else:
                    option.add_child(ValueNode(cmd.value[0]))

            if cmd.cmd == "env":
                for value in cmd.value:
                    parts = value.split("=")
                    env_var_option = OptionNode(parts[0], cmd.start_line)
                    option.add_child(env_var_option)
                    value_node = ValueNode(parts[1])
                    env_var_option.add_child(value_node)

            elif cmd.cmd in ["cmd", "entrypoint"]:
                exec_command = " ".join(cmd.value)
                exec_command_node = OptionNode(
                    "exec_command", location=option.location
                )
                option.add_child(exec_command_node)
                exec_command_node.add_child(ValueNode(exec_command))

                self._add_params(option, cmd.value)

            elif cmd.cmd in ["add", "copy"]:
                src = OptionNode("src", cmd.start_line)
                option.add_child(src)
                # remove leading `./` or `/`
                src_file = re.sub(r"^(\.)?/", "", cmd.value[-2])
                src.add_child(
                    ValueNode(name=src_file, config_type=ConfigType.PATH)
                )
                dest = OptionNode("dest", cmd.start_line)
                option.add_child(dest)
                dest_value = cmd.value[-1]
                dest.add_child(
                    ValueNode(name=dest_value, config_type=ConfigType.PATH)
                )
                destination_files.append(dest_value)
                if len(cmd.value) > 2:  # handle flags
                    flag_re = re.compile(r"--(chown|from)=([^ ]+)")
                    for part in cmd.value:
                        match = flag_re.match(part)
                        if match:
                            flag_key = match.group(1)
                            flag_value = match.group(2)
                            flag_node = OptionNode(flag_key, cmd.start_line)
                            option.add_child(flag_node)
                            flag_node.add_child(ValueNode(flag_value))

            elif cmd.cmd == "expose":
                for value in cmd.value:
                    self._parse_expose(option, value)

            if not option.children:
                artifact.children.remove(option)

        return artifact

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)

        if file_name == "Dockerfile":
            return True

        return False

    def _parse_expose(self, option: OptionNode, value: str) -> None:
        match = self.expose_command.fullmatch(value)
        if match:
            port = ValueNode(match.group("port"), config_type=ConfigType.PORT)
            protocol = ValueNode(
                match.group("protocol"), config_type=ConfigType.PROTOCOL
            )
            option_port = OptionNode("port", option.location)
            option_protocol = OptionNode("protocol", option.location)
            option.add_child(option_port)
            option.add_child(option_protocol)
            option_port.add_child(port)
            option_protocol.add_child(protocol)
        else:
            option.add_child(
                ValueNode(name=value, config_type=ConfigType.PORT)
            )

    @staticmethod
    def _add_params(option: OptionNode, parameters: List[str]):
        param_counter = 0
        for param in parameters:
            option_param = OptionNode(
                "param" + str(param_counter), option.location
            )
            option.add_child(option_param)
            value = re.sub(r"^(\.)?/", "", param)
            option_param.add_child(ValueNode(value))
            param_counter += 1
