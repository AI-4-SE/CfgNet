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

from cfgnet.plugins.concept.hadoop_hdfs_plugin import HadoopHdfsPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = HadoopHdfsPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    hadoop_hdfs_file = plugin.is_responsible("tests/files/hdfs-site.xml")
    hadoop_hdfs_default_file = plugin.is_responsible("tests/files/hdfs-default.xml")
    not_hadoop_hdfs_file = plugin.is_responsible("tests/files/core-site.xml")

    assert hadoop_hdfs_file
    assert hadoop_hdfs_default_file
    assert not not_hadoop_hdfs_file


def test_parse_hadoop_hdfs_file(get_plugin):
    plugin = get_plugin
    hadoop_hdfs_file = os.path.abspath("tests/files/hdfs-site.xml")
    artifact = plugin.parse_file(hadoop_hdfs_file, "hdfs-site.xml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 9

    assert make_id("hdfs-site.xml", "file", "hdfs-site.xml") in ids
    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.replication", "value", "3") in ids
    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.replication", "description", "Default block replication. Number of copies of each block in HDFS.") in ids

    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.blocksize", "value", "134217728") in ids
    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.blocksize", "description", "Block size in bytes. Default is 128MB.") in ids

    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.namenode.http-address", "value", "namenode.example.com:50070") in ids
    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.namenode.http-address", "description", "HTTP address for the NameNode.") in ids

    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.datanode.data.dir", "value", "file:///var/lib/hadoop/hdfs/datanode") in ids
    assert make_id("hdfs-site.xml", "configuration", "property", "dfs.datanode.data.dir", "description", "Directory where the DataNodes store the blocks.") in ids
    

def test_config_types(get_plugin):
    plugin = get_plugin
    hadoop_hdfs_file = os.path.abspath("tests/files/hdfs-site.xml")
    artifact = plugin.parse_file(hadoop_hdfs_file, "hdfs-site.xml")
    nodes = artifact.get_nodes()

    number_node = next(filter(lambda x: x.id == make_id("hdfs-site.xml", "configuration", "property", "dfs.replication", "value", "3",), nodes))
    size_node = next(filter(lambda x: x.id == make_id("hdfs-site.xml", "configuration", "property", "dfs.blocksize", "value", "134217728"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("hdfs-site.xml", "configuration", "property", "dfs.datanode.data.dir", "value", "file:///var/lib/hadoop/hdfs/datanode"), nodes))

    assert number_node.config_type == ConfigType.NUMBER
    assert size_node.config_type == ConfigType.SIZE
    assert path_node.config_type == ConfigType.PATH
