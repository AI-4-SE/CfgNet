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
from cfgnet.plugins.file_type.toml_plugin import TomlPlugin
from cfgnet.config_types.config_types import ConfigType


class CargoPlugin(TomlPlugin):
    def __init__(self):
        super().__init__("cargo")
        self.excluded_keys = [
            "description",
            "authors",
            "maintainers",
            "readme",
            "keywords",
            "classifiers",
        ]

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith("Cargo.toml"):
            return True
        return False

    @staticmethod
    def get_config_type(option_name: str) -> ConfigType:
        """
        Find config type based on option name.

        :param option_name: name of option
        :return: config type
        """
        if option_name in (
            "homepage",
            "repository",
            "documentation",
            "urls",
            "url",
        ):
            return ConfigType.URL
        if option_name in ("include", "exclude"):
            return ConfigType.PATH
        if option_name in ("version", "dependencies", "dev-dependencies"):
            return ConfigType.VERSION_NUMBER
        return ConfigType.UNKNOWN
