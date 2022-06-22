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
from typing import Dict, List
from cfgnet.plugins.source_code.ml_plugin import MLPlugin
from cfgnet.network.nodes import OptionNode, ValueNode


class SklearnPlugin(MLPlugin):
    modules_file = os.path.join(
        os.path.dirname(__file__), "modules", "sklearn.json"
    )

    def __init__(self):
        super().__init__("sklearn")

    def parse_arguments(
        self, args: List, parent: OptionNode, module: Dict
    ) -> None:
        params = module["params"]
        if params:
            if params[0] == "*arrays":
                count = 0
                for arg in args:
                    option = OptionNode(
                        name=f"*arrays_{str(count)}", location=str(arg.lineno)
                    )
                    parent.add_child(option)
                    value = ValueNode(name=ast.unparse(arg))
                    option.add_child(value)
                    count += 1
            else:
                super().parse_arguments(args, parent, module)
