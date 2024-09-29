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

from cfgnet.plugins.concept.kafka_plugin import KafkaPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = KafkaPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    kafka_file = plugin.is_responsible("tests/files/server.properties")
    not_kafka_file = plugin.is_responsible("tests/files/application.xml")

    assert kafka_file
    assert not not_kafka_file


def test_parse_alluxio_file(get_plugin):
    plugin = get_plugin
    kafka_file = os.path.abspath("tests/files/server.properties")
    artifact = plugin.parse_file(kafka_file, "server.properties")

    value_nodes = artifact.get_nodes()
    ids = [node.id for node in value_nodes]

    assert artifact is not None
    assert len(value_nodes) == 10

    assert make_id("server.properties", "file", "server.properties") in ids
    assert make_id("server.properties", "broker.id", "1") in ids
    assert make_id("server.properties", "listeners", "PLAINTEXT://:9092") in ids
    assert make_id("server.properties", "advertised.listeners", "PLAINTEXT://broker1.example.com:9092") in ids
    assert make_id("server.properties", "log.dirs", "/var/lib/kafka/logs") in ids
    assert make_id("server.properties", "num.partitions", "3") in ids
    assert make_id("server.properties", "log.retention.hours", "168") in ids
    assert make_id("server.properties", "log.segment.bytes", "1073741824") in ids
    assert make_id("server.properties", "log.retention.check.interval.ms", "300000") in ids
    assert make_id("server.properties", "auto.create.topics.enable", "true") in ids
    

def test_alluxio_config_types(get_plugin):
    plugin = get_plugin
    kafka_file = os.path.abspath("tests/files/server.properties")
    artifact = plugin.parse_file(kafka_file, "server.properties")
    nodes = artifact.get_nodes()

    path_node = next(filter(lambda x: x.id == make_id("server.properties", "log.dirs", "/var/lib/kafka/logs",), nodes))
    size_node = next(filter(lambda x: x.id == make_id("server.properties", "log.segment.bytes", "1073741824",), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("server.properties", "auto.create.topics.enable", "true"), nodes))

    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert size_node.config_type == ConfigType.SIZE
    assert path_node.config_type == ConfigType.PATH
