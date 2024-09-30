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

from cfgnet.plugins.concept.mapreduce_plugin import MapReducePlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = MapReducePlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    mapred_file = plugin.is_responsible("tests/files/mapred-site.xml")
    not_mapred_file = plugin.is_responsible("tests/files/core-site.xml")

    assert mapred_file
    assert not not_mapred_file


def test_parse_mapred_file(get_plugin):
    plugin = get_plugin
    mapred_file = os.path.abspath("tests/files/mapred-site.xml")
    artifact = plugin.parse_file(mapred_file, "mapred-site.xml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 11

    assert make_id("mapred-site.xml", "file", "mapred-site.xml") in ids
    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.framework.name", "value", "yarn") in ids
    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.framework.name", "description", "Specifies that YARN will be used as the MapReduce execution framework.") in ids

    assert make_id("mapred-site.xml", "configuration", "property", "yarn.resourcemanager.address", "value", "resourcemanager.example.com:8032") in ids
    assert make_id("mapred-site.xml", "configuration", "property", "yarn.resourcemanager.address", "description", "Address of the YARN ResourceManager.") in ids

    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.output.fileoutputformat.compress", "value", "true") in ids
    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.output.fileoutputformat.compress", "description", "Enable compression for job output files.") in ids

    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.job.reduces", "value", "2") in ids
    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.job.reduces", "description", "Sets the number of reducers for MapReduce jobs.") in ids
    
    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.map.memory.mb", "value", "1024") in ids
    assert make_id("mapred-site.xml", "configuration", "property", "mapreduce.map.memory.mb", "description", "Sets the heap size in MB for map tasks (1GB in this case).") in ids
    

def test_config_types(get_plugin):
    plugin = get_plugin
    mapred_file = os.path.abspath("tests/files/mapred-site.xml")
    artifact = plugin.parse_file(mapred_file, "mapred-site.xml")
    nodes = artifact.get_nodes()

    name_node = next(filter(lambda x: x.id == make_id("mapred-site.xml", "configuration", "property", "mapreduce.framework.name", "value", "yarn",), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("mapred-site.xml", "configuration", "property", "mapreduce.output.fileoutputformat.compress", "value", "true"), nodes))
    number_node = next(filter(lambda x: x.id == make_id("mapred-site.xml", "configuration", "property", "mapreduce.job.reduces", "value", "2"), nodes))
    size_node = next(filter(lambda x: x.id == make_id("mapred-site.xml", "configuration", "property", "mapreduce.map.memory.mb", "value", "1024"), nodes))

    assert name_node.config_type == ConfigType.NAME
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert number_node.config_type == ConfigType.NUMBER
    assert size_node.config_type == ConfigType.SIZE
