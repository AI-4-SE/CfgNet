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

from cfgnet.plugins.concept.alluxio_plugin import AlluxioPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = AlluxioPlugin()
    return plugin


def test_is_responsible(get_plugin):
    alluxio_plugin = get_plugin

    alluxio_file = alluxio_plugin.is_responsible("tests/files/alluxio-site.properties")
    not_alluxio_file = alluxio_plugin.is_responsible("tests/files/application.xml")

    assert alluxio_file
    assert not not_alluxio_file


def test_parse_alluxio_file(get_plugin):
    alluxio_plugin = get_plugin
    alluxio_file = os.path.abspath("tests/files/alluxio-site.properties")
    artifact = alluxio_plugin.parse_file(alluxio_file, "alluxio-site.properties")

    value_nodes = artifact.get_nodes()
    ids = [node.id for node in value_nodes]

    assert artifact is not None
    assert len(value_nodes) == 12

    assert make_id("alluxio-site.properties", "file", "alluxio-site.properties") in ids
    assert make_id("alluxio-site.properties", "alluxio.master.hostname", "alluxio-master.example.com") in ids
    assert make_id("alluxio-site.properties", "alluxio.master.port", "19998") in ids
    assert make_id("alluxio-site.properties", "alluxio.worker.memory.size", "16GB") in ids
    assert make_id("alluxio-site.properties", "alluxio.underfs.address", "hdfs://namenode.example.com:8020/") in ids
    assert make_id("alluxio-site.properties", "alluxio.worker.tieredstore.level0.dirs.path", "/mnt/ramdisk") in ids
    assert make_id("alluxio-site.properties", "alluxio.user.file.replication.min", "2") in ids
    assert make_id("alluxio-site.properties", "alluxio.master.logging.level", "INFO") in ids
    assert make_id("alluxio-site.properties", "alluxio.user.block.size.bytes", "128MB") in ids
    assert make_id("alluxio-site.properties", "alluxio.user.max.retry.count", "5") in ids
    assert make_id("alluxio-site.properties", "alluxio.user.file.readtype.default", "CACHE") in ids
    assert make_id("alluxio-site.properties", "alluxio.worker.rpc.port", "30000") in ids
    

def test_alluxio_config_types(get_plugin):
    alluxio_plugin = get_plugin
    alluxio_file = os.path.abspath("tests/files/alluxio-site.properties")
    artifact = alluxio_plugin.parse_file(alluxio_file, "alluxio-site.properties")
    nodes = artifact.get_nodes()

    name_node = next(filter(lambda x: x.id == make_id("alluxio-site.properties", "alluxio.master.hostname", "alluxio-master.example.com",), nodes))
    port_node = next(filter(lambda x: x.id == make_id("alluxio-site.properties", "alluxio.master.port", "19998",), nodes))
    size_node = next(filter(lambda x: x.id == make_id("alluxio-site.properties", "alluxio.user.block.size.bytes", "128MB"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("alluxio-site.properties", "alluxio.worker.tieredstore.level0.dirs.path", "/mnt/ramdisk"), nodes))

    assert name_node.config_type == ConfigType.NAME
    assert port_node.config_type == ConfigType.PORT
    assert size_node.config_type == ConfigType.SIZE
    assert path_node.config_type == ConfigType.PATH
