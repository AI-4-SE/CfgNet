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

from cfgnet.plugins.concept.gradle_wrapper_plugin import GradleWrapperPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = GradleWrapperPlugin()
    return plugin


def test_is_responsible(get_plugin):
    gradle_wrapper_plugin = get_plugin

    gradle_wrapper_file = gradle_wrapper_plugin.is_responsible("tests/files/gradle-wrapper.properties")
    not_gradle_wrapper_file = gradle_wrapper_plugin.is_responsible("tests/files/test.properties")

    assert gradle_wrapper_file
    assert not not_gradle_wrapper_file


def test_parse_gradle_wrapper_file(get_plugin):
    gradle_wrapper_plugin = get_plugin
    gradle_wrapper_file = os.path.abspath("tests/files/gradle-wrapper.properties")
    artifact = gradle_wrapper_plugin.parse_file(gradle_wrapper_file, "gradle-wrapper.properties")

    value_nodes = artifact.get_nodes()
    ids = {node.id for node in value_nodes}

    assert artifact is not None
    assert len(value_nodes) == 6

    assert make_id("gradle-wrapper.properties", "file", "gradle-wrapper.properties") in ids
    assert make_id("gradle-wrapper.properties", "distributionurl", "https://services.gradle.org/distributions/gradle-8.6-bin.zip") in ids
    assert make_id("gradle-wrapper.properties", "distributionbase", "GRADLE_USER_HOME") in ids
    assert make_id("gradle-wrapper.properties", "distributionpath", "wrapper/dists") in ids
    assert make_id("gradle-wrapper.properties", "zipstorebase", "GRADLE_USER_HOME") in ids
    assert make_id("gradle-wrapper.properties", "zipstorepath", "wrapper/dists") in ids


def test_config_types(get_plugin):
    gradle_wrapper_plugin = get_plugin
    gradle_wrapper_file = os.path.abspath("tests/files/gradle-wrapper.properties")
    artifact = gradle_wrapper_plugin.parse_file(gradle_wrapper_file, "gradle-wrapper.properties")
    nodes = artifact.get_nodes()

    url_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "gradle-wrapper.properties",
                "distributionurl",
                "https://services.gradle.org/distributions/gradle-8.6-bin.zip",
            ),
            nodes,
        )
    )

    path_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "gradle-wrapper.properties",
                "distributionpath",
                "wrapper/dists",
            ),
            nodes,
        )
    )

    assert url_node.config_type == ConfigType.URL
    assert path_node.config_type == ConfigType.PATH
