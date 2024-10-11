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
from cfgnet.plugins.file_type.hadoop_plugin import HadoopPlugin


class HadoopCommonPlugin(HadoopPlugin):
    def __init__(self):
        super().__init__("hadoop-common")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return file_name == "core-site.xml"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(
            (
                "name",
                "interface",
                ".base",
                ".userbase",
                ".groupbase",
                ".providers",
                ".defaultFS",
            )
        ):
            return ConfigType.NAME

        if option_name.endswith((".version")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith(
            (".ms", ".secs", ".timeout", ".interval", ".duration")
        ):
            return ConfigType.TIME

        if option_name.endswith(
            (
                ".threads",
                ".attempts",
                ".capacity",
                ".limit",
                ".length",
                ".factor",
                ".num_retries",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith((".url")):
            return ConfigType.URL

        if option_name.endswith(
            (
                ".keystore",
                ".file",
                ".path",
                ".truststore",
                ".dir",
                ".directories",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith((".password")):
            return ConfigType.PASSWORD

        if option_name.endswith((".users", ".username", ".staticuser.user")):
            return ConfigType.USERNAME

        if option_name.endswith((".enable")):
            return ConfigType.BOOLEAN

        if option_name.endswith((".host")):
            return ConfigType.IP_ADDRESS

        if option_name.endswith((".port")):
            return ConfigType.PORT

        if option_name.endswith((".mode")):
            return ConfigType.TYPE

        if option_name.endswith((".buffer", ".blocksize", ".size", ".mb")):
            return ConfigType.SIZE

        if option_name.endswith((".key", ".token", ".id")):
            return ConfigType.ID

        return super().get_config_type(option_name, value)
