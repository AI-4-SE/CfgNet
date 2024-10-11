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
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin
from cfgnet.config_types.config_types import ConfigType


class MongoDBPlugin(YAMLPlugin):
    def __init__(self):
        super().__init__("mongodb")

    def is_responsible(self, abs_file_path) -> bool:
        if abs_file_path.endswith("mongod.conf"):
            return True
        return False

    # pylint: disable=unused-argument,too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()
        if option_name.endswith(
            (
                "verbosity",
                "connections",
                "level",
                "retries",
                "interval",
                "intervalms",
                "secs",
                "hours",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith("bindip"):
            return ConfigType.IP_ADDRESS

        if option_name.endswith(
            (
                "thresholdss",
                "timeoutms",
                "seconds",
            )
        ):
            return ConfigType.TIME

        if option_name.endswith(
            (
                "sizemb",
                "sizegb",
            )
        ):
            return ConfigType.SIZE

        if option_name.endswith(
            ("path", "destination", "timezoneinfo", "pathprefix", "file")
        ):
            return ConfigType.PATH

        if option_name.endswith("format"):
            return ConfigType.TYPE

        if option_name.endswith("keyidentifier"):
            return ConfigType.ID

        if option_name.endswith(("name", "configdb")):
            return ConfigType.NAME

        return super().get_config_type(option_name, value)
