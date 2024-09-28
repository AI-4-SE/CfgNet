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

from cfgnet.plugins.concept.hadoop_hbase_plugin import HadoopHbasePlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = HadoopHbasePlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    hadoop_hbase_file = plugin.is_responsible("tests/files/hbase-site.xml")
    hadoop_hbase_default_file = plugin.is_responsible("tests/files/hbase-default.xml")
    not_hadoop_hbase_file = plugin.is_responsible("tests/files/core-site.xml")

    assert hadoop_hbase_file
    assert hadoop_hbase_default_file
    assert not not_hadoop_hbase_file


def test_parse_hadoop_hbase_file(get_plugin):
    plugin = get_plugin
    hadoop_hbase_file = os.path.abspath("tests/files/hbase-site.xml")
    artifact = plugin.parse_file(hadoop_hbase_file, "hbase-site.xml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 9

    assert make_id("hbase-site.xml", "file", "hbase-site.xml") in ids
    assert make_id("hbase-site.xml", "configuration", "property", "hbase.rootdir", "value", "hdfs://namenode.example.com:9000/hbase") in ids
    assert make_id("hbase-site.xml", "configuration", "property", "hbase.rootdir", "description", "The directory shared by region servers and master where HBase stores data in HDFS.") in ids

    assert make_id("hbase-site.xml", "configuration", "property", "hbase.master.port", "value", "16000") in ids
    assert make_id("hbase-site.xml", "configuration", "property", "hbase.master.port", "description", "The port for the HBase master.") in ids

    assert make_id("hbase-site.xml", "configuration", "property", "hbase.regionserver.global.memstore.upperLimit", "value", "0.4") in ids
    assert make_id("hbase-site.xml", "configuration", "property", "hbase.regionserver.global.memstore.upperLimit", "description", "Maximum heap size a RegionServer's MemStore can use (40% in this case).") in ids

    assert make_id("hbase-site.xml", "configuration", "property", "hbase.client.pause", "value", "100") in ids
    assert make_id("hbase-site.xml", "configuration", "property", "hbase.client.pause", "description", "Time between client retries, in milliseconds.") in ids
    

def test_config_types(get_plugin):
    plugin = get_plugin
    hadoop_hbase_file = os.path.abspath("tests/files/hbase-site.xml")
    artifact = plugin.parse_file(hadoop_hbase_file, "hbase-site.xml")
    nodes = artifact.get_nodes()

    port_node = next(filter(lambda x: x.id == make_id("hbase-site.xml", "configuration", "property", "hbase.master.port", "value", "16000",), nodes))
    path_node = next(filter(lambda x: x.id == make_id("hbase-site.xml", "configuration", "property", "hbase.rootdir", "value", "hdfs://namenode.example.com:9000/hbase"), nodes))

    assert port_node.config_type == ConfigType.PORT
    assert path_node.config_type == ConfigType.PATH
