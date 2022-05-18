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
import ast
import os
import re
from typing import List, Dict

from cfgnet.network.nodes import OptionNode, ValueNode
from cfgnet.plugins.source_code.ml_plugin import MLPlugin


class PytorchPLugin(MLPlugin):
    modules_file = os.path.join(
        os.path.dirname(__file__), "modules", "pytorch.json"
    )
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

    def parse_arguments(
        self, args: List, parent: OptionNode, module: Dict
    ) -> None:
        params = module["params"]
        if params:
            if len(params) == 1:
                if params[0].startswith("*") or params[0].startswith("**"):
                    option = OptionNode(
                        name=params[0], location=parent.location
                    )
                    parent.add_child(option)
                    for arg in args:
                        value_name = ast.unparse(arg)
                        if value_name.startswith("'") and value_name.endswith(
                            "'"
                        ):
                            value_name = value_name.replace("'", "")
                        value = ValueNode(name=value_name)
                        option.add_child(value)

            else:
                super().parse_arguments(args, parent, module)
