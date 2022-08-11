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
import logging
from typing import List


class HpoPlugin:
    imports: List[str] = ["hyperopt", "optuna", "optunity", "ray", "talos"]

    @staticmethod
    def parse_file(abs_file_path: str) -> None:
        with open(abs_file_path, "r", encoding="utf-8") as source:
            code_str = source.read()
            tree = ast.parse(code_str)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for package in node.names:
                    module = package.name.split(".")[0]
                    if module in HpoPlugin.imports:
                        logging.info(
                            "%s is imported and probably used for parameter tuning",
                            module,
                        )

            if isinstance(node, ast.ImportFrom):
                for package in node.names:
                    if node.module:
                        module = node.module.split(".")[0]
                        if module in HpoPlugin.imports:
                            logging.info(
                                "%s is imported and probably used for parameter tuning",
                                module,
                            )
