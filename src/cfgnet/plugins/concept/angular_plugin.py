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
from cfgnet.plugins.file_type.json_plugin import JsonPlugin
from cfgnet.config_types.config_types import ConfigType


class AngularPlugin(JsonPlugin):
    def __init__(self):
        super().__init__("angular")
        self.excluded_keys = [
            "keywords",
            "description",
            "author",
            "contributors",
        ]

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return file_name == "angular.json"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:
        """
        Find config type based on option name.

        :param option_name: name of option
        :return: config type
        """
        if option_name in ("version"):
            return ConfigType.VERSION_NUMBER
        if option_name in (
            "main",
            "sourceRoot",
            "replace",
            "with",
            "root",
            "$schema",
        ):
            return ConfigType.PATH
        if option_name in ("scripts", "bin"):
            return ConfigType.COMMAND
        if option_name in (
            "name",
            "bundledDependencies",
            "newProjectRoot",
            "projectType",
        ):
            return ConfigType.NAME
        return ConfigType.UNKNOWN