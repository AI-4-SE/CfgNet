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
import re
from yaml.nodes import ScalarNode
from cfgnet.config_types.config_types import ConfigType

from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin


class DockerComposePlugin(YAMLPlugin):
    file_name = re.compile(r"docker-compose(.\w+)?.yml")
    ports = re.compile(r"(?P<in>[0-9]{4}):(?P<out>[0-9]{4})")

    def __init__(self):
        super().__init__("docker-compose")

    def is_responsible(self, abs_file_path):
        if self.file_name.search(abs_file_path):
            return True
        return False

    def _parse_scalar_node(self, node, parent):
        if node.value != "":
            match = DockerComposePlugin.ports.match(node.value)
            if match is not None:
                port_in = ValueNode(name=match.group("in"))
                port_out = ValueNode(name=match.group("out"))
                option_port_in = OptionNode(
                    "in", node.start_mark.line + 1, ConfigType.PORT
                )
                option_port_out = OptionNode(
                    "out", node.start_mark.line + 1, ConfigType.PORT
                )
                parent.add_child(option_port_in)
                parent.add_child(option_port_out)
                option_port_in.add_child(port_in)
                option_port_out.add_child(port_out)
            else:
                if len(node.value.split("=")) == 2:
                    self._parse_value_assignment(node=node, parent=parent)
                    return

                name = (
                    f"{parent.name}:{node.value}"
                    if parent.config_type == ConfigType.VERSION_NUMBER
                    else node.value
                )

                value = ValueNode(name=name)

                if isinstance(parent, ArtifactNode):
                    option = OptionNode(
                        "unnamed_option", node.start_mark.line + 1
                    )
                    parent.add_child(option)
                    option.add_child(value)
                else:
                    parent.add_child(value)

    def _parse_value_assignment(
        self, node: ScalarNode, parent: OptionNode
    ) -> None:
        value_parts = node.value.split("=")
        config_type = self.get_config_type(option_name=value_parts[0])
        variable = OptionNode(
            name=value_parts[0],
            location=str(node.start_mark.line + 1),
            config_type=config_type,
        )
        parent.add_child(variable)
        value = ValueNode(name=value_parts[1])
        variable.add_child(value)

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:  # noqa: C901
        """
        Find config type based on option name.

        :param option_name: name of option
        :return: config type
        """
        option_name = option_name.lower()

        if option_name == "version":
            return ConfigType.VERSION_NUMBER
        if option_name in ("ports", "port", "expose", "PORT", "tmpfs"):
            return ConfigType.PORT
        if option_name == "image":
            return ConfigType.IMAGE
        if option_name == ("size", "weight", "height"):
            return ConfigType.SIZE
        if option_name in ("path", "file", "env_file"):
            return ConfigType.PATH
        if option_name == "environment":
            return ConfigType.ENVIRONMENT
        if option_name in ("command", "entrypoint", "test"):
            return ConfigType.COMMAND
        if option_name in (
            "name",
            "driver",
            "labels",
            "hostname",
            "cap_add",
            "cap_drop",
            "cgroup_parent",
            "source",
            "container_name",
            "depends_on",
            "registry",
            "service",
            "external_links",
        ):
            return ConfigType.NAME
        if option_name == "rate":
            return ConfigType.SPEED
        if option_name in (
            "cpu_rt_runtime",
            "cpu_rt_period",
            "start_period",
            "interval",
            "timeout",
            "stop_grace_period",
        ):
            return ConfigType.TIME
        if option_name in (
            "cpu_count",
            "cpu_shares",
            "uid",
            "gid",
            "retries",
            "priority",
            "pids_limit",
            "sysctls",
        ):
            return ConfigType.NUMBER
        if option_name == "cpu_percent":
            return ConfigType.FRACTION
        if option_name in ("external", "disable", "init", "attachable"):
            return ConfigType.BOOLEAN
        if option_name in (
            "mode",
            "condition",
            "network_mode",
            "restart",
            "userns_mode",
        ):
            return ConfigType.MODE
        if option_name in (
            "dns",
            "ipv4_address",
            "ipv6_address",
            "subnet",
            "link_local_ips",
            "host_ip",
            "ip_range",
            "gateway",
            "aux_addresses",
        ):
            return ConfigType.IP_ADDRESS
        if option_name in ("dns_search", "extra_hosts"):
            return ConfigType.URL
        if any(option_name.endswith(x) for x in ["user", "username"]):
            return ConfigType.USERNAME
        if any(option_name.endswith(x) for x in ["password"]):
            return ConfigType.PASSWORD
        if option_name == "platform":
            return ConfigType.PLATFORM
        if option_name == "protocol":
            return ConfigType.PROTOCOL

        return ConfigType.UNKNOWN
