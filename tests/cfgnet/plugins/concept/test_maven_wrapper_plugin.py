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

from cfgnet.plugins.concept.maven_wrapper_plugin import MavenWrapperPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = MavenWrapperPlugin()
    return plugin


def test_is_responsible(get_plugin):
    maven_wrapper_plugin = get_plugin

    maven_wrapper_file = maven_wrapper_plugin.is_responsible("tests/files/maven-wrapper.properties")
    not_maven_wrapper_file = maven_wrapper_plugin.is_responsible("tests/files/test.properties")

    assert maven_wrapper_file
    assert not not_maven_wrapper_file


def test_parse_maven_wrapper_file(get_plugin):
    maven_wrapper_plugin = get_plugin
    maven_wrapper_file = os.path.abspath("tests/files/maven-wrapper.properties")
    artifact = maven_wrapper_plugin.parse_file(maven_wrapper_file, "maven-wrapper.properties")

    value_nodes = artifact.get_nodes()
    ids = {node.id for node in value_nodes}

    assert artifact is not None
    assert len(value_nodes) == 3

    assert make_id("maven-wrapper.properties", "file", "maven-wrapper.properties") in ids
    assert make_id("maven-wrapper.properties", "distributionurl", "https://repo.maven.apache.org/apache-maven-3.9.5-bin.zip") in ids
    assert make_id("maven-wrapper.properties", "wrapperurl", "https://repo.maven.apache.org/maven-wrapper-3.2.0.jar") in ids


def test_config_types(get_plugin):
    maven_wrapper_plugin = get_plugin
    maven_wrapper_file = os.path.abspath("tests/files/maven-wrapper.properties")
    artifact = maven_wrapper_plugin.parse_file(maven_wrapper_file, "maven-wrapper.properties")
    nodes = artifact.get_nodes()

    distribution_url_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "maven-wrapper.properties",
                "distributionurl",
                "https://repo.maven.apache.org/apache-maven-3.9.5-bin.zip",
            ),
            nodes,
        )
    )

    wrapper_url_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "maven-wrapper.properties",
                "wrapperurl",
                "https://repo.maven.apache.org/maven-wrapper-3.2.0.jar",
            ),
            nodes,
        )
    )

    assert distribution_url_node.config_type == ConfigType.URL
    assert wrapper_url_node.config_type == ConfigType.URL
