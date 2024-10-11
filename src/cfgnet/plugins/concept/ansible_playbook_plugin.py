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


class AnsiblePlaybookPlugin(YAMLPlugin):
    def __init__(self):
        super().__init__("ansible-playbook")

    def is_responsible(self, abs_file_path) -> bool:
        if abs_file_path.endswith(
            ("site.yml", "playbook.yml", "site.yaml", "playbook.yaml")
        ):
            return True

        if "playbooks/" in abs_file_path and abs_file_path.endswith(
            (".yml", ".yaml")
        ):
            return True

        return False

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:

        if option_name.endswith("user"):
            return ConfigType.USERNAME

        if option_name.endswith("password"):
            return ConfigType.PASSWORD

        if option_name.endswith(
            ("register", "group", "master", "hosts", "name")
        ):
            return ConfigType.NAME

        if option_name.endswith(("local_action")):
            return ConfigType.COMMAND

        if option_name.endswith(("src", "dest", "path")):
            return ConfigType.PATH

        if option_name.endswith(("network", "gateway", "dns4")):
            return ConfigType.IP_ADDRESS

        return super().get_config_type(option_name, value)
