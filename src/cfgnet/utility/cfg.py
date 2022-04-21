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
from typing import Dict
from scalpel.cfg import CFGBuilder
from scalpel.SSA.const import SSA


class Cfg:
    """Control flow graph module."""

    def __init__(self, code_str: str) -> None:
        self.cfg = CFGBuilder().build_from_src(name="", src=code_str)
        self.ssa = SSA()

    def compute_values(self, var: str) -> Dict:
        """
        Compute all possible values of a variable.

        :param var: variable for which all values should be identified
        """
        _, const_dict = self.ssa.compute_SSA(self.cfg)

        final_const_dict = {}

        for name, value in const_dict.items():
            if name[0] == var:
                final_const_dict[name] = ast.unparse(value)

        return final_const_dict
