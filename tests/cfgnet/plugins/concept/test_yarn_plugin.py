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

from cfgnet.plugins.concept.yarn_plugin import YarnPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = YarnPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    yarn_file = plugin.is_responsible("tests/files/yarn-site.xml")
    not_yarn_file = plugin.is_responsible("tests/files/core-site.xml")

    assert yarn_file
    assert not not_yarn_file


def test_parse_yarn_file(get_plugin):
    plugin = get_plugin
    yarn_file = os.path.abspath("tests/files/yarn-site.xml")
    artifact = plugin.parse_file(yarn_file, "yarn-site.xml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 5

    assert make_id("yarn-site.xml", "file", "yarn-site.xml") in ids
    assert make_id("yarn-site.xml", "configuration", "property", "yarn.resourcemanager.hostname", "value", "resourcemanager.example.com") in ids
    assert make_id("yarn-site.xml", "configuration", "property", "yarn.resourcemanager.address", "value", "resourcemanager.example.com:8032") in ids
    assert make_id("yarn-site.xml", "configuration", "property", "yarn.nodemanager.resource.memory-mb", "value", "8192") in ids
    assert make_id("yarn-site.xml", "configuration", "property", "yarn.nodemanager.resource.cpu-vcores", "value", "4") in ids


def test_config_types(get_plugin):
    plugin = get_plugin
    yarn_file = os.path.abspath("tests/files/yarn-site.xml")
    artifact = plugin.parse_file(yarn_file, "yarn-site.xml")
    nodes = artifact.get_nodes()

    number_node = next(filter(lambda x: x.id == make_id("yarn-site.xml", "configuration", "property", "yarn.nodemanager.resource.cpu-vcores", "value", "4"), nodes))
    name_node = next(filter(lambda x: x.id == make_id("yarn-site.xml", "configuration", "property", "yarn.resourcemanager.hostname", "value", "resourcemanager.example.com"), nodes))
    size_node = next(filter(lambda x: x.id == make_id("yarn-site.xml", "configuration", "property", "yarn.nodemanager.resource.memory-mb", "value", "8192"), nodes))

    assert number_node.config_type == ConfigType.NUMBER
    assert name_node.config_type == ConfigType.NAME
    assert size_node.config_type == ConfigType.SIZE
