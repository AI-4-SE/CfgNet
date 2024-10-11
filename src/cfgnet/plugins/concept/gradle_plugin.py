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


class GradlePlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("gradle")

    def is_responsible(self, abs_file_path):
        file_name = os.path.basename(abs_file_path)
        return file_name == "gradle.properties"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:

        if option_name.endswith((".home", ".projectcachedir")):
            return ConfigType.PATH

        if option_name.endswith(("max")):
            return ConfigType.NUMBER

        if option_name.endswith(".idletimeout"):
            return ConfigType.TIME

        if option_name.endswith(".worker.max"):
            return ConfigType.NUMBER

        if option_name.endswith(
            (
                ".caching",
                ".debug",
                ".configuration-cache",
                "configureondemand",
                ".daemon",
                ".isolated-projects",
                ".verbose",
                ".watch",
            )
        ):
            return ConfigType.BOOLEAN

        if option_name.endswith((".console", ".level", ".priority", ".mode")):
            return ConfigType.TYPE

        return super().get_config_type(option_name, value)
