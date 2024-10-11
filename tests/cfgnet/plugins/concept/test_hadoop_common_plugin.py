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

from cfgnet.plugins.concept.hadoop_common_plugin import HadoopCommonPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = HadoopCommonPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    hadoop_common_file = plugin.is_responsible("tests/files/core-site.xml")
    not_hadoop_common_file = plugin.is_responsible("tests/files/test.xml")

    assert hadoop_common_file
    assert not not_hadoop_common_file


def test_parse_hadoop_common_file(get_plugin):
    plugin = get_plugin
    hadoop_common_file = os.path.abspath("tests/files/core-site.xml")
    artifact = plugin.parse_file(hadoop_common_file, "core-site.xml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 5

    assert make_id("core-site.xml", "file", "core-site.xml") in ids
    assert make_id("core-site.xml", "configuration", "property", "fs.defaultFS", "value", "hdfs://namenode.example.com:9000") in ids
    assert make_id("core-site.xml", "configuration", "property", "hadoop.tmp.dir", "value", "/var/lib/hadoop/tmp") in ids
    assert make_id("core-site.xml", "configuration", "property", "io.file.buffer.size", "value", "131072") in ids
    assert make_id("core-site.xml", "configuration", "property", "ipc.client.connect.timeout", "value", "30000") in ids


def test_config_types(get_plugin):
    plugin = get_plugin
    hadoop_common_file = os.path.abspath("tests/files/core-site.xml")
    artifact = plugin.parse_file(hadoop_common_file, "core-site.xml")
    nodes = artifact.get_nodes()

    path_node = next(filter(lambda x: x.id == make_id("core-site.xml", "configuration", "property", "hadoop.tmp.dir", "value", "/var/lib/hadoop/tmp",), nodes))
    size_node = next(filter(lambda x: x.id == make_id("core-site.xml", "configuration", "property", "io.file.buffer.size", "value", "131072"), nodes))
    time_node = next(filter(lambda x: x.id == make_id("core-site.xml", "configuration", "property", "ipc.client.connect.timeout", "value", "30000"), nodes))

    assert path_node.config_type == ConfigType.PATH
    assert size_node.config_type == ConfigType.SIZE
    assert time_node.config_type == ConfigType.TIME
