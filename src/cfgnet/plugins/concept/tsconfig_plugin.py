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


class TsconfigPlugin(JsonPlugin):
    def __init__(self):
        super().__init__("tsconfig")
        self.excluded_keys = []

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith("tsconfig.json"):
            return True
        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name in (
            "files",
            "outFile",
            "include",
            "exclude",
            "extends",
            "baseUrl",
            "paths",
            "rootDir",
            "rootDirs",
            "typeRoots",
            "mapRoot",
        ):
            return ConfigType.PATH

        if option_name in (
            "noImplicitAny",
            "removeComments",
            "preserveConstEnums",
            "sourceMap",
            "allowJs",
            "strictNullChecks",
            "allowUnreachableCode",
            "allowUnusedLabels",
            "emitBOM",
            "noEmitOnError",
            "preserveConstEnums",
            "removeComments"
            "allowJs"
            "disableSizeLimit"
            "allowSyntheticDefaultImports",
        ):
            return ConfigType.BOOLEAN

        if option_name == "types":
            return ConfigType.NAME

        return super().get_config_type(option_name, value)
