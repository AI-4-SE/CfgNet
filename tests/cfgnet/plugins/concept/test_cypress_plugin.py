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

from cfgnet.plugins.concept.cypress_plugin import CypressPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = CypressPlugin()
    return plugin


def test_is_responsible(get_plugin):
    cypress_plugin = get_plugin

    cypress_file = cypress_plugin.is_responsible("tests/files/cypress.json")
    no_cypress_file = cypress_plugin.is_responsible("tests/files/package.json")

    assert cypress_file
    assert not no_cypress_file


def test_parse_cypress_file(get_plugin):
    cypress_plugin = get_plugin
    file = os.path.abspath("tests/files/cypress.json")

    artifact = cypress_plugin.parse_file(file, "cypress.json")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 16

    assert make_id("cypress.json", "file", "cypress.json") in ids
    assert make_id("cypress.json", "baseUrl", "https://test:3000/") in ids
    assert make_id("cypress.json", "fixturesFolder", "cypress/fixtures") in ids
    assert (
        make_id("cypress.json", "env", "backendUrl", "https://test/api") in ids
    )
    assert make_id("cypress.json", "env", "phone", "1234") in ids
    assert make_id("cypress.json", "env", "password", "test") in ids
    assert make_id("cypress.json", "env", "staff", "phone", "1234") in ids
    assert make_id("cypress.json", "env", "staff", "password", "test") in ids
    assert make_id("cypress.json", "defaultCommandTimeout", "8000") in ids
    assert make_id("cypress.json", "projectId", "abcd") in ids
    assert make_id("cypress.json", "retries", "runMode", "2") in ids
    assert make_id("cypress.json", "video", "False") in ids
    assert make_id("cypress.json", "viewportWidth", "1064") in ids
    assert make_id("cypress.json", "reporter", "junit") in ids
    assert make_id("cypress.json", "specPattern", "*.test.js") in ids
    assert make_id("cypress.json", "nodeVersion", "nodeVersion:system") in ids


def test_config_types(get_plugin):
    cypress_plugin = get_plugin
    file = os.path.abspath("tests/files/cypress.json")

    artifact = cypress_plugin.parse_file(file, "cypress.json")
    nodes = artifact.get_nodes()

    url_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "cypress.json",
                "baseUrl",
                "https://test:3000/",
            ),
            nodes,
        )
    )
    env_node = next(
        filter(
            lambda x: x.id == make_id("cypress.json", "env", "phone", "1234"),
            nodes,
        )
    )
    env_url_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "cypress.json", "env", "backendUrl", "https://test/api"
            ),
            nodes,
        )
    )
    timeout_node = next(
        filter(
            lambda x: x.id
            == make_id("cypress.json", "defaultCommandTimeout", "8000"),
            nodes,
        )
    )

    folder_node = next(
        filter(
            lambda x: x.id
            == make_id("cypress.json", "fixturesFolder", "cypress/fixtures"),
            nodes,
        )
    )

    id_node = next(
        filter(
            lambda x: x.id == make_id("cypress.json", "projectId", "abcd"),
            nodes,
        )
    )

    size_node = next(
        filter(
            lambda x: x.id == make_id("cypress.json", "viewportWidth", "1064"),
            nodes,
        )
    )

    pattern_node = next(
        filter(
            lambda x: x.id
            == make_id("cypress.json", "specPattern", "*.test.js"),
            nodes,
        )
    )

    assert url_node.config_type == ConfigType.URL
    assert env_node.config_type == ConfigType.ENVIRONMENT
    assert env_url_node.config_type == ConfigType.URL
    assert timeout_node.config_type == ConfigType.TIME
    assert folder_node.config_type == ConfigType.PATH
    assert id_node.config_type == ConfigType.ID
    assert size_node.config_type == ConfigType.SIZE
    assert pattern_node.config_type == ConfigType.PATTERN
