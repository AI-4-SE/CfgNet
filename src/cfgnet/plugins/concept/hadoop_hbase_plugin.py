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
from cfgnet.plugins.file_type.hadoop_plugin import HadoopPlugin


class HadoopHbasePlugin(HadoopPlugin):
    def __init__(self):
        super().__init__("hadoop-hbase")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return any(
            file_name == name
            for name in ["hbase-site.xml", "hbase-default.xml"]
        )
