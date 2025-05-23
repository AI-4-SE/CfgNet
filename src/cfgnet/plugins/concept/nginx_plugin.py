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

import os
from typing import Optional
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.plugin import Plugin
from cfgnet.network.nodes import (
    ArtifactNode,
    OptionNode,
    ProjectNode,
    ValueNode,
)


class NginxPlugin(Plugin):
    """Plugin for parsing Nginx configuration files."""

    def __init__(self):
        super().__init__("nginx")

    def is_responsible(self, abs_file_path: str) -> bool:
        """Check if the plugin is responsible for the given file."""
        file_name = os.path.basename(abs_file_path)
        return file_name.endswith("nginx.conf")

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        """Parse the Nginx configuration file."""
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        with open(abs_file_path, "r", encoding="utf-8") as file:
            content = file.readlines()

        current_block = []
        for line_number, line in enumerate(content, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.endswith("{"):
                block_name = line[:-1].strip()
                current_block.append(block_name)
            elif line == "}":
                if current_block:
                    current_block.pop()
            else:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    option_name = parts[0]
                    value = parts[1].rstrip(";")

                    config_type = self.get_config_type(option_name, value)

                    # If we're inside a block, create a block-level node
                    if current_block:
                        # Create nodes for each level of nesting
                        parent = artifact
                        for block_name in current_block:
                            block_node = OptionNode(
                                name=block_name,
                                location=line_number,
                                config_type=config_type,
                            )
                            parent.add_child(block_node)
                            parent = block_node

                        # Add the option node under the innermost block
                        option_node = OptionNode(
                            name=option_name,
                            location=line_number,
                            config_type=config_type,
                        )
                        parent.add_child(option_node)
                        value_node = ValueNode(name=value)
                        option_node.add_child(value_node)
                    else:
                        # Create regular node for non-block options
                        option_node = OptionNode(
                            name=option_name,
                            location=line_number,
                            config_type=config_type,
                        )
                        artifact.add_child(option_node)
                        value_node = ValueNode(name=value)
                        option_node.add_child(value_node)

        return artifact

    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        """Determine the configuration type based on the option name and value."""
        option_name = option_name.lower()

        if option_name in ["listen", "server_port"]:
            return ConfigType.PORT

        if option_name in ["server_name", "hostname"]:
            return ConfigType.NAME

        if option_name in [
            "root",
            "alias",
            "include",
            "access_log",
            "error_log",
        ]:
            return ConfigType.PATH

        if option_name in [
            "client_max_body_size",
            "proxy_buffer_size",
            "proxy_buffers",
        ]:
            return ConfigType.SIZE

        if option_name in [
            "proxy_read_timeout",
            "proxy_connect_timeout",
            "keepalive_timeout",
        ]:
            return ConfigType.TIME

        if option_name in ["proxy_pass", "fastcgi_pass"]:
            return ConfigType.URL

        if option_name in ["ssl_certificate", "ssl_certificate_key"]:
            return ConfigType.PATH

        if option_name in ["ssl_protocols", "ssl_ciphers"]:
            return ConfigType.TYPE

        if option_name in ["auth_basic", "auth_basic_user_file"]:
            return ConfigType.PASSWORD

        return super().get_config_type(option_name, value)
