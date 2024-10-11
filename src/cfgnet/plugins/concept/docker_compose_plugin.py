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
    ports = re.compile(r"(?P<host>[0-9]{4}):(?P<container>[0-9]{4})")

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
                port_in = ValueNode(name=match.group("host"))
                port_out = ValueNode(name=match.group("container"))
                option_port_in = OptionNode(
                    "host", node.start_mark.line + 1, ConfigType.PORT
                )
                option_port_out = OptionNode(
                    "container", node.start_mark.line + 1, ConfigType.PORT
                )
                parent.add_child(option_port_in)
                parent.add_child(option_port_out)
                option_port_in.add_child(port_in)
                option_port_out.add_child(port_out)
            else:
                if len(node.value.split("=")) == 2:
                    self._parse_value_assignment(node=node, parent=parent)
                    return

                name = node.value

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
        config_type = self.get_config_type(
            option_name=value_parts[0], value=value_parts[1]
        )
        variable = OptionNode(
            name=value_parts[0],
            location=str(node.start_mark.line + 1),
            config_type=config_type,
        )
        parent.add_child(variable)
        value = ValueNode(name=value_parts[1])
        variable.add_child(value)

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(("size", "weight", "height")):
            return ConfigType.SIZE

        if option_name == "env_file":
            return ConfigType.PATH

        if option_name.endswith(
            (
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
                "build",
            )
        ):
            return ConfigType.NAME

        if option_name == "rate":
            return ConfigType.SPEED

        if option_name.endswith(
            (
                "cpu_rt_runtime",
                "cpu_rt_period",
                "start_period",
                "interval",
                "timeout",
                "stop_grace_period",
            )
        ):
            return ConfigType.TIME

        if option_name.endswith(
            (
                "cpu_shares",
                "uid",
                "gid",
                "retries",
                "priority",
                "pids_limit",
                "sysctls",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith(("external", "disable", "init", "attachable")):
            return ConfigType.BOOLEAN

        if option_name == "test":
            return ConfigType.COMMAND

        if option_name.endswith(
            (
                "dns",
                "ipv4_address",
                "ipv6_address",
                "subnet",
                "link_local_ips",
                "host_ip",
                "ip_range",
                "gateway",
                "aux_addresses",
            )
        ):
            return ConfigType.IP_ADDRESS

        if option_name.endswith(("dns_search", "extra_hosts")):
            return ConfigType.URL

        return super().get_config_type(option_name, value)
