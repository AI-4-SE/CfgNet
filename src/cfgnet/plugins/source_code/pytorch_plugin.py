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
import re
from cfgnet.plugins.plugin import Plugin


class PytorchPLugin(Plugin):
    import_regex = re.compile(r"import torch")
    import_from_regex = re.compile(r"from torch[a-zA-z._]* import [a-zA-Z_]*")

    def __init__(self):
        super().__init__("pytorch")

    def is_responsible(self, abs_file_path):
        file_name = os.path.basename(abs_file_path)

        if not file_name.endswith(".py"):
            return False

        with open(abs_file_path, "r", encoding="utf-8") as source:
            for line in source.readlines():
                if self.import_regex.search(line):
                    return True
                if self.import_from_regex.search(line):
                    return True

        return False


    