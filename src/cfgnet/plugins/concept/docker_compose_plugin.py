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
            match = self.ports.match(node.value)
            if match is not None:
                port_in = ValueNode(match.group("in"))
                port_out = ValueNode(match.group("out"))
                option_port_in = OptionNode("in", node.start_mark.line + 1)
                option_port_out = OptionNode("out", node.start_mark.line + 1)
                parent.add_child(option_port_in)
                parent.add_child(option_port_out)
                option_port_in.add_child(port_in)
                option_port_out.add_child(port_out)
            else:
                value = ValueNode(node.value)

                if isinstance(parent, ArtifactNode):
                    option = OptionNode(
                        "unnamed_option", node.start_mark.line + 1
                    )
                    parent.add_child(option)
                    option.add_child(value)
                else:
                    parent.add_child(value)
