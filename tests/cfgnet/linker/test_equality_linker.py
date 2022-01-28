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
from cfgnet.network.nodes import ValueNode


def test_check_config_types():
    linker = EqualityLinker()

    port_node_a = ValueNode(name="8000", config_type=ConfigType.PORT)
    port_node_b = ValueNode(name="8000", config_type=ConfigType.PORT)
    unknown_node_a = ValueNode(name="unknown", config_type=ConfigType.UNKNOWN)
    unknown_node_b = ValueNode(name="unknown", config_type=ConfigType.UNKNOWN)
    filepath_node = ValueNode(name="pom.xml", config_type=ConfigType.FILEPATH)
    path_node = ValueNode(name="path", config_type=ConfigType.PATH)

    same_type = linker._check_config_types(port_node_a, port_node_b)
    only_one_unknown = linker._check_config_types(port_node_a, unknown_node_a)
    both_unknown = linker._check_config_types(unknown_node_a, unknown_node_b)
    path_type = linker._check_config_types(path_node, filepath_node)
    different_types = linker._check_config_types(port_node_a, filepath_node)

    assert same_type
    assert only_one_unknown
    assert both_unknown
    assert path_type
    assert not different_types
