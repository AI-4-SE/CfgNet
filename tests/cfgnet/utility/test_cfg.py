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


def test_number_cfgs():
    with open("tests/files/cfg.py", "r", encoding="utf-8") as source:
        code_str = source.read()

    cfg = Cfg(code_str=code_str)

    assert len(cfg.all_cfgs) == 6


def test_compute_values():
    with open("tests/files/cfg.py", "r", encoding="utf-8") as source:
        code_str = source.read()

    cfg = Cfg(code_str=code_str)

    values_a = cfg.compute_values("a")
    values_x = cfg.compute_values("x")
    values_z = cfg.compute_values("z")
    values_i = cfg.compute_values("i")
    values_j = cfg.compute_values("j")
    values_c = cfg.compute_values("c")
    # values_selfx = cfg.compute_values("self.x") -> https://github.com/SMAT-Lab/Scalpel/issues/39
    # values_k = cfg.compute_values("k") -> https://github.com/SMAT-Lab/Scalpel/issues/42
    # values_p = cfg.compute_values("p") -> https://github.com/SMAT-Lab/Scalpel/issues/42

    print(values_i)

    assert len(values_a) == 5
    assert len(values_x) == 1

    assert len(values_z) == 2
    assert values_z[('z', 19)] == "'hello'"

    assert len(values_i) == 1
    assert values_i[('i', 44)] == [0, 1, 2]

    assert len(values_j) == 1
    assert values_j[('j', 47)] == [1, 2, 3, 4]

    assert len(values_c) == 1
    assert values_c[('c', 50)] == [1, 3, 5, 7, 9]

    # assert len(values_selfx) == 2
    # assert len(values_k) == 1
    # assert len(values_p) == 1
