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
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin


class AnsiblePlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("ansible")

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith("ansible.cfg"):
            return True
        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(
            (
                "_path",
                "_home",
                "_file",
                "_paths",
                "_output",
                "_local_tmp",
                "_dir",
                "_root",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith(("_interval", "_timeout")):
            return ConfigType.TIME

        if option_name.endswith(("_executable")):
            return ConfigType.COMMAND

        if option_name.endswith(("_name")):
            return ConfigType.NAME

        if option_name.endswith(("_port")):
            return ConfigType.PORT

        if option_name.endswith(("_user")):
            return ConfigType.USERNAME

        if option_name.endswith(("_identity")):
            return ConfigType.ID

        if option_name.endswith(("_url")):
            return ConfigType.URL

        if option_name.endswith(("_count")):
            return ConfigType.NUMBER

        if option_name.endswith(("_enabled")):
            return ConfigType.BOOLEAN

        return super().get_config_type(option_name, value)
