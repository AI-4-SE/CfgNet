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

from cfgnet.plugins.concept.android_plugin import AndroidPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = AndroidPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/AndroidManifest.xml")
    assert not plugin.is_responsible("tests/files/pom.xml")


def test_config_types(get_plugin):
    maven_plugin = get_plugin
    maven_file = os.path.abspath("tests/files/AndroidManifest.xml")
    artifact = maven_plugin.parse_file(maven_file, "AndroidManifest.xml")
    nodes = artifact.get_nodes()

    name_node = next(filter(lambda x: x.id == make_id("AndroidManifest.xml", "manifest", "package", "com.example.myfirstapp"), nodes))
    bool_node = next(filter(lambda x: x.id == make_id("AndroidManifest.xml", "manifest", "application", "allowBackup", "true"), nodes))
    version_node = next(filter(lambda x: x.id == make_id("AndroidManifest.xml", "manifest", "uses-sdk", "minSdkVersion", "21"), nodes))

    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert bool_node.config_type == ConfigType.BOOLEAN
    assert name_node.config_type == ConfigType.NAME
