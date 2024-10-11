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


class KafkaPlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("kafka")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return file_name == "server.properties"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(("broker.id", "client.id")):
            return ConfigType.ID

        if option_name.endswith((".dirs", ".dir", ".path", ".location")):
            return ConfigType.PATH

        if option_name.endswith((".type", ".level")):
            return ConfigType.TYPE

        if option_name.endswith((".name", ".names")):
            return ConfigType.NAME

        if option_name.endswith(
            (
                ".threads",
                ".partitions",
                ".factor",
                ".requests",
                ".retries",
                ".ratio",
                ".rate",
                ".connections",
                ".limit",
                ".num",
                ".iterations",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith((".ms", ".second", ".hour", ".minute")):
            return ConfigType.TIME

        if option_name.endswith((".enable")):
            return ConfigType.BOOLEAN

        if option_name.endswith(("listeners")):
            return ConfigType.URL

        if option_name.endswith((".bytes", ".size")):
            return ConfigType.SIZE

        if option_name.endswith((".version")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith((".cmd")):
            return ConfigType.COMMAND

        if option_name.endswith((".password")):
            return ConfigType.PASSWORD

        if option_name.endswith((".username")):
            return ConfigType.USERNAME

        return super().get_config_type(option_name, value)
