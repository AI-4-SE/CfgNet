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

import os

import pytest

from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = YAMLPlugin()
    return plugin


def test_is_responsible(get_plugin):
    yaml_plugin = get_plugin
    yaml_file = os.path.abspath("tests/files/test.yaml")
    yml_file = "test.yml"
    no_yaml_file = os.path.abspath("tests/files/Dockerfile")

    yaml_file_result = yaml_plugin.is_responsible(yaml_file)
    yml_file_result = yaml_plugin.is_responsible(yml_file)
    no_yaml_file_result = yaml_plugin.is_responsible(no_yaml_file)

    assert yaml_file_result
    assert yml_file_result
    assert not no_yaml_file_result


def test_parse_yaml_file(get_plugin):
    yaml_plugin = get_plugin
    yaml_file = os.path.abspath("tests/files/test.yaml")

    artifact = yaml_plugin.parse_file(yaml_file, "test.yaml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 9
    assert make_id("test.yaml", "file", "test.yaml") in ids
    assert make_id("test.yaml", "test.yaml_0", "name", "Port") in ids
    assert make_id("test.yaml", "test.yaml_0", "args", "number", "8000") in ids
    assert make_id("test.yaml", "test.yaml_0", "register", "Port") in ids
    assert make_id("test.yaml", "test.yaml_1", "name", "Test") in ids
    assert make_id("test.yaml", "test.yaml_1", "ignore_errors", "true") in ids
    assert (
        make_id("test.yaml", "test.yaml_1", "copy", "src", "./tmp.sh") in ids
    )
    assert (
        make_id("test.yaml", "test.yaml_1", "copy", "dest", "./tmp.sh") in ids
    )
    assert make_id("test.yaml", "test.yaml_2", "runs-on", "matrix.os") in ids
