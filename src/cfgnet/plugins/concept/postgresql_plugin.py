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


class PostgreSQLPlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("postgresql")

    def is_responsible(self, abs_file_path) -> bool:
        if abs_file_path.endswith("postgresql.conf"):
            return True
        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(("_name", "_names", "_hostname")):
            return ConfigType.NAME

        if option_name.endswith("_addresses"):
            return ConfigType.IP_ADDRESS

        if option_name.endswith(
            (
                "_connections",
                "_iterations",
                "_permissions",
                "_count",
                "_buffers",
                "_transactions",
                "_depth",
                "_pages",
                "_concurrency",
                "_workers",
                "_senders",
                "_slots",
                "_subscription",
                "_cost",
                "_threshold",
                "_seed",
                "_generations",
                "_fraction",
                "_rate",
                "_length",
                "_factor",
                "_age",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith(
            (
                "_timeout",
                "_interval",
                "_delay",
                "_time",
                "_timestamp",
                "_duration",
            )
        ):
            return ConfigType.TIME

        if option_name.endswith(
            (
                "_file",
                "_files",
                "_dir",
                "_directories",
                "_keyfile",
                "_directory",
                "_destination",
                "_path",
                "_filename",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith(("_version", "_version_num")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith("_command"):
            return ConfigType.COMMAND

        if option_name.endswith(("_size", "_mem", "_limit", "_memory")):
            return ConfigType.SIZE

        if option_name.endswith(("_type", "_level")):
            return ConfigType.TYPE

        if option_name.endswith(("_xid", "_ident", "_id")):
            return ConfigType.ID

        if option_name.endswith("port"):
            return ConfigType.PORT

        return super().get_config_type(option_name, value)
