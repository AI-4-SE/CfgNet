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

    assert len(cfg.all_cfgs) == 9


def test_compute_values():
    with open("tests/files/cfg.py", "r", encoding="utf-8") as source:
        code_str = source.read()

    cfg = Cfg(code_str=code_str)

    a = cfg.compute_values("a")
    x = cfg.compute_values("x")
    z = cfg.compute_values("z")
    i = cfg.compute_values("i")
    j = cfg.compute_values("j")
    s = cfg.compute_values("s")
    solver = cfg.compute_values("solver")
    anchors = cfg.compute_values("anchors")
    kwargs = cfg.compute_values("**kwargs")
    n_neighbors = cfg.compute_values("n_neighbors")
    preprocessing = cfg.compute_values("preprocessing")
    value = cfg.compute_values("value")
    tuple_var_k = cfg.compute_values("k")
    tuple_var_p = cfg.compute_values("p")
    # values_selfx = cfg.compute_values("self.x") #-> https://github.com/SMAT-Lab/Scalpel/issues/39

    assert len(a) == 7
    assert len(x) == 1
    assert x[('x', 12)][0] == '5'
    assert x[('x', 12)][1] == 'Method Argument'

    assert len(z) == 3
    assert z[('z', 21)][0] == "'test'"

    assert len(i) == 1
    assert i[('i', 43)][0] == "i in range(3)"
    assert i[('i', 43)][1] == 'Call'

    assert len(j) == 1
    assert j[('j', 46)][0] == "j in range(1, 5)"
    assert j[('j', 46)][1] == "Call"

    assert len(s) == 1
    assert s[('s', 49)][0] == "s in range(1, 10, 2)"
    assert s[('s', 49)][1] == "Call"

    assert len(solver) == 1
    assert solver[('solver', 53)][0] == "'lbfgs'"
    assert solver[('solver', 53)][1] == "Method Argument"

    assert len(anchors) == 3
    assert anchors[('anchors', 60)][0] == '[x for x in range(3)]'
    assert anchors[('anchors', 60)][1] == 'ListComp'

    assert len(kwargs) == 1
    assert kwargs[('kwargs', 64)][0] == "{'min_samples_leaf': 1, 'max_leaf_nodes': 2}"

    assert len(n_neighbors) == 1
    assert n_neighbors[('n_neighbors', 70)][0] == "n_neighbors"
    assert n_neighbors[('n_neighbors', 70)][1] == "Method Argument"

    assert len(preprocessing) == 1
    assert preprocessing[('preprocessing', 84)][0] == "preprocessing"
    assert preprocessing[('preprocessing', 84)][1] == "Call"

    assert len(value) == 1
    assert value[('value', 80)][0] == "value in enumerate(C_range)"
    assert value[('value', 80)][1] == "Call"

    assert len(tuple_var_k) == 1
    assert tuple_var_k[('k', 8)][0] == "1"
    assert tuple_var_k[('k', 8)][1] == "int"

    assert len(tuple_var_p) == 1
    assert tuple_var_p[('p', 8)][0] == "2"
    assert tuple_var_p[('p', 8)][1] == "int"

    # assert len(values_selfx) == 2
