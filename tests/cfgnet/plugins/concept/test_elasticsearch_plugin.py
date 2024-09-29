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

from cfgnet.plugins.concept.elastisearch_plugin import ElasticsearchPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = ElasticsearchPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    elsticsearch_file = plugin.is_responsible("tests/files/elasticsearch.yml")
    not_elsticsearch_file_file = plugin.is_responsible("tests/files/docker-compose.dev.yml")

    assert elsticsearch_file
    assert not not_elsticsearch_file_file


def test_parse_elasticsearch_file(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/elasticsearch.yml")

    artifact = plugin.parse_file(file, "elasticsearch.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 13

    assert make_id("elasticsearch.yml", "file", "elasticsearch.yml") in ids
    assert make_id("elasticsearch.yml", "cluster.name", "my-cluster") in ids
    assert make_id("elasticsearch.yml", "node.name", "node-1") in ids
    assert make_id("elasticsearch.yml", "node.master", "true") in ids
    assert make_id("elasticsearch.yml", "node.data", "true") in ids
    assert make_id("elasticsearch.yml", "node.ingest", "true") in ids
    assert make_id("elasticsearch.yml", "path.data", "/var/lib/elasticsearch/data") in ids
    assert make_id("elasticsearch.yml", "path.logs", "/var/log/elasticsearch") in ids
    assert make_id("elasticsearch.yml", "network.host", "0.0.0.0") in ids
    assert make_id("elasticsearch.yml", "http.port", "9200") in ids
    assert make_id("elasticsearch.yml", "discovery.seed_hosts", "['es-node1.example.com', 'es-node2.example.com']") in ids
    assert make_id("elasticsearch.yml", "cluster.initial_master_nodes", "['es-node1.example.com', 'es-node2.example.com']") in ids
    assert make_id("elasticsearch.yml", "http.enabled", "true") in ids


def test_config_types(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/elasticsearch.yml")
    artifact = plugin.parse_file(file, "elasticsearch.yml")
    nodes = artifact.get_nodes()
  
    port_node = next(filter(lambda x: x.id == make_id("elasticsearch.yml", "http.port", "9200"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("elasticsearch.yml", "node.master", "true"), nodes))
    name_node = next(filter(lambda x: x.id == make_id("elasticsearch.yml", "node.name", "node-1"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("elasticsearch.yml", "path.data", "/var/lib/elasticsearch/data"), nodes))

    assert port_node.config_type == ConfigType.PORT
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert name_node.config_type == ConfigType.NAME
    assert path_node.config_type == ConfigType.PATH
