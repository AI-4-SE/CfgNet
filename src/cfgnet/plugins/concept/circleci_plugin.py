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


class CircleCiPlugin(YAMLPlugin):
    def __init__(self):
        super().__init__("circleci")

    def is_responsible(self, abs_file_path):
        return abs_file_path.endswith(".circleci/config.yml")

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name in ("command", "run", "shell", "entrypoint"):
            return ConfigType.COMMAND

        if option_name == "image":
            return ConfigType.IMAGE

        if option_name in ("parallelism"):
            return ConfigType.NUMBER

        if option_name in (
            "at",
            "working_directory",
            "path",
            "paths",
            "destination",
        ):
            return ConfigType.PATH

        if option_name in ("name", "resource_class"):
            return ConfigType.NAME

        if option_name == "user":
            return ConfigType.USERNAME

        if option_name == "environment":
            return ConfigType.ENVIRONMENT

        if option_name in ("xcode", "version"):
            return ConfigType.VERSION_NUMBER

        if option_name in ("docker_layer_caching", "background"):
            return ConfigType.BOOLEAN

        if option_name in ("no_output_timeout"):
            return ConfigType.TIME

        return super().get_config_type(option_name, value)
