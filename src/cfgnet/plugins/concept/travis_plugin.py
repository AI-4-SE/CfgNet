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

from yaml.nodes import MappingNode, ScalarNode

from cfgnet.network.nodes import OptionNode
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin
from cfgnet.config_types.config_types import ConfigType


class TravisPlugin(YAMLPlugin):
    def __init__(self):
        super().__init__("travis")

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith(".travis.yml"):
            return True
        return False

    def _parse_sequence_node(self, node, parent):
        for child in node.value:
            if isinstance(child, MappingNode):
                virtual_option = TravisPlugin._create_virtual_option(child)

                if virtual_option:
                    parent.add_child(virtual_option)
                    self._iter_tree(child, virtual_option)
            else:
                self._iter_tree(child, parent)

    @staticmethod
    def _create_virtual_option(node):
        key = node.value[0]
        if isinstance(key, tuple):
            if isinstance(key[0], ScalarNode) and isinstance(
                key[1], ScalarNode
            ):
                option_name = key[0].value + "/" + key[1].value
                virtual_option = OptionNode(
                    name=option_name, location=key[0].start_mark.line + 1
                )
                return virtual_option

        return None

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name in (
            "before_install",
            "before_script",
            "script",
            "before_script",
            "install",
            "before_cache",
            "after_success",
            "after_failure",
            "before_deploy",
            "after_deploy",
            "after_script",
        ):
            return ConfigType.COMMAND

        if option_name in ("submodules", "quiet", "lfs_skip_smudge"):
            return ConfigType.BOOLEAN

        if option_name == "hosts":
            return ConfigType.URL

        if option_name in ("os", "arch"):
            return ConfigType.PLATFORM

        if option_name in ("name", "services", "hostname", "dist", "compiler"):
            return ConfigType.NAME

        if option_name == "env":
            return ConfigType.ENVIRONMENT

        if any(
            x in option_name
            for x in ["file", "File", "FILE", "folder", "FOLDER"]
        ):
            return ConfigType.PATH

        if option_name == "depth":
            return ConfigType.NUMBER

        if option_name in (
            "version",
            "firefox",
            "mariadb",
            "postgresql",
            "rethinkdb",
        ):
            return ConfigType.VERSION_NUMBER

        return super().get_config_type(option_name, value)
