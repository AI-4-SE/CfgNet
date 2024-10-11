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
from cfgnet.plugins.file_type.json_plugin import JsonPlugin
from cfgnet.config_types.config_types import ConfigType


class NodejsPlugin(JsonPlugin):
    def __init__(self):
        super().__init__("nodejs")
        self.excluded_keys = [
            "keywords",
            "description",
            "author",
            "contributors",
        ]

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith("package.json"):
            return True
        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name in (
            "version",
            "dependencies",
            "devDependencies",
            "peerDependencies",
            "optionalDependencies",
            "engines",
        ):
            return ConfigType.VERSION_NUMBER
        if option_name in (
            "main",
            "files",
            "man",
            "directories",
            "workspaces",
        ):
            return ConfigType.PATH
        if option_name in ("scripts", "bin"):
            return ConfigType.COMMAND
        if option_name in ("name", "bundledDependencies"):
            return ConfigType.NAME
        if option_name == "url":
            return ConfigType.URL
        if option_name == "email":
            return ConfigType.EMAIL
        if option_name in ("repository", "funding", "type"):
            return ConfigType.UNKNOWN
        if option_name == "license":
            return ConfigType.LICENSE
        if option_name == "private":
            return ConfigType.BOOLEAN
        return super().get_config_type(option_name, value)
