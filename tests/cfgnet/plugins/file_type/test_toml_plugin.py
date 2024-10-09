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

from cfgnet.plugins.file_type.toml_plugin import TomlPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = TomlPlugin()
    return plugin


def test_is_responsible(get_plugin):
    toml_plugin = get_plugin

    toml_file = toml_plugin.is_responsible("/path/to/file.toml")
    no_toml_file = toml_plugin.is_responsible("/path/to/pom.xml")

    assert toml_file
    assert not no_toml_file


def test_parse_toml_file(get_plugin):
    toml_plugin = get_plugin
    toml_file = os.path.abspath("tests/files/test.toml")

    artifact = toml_plugin.parse_file(toml_file, "test.toml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 7

    assert make_id("test.toml", "file", "test.toml") in ids
    assert make_id("test.toml", "tool", "poetry", "name", "cfgnet") in ids
    assert make_id("test.toml", "tool", "poetry", "version", "v1.1.0") in ids
    assert make_id("test.toml", "tool", "poetry", "keywords", "['config']") in ids
    assert make_id("test.toml", "dependencies", "python", "^3.6") in ids
    assert make_id("test.toml", "dependencies", "gitpython", "^3.0") in ids
    assert make_id("test.toml", "tool", "poetry", "packages", "[{'include': 'cfgnet', 'from': 'src'}]") in ids
