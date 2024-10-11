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


class AlluxioPlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("alluxio")

    def is_responsible(self, abs_file_path: str) -> bool:
        #  typical location: ${ALLUXIO_HOME}/conf/alluxio-site.properties
        file_name = os.path.basename(abs_file_path)
        return file_name == "alluxio-site.properties"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith((".enabled", ".used")):
            return ConfigType.BOOLEAN

        if option_name.endswith((".version")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith(
            (
                ".threshold",
                ".interval",
                ".timeout",
                ".time",
                ".frequency",
                ".delay",
                ".age",
                ".sleep",
                ".duration",
                ".wait",
                ".period",
                ".seconds",
            )
        ):
            return ConfigType.TIME

        if option_name.endswith(
            (
                ".name",
                ".hostname",
                ".home",
                ".classname",
                ".namespace",
                ".alias",
                ".class",
            )
        ):
            return ConfigType.NAME

        if option_name.endswith(
            (
                ".path",
                ".dir",
                ".file",
                ".dirs",
                ".keyfile",
                ".keyring",
                ".directory",
                ".tmp",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith(
            (
                ".max",
                ".threads",
                ".count",
                ".capacity",
                ".number",
                ".length",
                ".retry",
                ".entries",
                ".ratio",
                ".factor",
                ".range",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith((".level", ".mode", ".type")):
            return ConfigType.TYPE

        if option_name.endswith((".port")):
            return ConfigType.PORT

        if option_name.endswith((".host")):
            return ConfigType.IP_ADDRESS

        if option_name.endswith((".size", ".limit", ".bytes", ".mem")):
            return ConfigType.SIZE

        if option_name.endswith((".auth.id", ".uid", ".client.id", ".app.id")):
            return ConfigType.ID

        if option_name.endswith((".password")):
            return ConfigType.PASSWORD

        if option_name.endswith((".user", ".username")):
            return ConfigType.USERNAME

        return super().get_config_type(option_name, value)
