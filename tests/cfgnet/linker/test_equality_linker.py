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

from cfgnet.linker.equality_linker import EqualityLinker
from cfgnet.config_types.config_types import ConfigType
from cfgnet.network.nodes import OptionNode, ValueNode


def test_check_config_types():
    linker = EqualityLinker()

    option_port_a = OptionNode("port_a", "1", ConfigType.PORT)
    port_a = ValueNode(name="8000")
    option_port_a.add_child(port_a)

    option_port_b = OptionNode("port_b", "2", ConfigType.PORT)
    port_b = ValueNode(name="8000")
    option_port_b.add_child(port_b)

    option_unknown_a = OptionNode("unknown_a", "3", ConfigType.UNKNOWN)
    unknown_a = ValueNode(name="unknown")
    option_unknown_a.add_child(unknown_a)

    option_path = OptionNode("path", "4", ConfigType.PATH)
    path = ValueNode(name="path")
    option_path.add_child(path)

    same_type = linker._check_config_types(port_a, port_b)
    only_one_unknown = linker._check_config_types(port_a, unknown_a)
    different_types = linker._check_config_types(port_a, path)

    assert same_type
    assert not only_one_unknown
    assert not different_types
