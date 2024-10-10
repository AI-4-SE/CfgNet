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

from cfgnet.plugins.concept.flutter_plugin import FlutterPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = FlutterPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/pubspec.yaml")
    assert not plugin.is_responsible("tests/files/pubspec.yml")


def test_config_types(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/pubspec.yaml")
    artifact = plugin.parse_file(file, "pubspec.yaml")
    nodes = artifact.get_nodes()
  
    for node in nodes:
        print(node, node.config_type)

    version_node = next(filter(lambda x: x.id == make_id("pubspec.yaml", "version", "1.0.0"), nodes))
    name_node = next(filter(lambda x: x.id == make_id("pubspec.yaml", "name", "my_flutter_app"), nodes))
    url_node = next(filter(lambda x: x.id == make_id("pubspec.yaml", "homepage", "https://example.com"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("pubspec.yaml", "flutter", "uses-material-design", "true"), nodes))
    dep_node = next(filter(lambda x: x.id == make_id("pubspec.yaml", "dev_dependencies", "test", ">=1.15.0 <2.0.0"), nodes))

    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert dep_node.config_type == ConfigType.VERSION_NUMBER
    assert name_node.config_type == ConfigType.NAME
    assert url_node.config_type == ConfigType.URL
