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
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin


class AnsiblePlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("ansible")

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith("ansible.cfg"):
            return True
        return False