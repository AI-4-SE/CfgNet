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


class PoetryPlugin(TomlPlugin):
    def __init__(self):
        super().__init__("poetry")
        self.excluded_keys = [
            "description",
            "authors",
            "maintainers",
            "readme",
            "keywords",
            "classifiers",
        ]

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith("pyproject.toml"):
            return True
        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name == "name":
            return ConfigType.NAME
        if option_name == "license":
            return ConfigType.LICENSE
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
        if option_name == "scripts":
            return ConfigType.COMMAND
        return super().get_config_type(option_name, value)
