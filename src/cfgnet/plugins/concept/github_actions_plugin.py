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
import re
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin
from cfgnet.config_types.config_types import ConfigType


class GitHubActionPlugin(YAMLPlugin):
    file_name = re.compile(r".*?\.github\/workflows\/[^\/]*\.yml$")

    def __init__(self):
        super().__init__("github-action")

    def is_responsible(self, abs_file_path):
        if self.file_name.search(abs_file_path):
            return True
        return False

    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name in ("run"):
            return ConfigType.COMMAND

        if option_name in ("name", "uses"):
            return ConfigType.NAME

        if option_name in ("python-version"):
            return ConfigType.VERSION_NUMBER

        return super().get_config_type(option_name, value)
