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
from cfgnet.utility.cfg import Cfg


def test_compute_values():
    with open("tests/files/cfg.py", "r", encoding="utf-8") as source:
        code_str = source.read()

    cfg = Cfg(code_str=code_str)

    values_a = cfg.compute_values("a")
    values_x = cfg.compute_values("x")
    values_i = cfg.compute_values("i")

    assert len(values_a) == 5
    assert len(values_x) == 1
    assert len(values_i) == 3
