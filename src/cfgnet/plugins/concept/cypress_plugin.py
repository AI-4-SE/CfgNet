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
from typing import List
from cfgnet.plugins.file_type.json_plugin import JsonPlugin
from cfgnet.config_types.config_types import ConfigType


class CypressPlugin(JsonPlugin):
    def __init__(self):
        super().__init__("cypress")
        self.excluded_keys: List[str] = []

    def is_responsible(self, abs_file_path: str) -> bool:
        if abs_file_path.endswith("cypress.json"):
            return True
        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:
        """
        Find config type based on option name.

        :param option_name: name of option
        :return: config type
        """
        if option_name == "projectId":
            return ConfigType.ID
        if any(x in option_name for x in ["Url", "url", "Hosts"]):
            return ConfigType.URL
        if option_name == "env":
            return ConfigType.ENVIRONMENT
        if option_name == "port":
            return ConfigType.PORT
        if option_name in (
            "includeShadowDom",
            "watchForFileChanges",
            "screenshotOnRunFailure",
            "trashAssetsBeforeRuns",
            "trashAssetsBeforeRuns",
            "video",
            "videoUploadOnPasses",
            "trashAssetsBeforeRuns",
            "chromeWebSecurity",
            "waitForAnimations",
            "toConsole",
        ):
            return ConfigType.BOOLEAN
        if any(x in option_name for x in ["Folder", "File", "Files"]):
            return ConfigType.PATH
        if option_name == "nodeVersion":
            return ConfigType.VERSION_NUMBER
        if option_name in (
            "defaultCommandTimeout",
            "execTimeout",
            "taskTimeout",
            "pageLoadTimeout",
            "requestTimeout",
            "responseTimeout",
            "slowTestThreshold",
        ):
            return ConfigType.TIME

        if option_name == "env":
            return ConfigType.ENVIRONMENT
        if option_name in (
            "numTestsKeptInMemory",
            "redirectionLimit",
            "videoCompression",
            "animationDistanceThreshold",
        ):
            return ConfigType.NUMBER

        if option_name in ("runMode", "openMode"):
            return ConfigType.MODE

        if option_name in ("reporter", "devServer"):
            return ConfigType.NAME

        if option_name in ("viewportHeight", "viewportWidth"):
            return ConfigType.SIZE

        if option_name in ("specPattern", "excludeSpecPattern"):
            return ConfigType.PATTERN

        return ConfigType.UNKNOWN
