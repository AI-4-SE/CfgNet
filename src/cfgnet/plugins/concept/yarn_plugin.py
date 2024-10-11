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


class YarnPlugin(HadoopPlugin):
    def __init__(self):
        super().__init__("yarn")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return file_name == "yarn-site.xml"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name.endswith((".hostname")):
            return ConfigType.NAME

        if option_name.endswith((".version")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith(("ms", ".timeout")):
            return ConfigType.TIME

        if option_name.endswith((".thread-count", "-retries")):
            return ConfigType.NUMBER

        if option_name.endswith((".uri")):
            return ConfigType.URL

        if option_name.endswith(
            (
                ".include-path",
                ".exclude-path",
                ".local-dirs",
                "path",
                ".dir",
                ".root-dir",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith((".enable")):
            return ConfigType.BOOLEAN

        if option_name.endswith((".bind-host", ".address")):
            return ConfigType.IP_ADDRESS

        if option_name.endswith((".cluster-id", ".id")):
            return ConfigType.ID

        return super().get_config_type(option_name, value)
