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

from cfgnet.plugins.concept.gradle_plugin import GradlePlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = GradlePlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/gradle.properties")
    assert not plugin.is_responsible("tests/files/test.properties")


def test_config_types(get_plugin):
    plugin = get_plugin
    gradle_file = os.path.abspath("tests/files/gradle.properties")
    artifact = plugin.parse_file(gradle_file, "gradle.properties")
    nodes = artifact.get_nodes()

    for node in nodes:
        print(node, node.config_type)

    name_node = next(filter(lambda x: x.id == make_id("gradle.properties", "appname", "MyApp"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("gradle.properties", "org.gradle.daemon", "true"), nodes))
    time_node = next(filter(lambda x: x.id == make_id("gradle.properties", "org.gradle.daemon.idletimeout", "1000"), nodes))
    version_node = next(filter(lambda x: x.id == make_id("gradle.properties", "projectversion", "1.0.0"), nodes))
    user_node = next(filter(lambda x: x.id == make_id("gradle.properties", "systemprop.gradle.wrapperuser", "myuser"), nodes))
    password_node = next(filter(lambda x: x.id == make_id("gradle.properties", "systemprop.gradle.wrapperpassword", "12345"), nodes))

    assert name_node.config_type == ConfigType.NAME
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert time_node.config_type == ConfigType.TIME
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert user_node.config_type == ConfigType.USERNAME
    assert password_node.config_type == ConfigType.PASSWORD
