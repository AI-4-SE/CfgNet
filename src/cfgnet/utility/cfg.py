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
import logging
import ast
from typing import Callable, Dict, List, Any
from scalpel.cfg import CFGBuilder, CFG
from scalpel.SSA.const import SSA


class Cfg:
    """Control flow graph module."""

    def __init__(self, code_str: str) -> None:
        self.code_str = code_str
        self.cfg: CFG = CFGBuilder().build_from_src(name="", src=code_str)
        self.ssa: SSA = SSA()
        self.all_cfgs: List[CFG] = []
        self._traverse(self.cfg, self._add_cfg)

    def _traverse(self, current_cfg: CFG, callback: Callable) -> None:
        """
        Traverse the control flow graph.

        :param current: Starting point of traversal
        :param callback: Callback called on every visited cfg
        :return: None
        """
        callback(current_cfg)

        for _, fun_cfg in current_cfg.functioncfgs.items():
            if fun_cfg is not None:
                self._traverse(fun_cfg, callback)

        for _, class_cfg in current_cfg.class_cfgs.items():
            if class_cfg is not None:
                self._traverse(class_cfg, callback)

    def _add_cfg(self, cfg: CFG):
        """
        Add cfg object to the list of all cfgs.

        :param cfg: Cfg object
        """
        self.all_cfgs.append(cfg)

    # pylint: disable=broad-except
    def compute_values(self, var: str) -> Dict:
        """
        Compute all possible values of a variable.

        :param var: variable for which all values should be identified
        :return: dictionary of possible values
        """
        if var.startswith("**"):
            var = var[2:]

        value_dict: Dict = {}
        try:
            for cfg in self.all_cfgs:
                self.get_values_from_ssa(
                    cfg=cfg, var=var, value_dict=value_dict
                )

            self.get_values_from_func_calls(var=var, value_dict=value_dict)
            return value_dict
        except Exception as error:
            logging.error(
                "Data flow analysis failed. Couldn't compute values for %s due to %s: %s",
                var,
                type(error).__name__,
                error,
            )
            return value_dict

    def get_values_from_ssa(
        self, cfg: CFG, var: str, value_dict: Dict
    ) -> None:
        _, const_dict = self.ssa.compute_SSA(cfg)
        for name, value in const_dict.items():
            val: Any = None
            if not value:
                continue
            if name[0] == var:
                if not hasattr(value, "lineno"):
                    key = (var, None)
                else:
                    key = (var, value.lineno)

                if isinstance(value, ast.Call):
                    if isinstance(value.func, ast.Name):
                        if value.func.id == "range":
                            val = self.parse_range_call(value)
                        else:
                            val = ast.unparse(value)

                if not val:
                    val = ast.unparse(value)

                val_type = str(type(value))
                val_type = val_type[12:-2]

                value_dict[key] = (val, val_type)

    def get_values_from_func_calls(self, var: str, value_dict: Dict) -> None:
        for node in ast.walk(ast.parse(self.code_str)):
            if isinstance(node, ast.FunctionDef):
                args = ast.unparse(node.args).split(",")
                parsed_args = map(lambda arg: arg.strip(), args)
                for arg in parsed_args:
                    arg_parts = arg.split("=")
                    if len(arg_parts) == 2:
                        if arg_parts[0] == var:
                            if not hasattr(node, "lineno"):
                                key: Any = (var, None)
                            else:
                                key = (var, node.lineno)
                            value_dict[key] = (arg_parts[1], "MethodArgument")

    @staticmethod
    def parse_range_call(node: ast.Call) -> Any:
        """
        Parse range call.

        :param: ast node of range()
        :return: list of range values
        """
        values = [
            arg.value for arg in node.args if isinstance(arg, ast.Constant)
        ]

        if all(isinstance(arg, ast.Constant) for arg in node.args):
            if len(node.args) == 1:
                return list(range(values[0]))
            if len(node.args) == 2:
                return list(range(values[0], values[1]))
            if len(node.args) == 3:
                return list(range(values[0], values[1], values[2]))

        return ast.unparse(node)
