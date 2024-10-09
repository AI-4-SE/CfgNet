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

from cfgnet.plugins.concept.cargo_plugin import CargoPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = CargoPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/Cargo.toml")
    assert not plugin.is_responsible("tests/files/test.toml")


def test_parse_pyproject_file(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/Cargo.toml")

    artifact = plugin.parse_file(file, "Cargo.toml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 13

    assert make_id("Cargo.toml", "file", "Cargo.toml") in ids
    assert make_id("Cargo.toml", "package", "name", "example") in ids
    assert make_id("Cargo.toml", "package", "version", "0.1.0") in ids
    assert make_id("Cargo.toml", "package", "edition", "2021") in ids
    assert make_id("Cargo.toml", "package", "license", "MIT") in ids
    assert make_id("Cargo.toml", "package", "homepage", "https://example.com") in ids
    assert make_id("Cargo.toml", "package", "workspace", "path/to/workspace/root") in ids
    assert make_id("Cargo.toml", "dependencies", "serde", "1.0") in ids
    assert make_id("Cargo.toml", "dependencies", "rand", "0.8") in ids
    assert make_id("Cargo.toml", "dev-dependencies", "tokio", "version", "1") in ids
    assert make_id("Cargo.toml", "dev-dependencies", "tokio", "features", "['full']") in ids
    assert make_id("Cargo.toml", "features", "default", "['serde']") in ids
    assert make_id("Cargo.toml", "profile", "release", "opt-level", "3") in ids
    
    
def test_config_types(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/Cargo.toml")

    artifact = plugin.parse_file(file, "Cargo.toml")
    nodes = artifact.get_nodes()

    name_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "package", "name", "example"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "package", "workspace", "path/to/workspace/root"), nodes))
    number_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "package", "edition", "2021"), nodes))
    dep_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "dependencies", "serde", "1.0"), nodes))
    url_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "package", "homepage", "https://example.com"), nodes))
    version_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "package", "version", "0.1.0"), nodes))
    license_node = next(filter(lambda x: x.id == make_id("Cargo.toml", "package", "license", "MIT"), nodes))
    number_node2 = next(filter(lambda x: x.id == make_id("Cargo.toml", "profile", "release", "opt-level", "3"), nodes))

    assert path_node.config_type == ConfigType.PATH
    assert url_node.config_type == ConfigType.URL
    assert license_node.config_type == ConfigType.LICENSE
    assert dep_node.config_type == ConfigType.VERSION_NUMBER
    assert number_node.config_type == ConfigType.NUMBER
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert name_node.config_type == ConfigType.NAME
    assert number_node2.config_type == ConfigType.NUMBER
