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
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin


class RabbitMQPlugin(ConfigParserPlugin):
    """Plugin for parsing RabbitMQ configuration files."""

    def __init__(self):
        super().__init__("rabbitmq")

    def is_responsible(self, abs_file_path: str) -> bool:
        """Check if the plugin is responsible for the given file."""
        file_name = os.path.basename(abs_file_path)
        return file_name.endswith("rabbitmq.conf")

    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        """Determine the configuration type based on the option name and value."""
        option_name = option_name.lower()

        if option_name in ["listeners.tcp.default", "management.tcp.port"]:
            return ConfigType.PORT

        if option_name in ["cluster_nodes", "cluster_partition_handling"]:
            return ConfigType.TYPE

        if option_name in ["log.file", "config_files", "enabled_plugins"]:
            return ConfigType.PATH

        if option_name in ["vm_memory_high_watermark", "disk_free_limit"]:
            return ConfigType.SIZE

        if option_name in ["heartbeat", "channel_max", "frame_max"]:
            return ConfigType.NUMBER

        if option_name in ["default_user", "default_pass"]:
            return ConfigType.PASSWORD

        if option_name in ["loopback_users", "collect_statistics"]:
            return ConfigType.BOOLEAN

        if option_name in ["auth_mechanisms", "auth_backends"]:
            return ConfigType.TYPE

        return super().get_config_type(option_name)
