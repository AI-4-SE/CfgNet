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

from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin
from cfgnet.config_types.config_types import ConfigType


class MavenWrapperPlugin(ConfigParserPlugin):
    """Plugin for parsing Maven wrapper properties files."""

    def __init__(self):
        super().__init__("maven-wrapper")

    def is_responsible(self, abs_file_path):
        """
        Check if the plugin is responsible for the given file.

        :param abs_file_path: Absolute path to the file
        :return bool: True if the plugin is responsible for the file
        """
        return abs_file_path.endswith("maven-wrapper.properties")

    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        """
        Get the configuration type for a given option name and value.

        :param option_name: Name of the option
        :param value: Value of the option
        """
        if option_name in ["distributionUrl", "wrapperUrl"]:
            return ConfigType.URL
        return super().get_config_type(option_name, value)
