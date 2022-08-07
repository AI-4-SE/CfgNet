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
import logging

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
                    value = ValueNode(
                        name=ast.unparse(arg),
                        value_type=MLPlugin.get_value_type(arg),
                    )
                    option.add_child(value)
                    count += 1
            else:
                super().parse_arguments(args, parent, module)

    def parse_keywords(self, keywords: List, parent: OptionNode) -> None:
        """
        Extract all parameters and their values and create corresponding nodes.

        :param keywords: list of parameters
        :param parent: parent option node
        """
        if len(keywords) == 1:
            key = ast.unparse(keywords[0])
            if key.startswith("**"):
                item_dict = None
                try:
                    values = self.cfg.compute_values(key[2:])
                    for key, item in values.items():
                        item_dict = ast.literal_eval(item[0])
                        if isinstance(item_dict, Dict):
                            break
                except (ValueError, TypeError, SyntaxError):
                    logging.warning("Failed to parse **kwargs variable.")
                finally:
                    if item_dict:
                        for key, value in item_dict.items():
                            option = OptionNode(
                                name=key, location=str(parent.location)
                            )
                            parent.add_child(option)
                            value = ValueNode(
                                name=value,
                                value_type=MLPlugin.get_value_type(value),
                            )
                            option.add_child(value)
                    else:
                        option = OptionNode(
                            name="**kwargs", location=str(parent.location)
                        )
                        parent.add_child(option)
                        value = ValueNode(name=key[0], value_type="kwargs")
                        option.add_child(value)
            else:
                super().parse_keywords(keywords, parent)
        else:
            super().parse_keywords(keywords, parent)
