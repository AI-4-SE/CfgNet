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

from cfgnet.plugins.concept.poetry_plugin import PoetryPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = PoetryPlugin()
    return plugin


def test_is_responsible(get_plugin):
    pyproject_plugin = get_plugin

    pyproject_file = pyproject_plugin.is_responsible("tests/files/pyproject.toml")
    no_pyrpoject_file = pyproject_plugin.is_responsible("tests/files/test.toml")

    assert pyproject_file
    assert not no_pyrpoject_file


def test_parse_pyproject_file(get_plugin):
    pyproject_plugin = get_plugin
    file = os.path.abspath("tests/files/pyproject.toml")

    artifact = pyproject_plugin.parse_file(file, "pyproject.toml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 12

    assert make_id("pyproject.toml", "file", "pyproject.toml") in ids
    assert make_id("pyproject.toml", "tool", "poetry", "name", "CfgNet") in ids
    assert (
        make_id("pyproject.toml", "tool", "poetry", "version", "version:1.0.0")
        in ids
    )
    assert (
        make_id("pyproject.toml", "tool", "poetry", "include", "test.py")
        in ids
    )
    assert (
        make_id("pyproject.toml", "tool", "poetry", "exclude", "hello.py")
        in ids
    )
    assert (
        make_id("pyproject.toml", "tool", "poetry", "license", "GPL-3.0+")
        in ids
    )
    assert (
        make_id(
            "pyproject.toml",
            "tool",
            "poetry",
            "homepage",
            "https://github.com",
        )
        in ids
    )
    assert (
        make_id(
            "pyproject.toml",
            "tool",
            "poetry",
            "packages",
            "packages_0",
            "include",
            "cfgnet",
        )
        in ids
    )
    assert (
        make_id(
            "pyproject.toml",
            "tool",
            "poetry",
            "packages",
            "packages_0",
            "from",
            "src",
        )
        in ids
    )
    assert (
        make_id(
            "pyproject.toml",
            "tool",
            "poetry",
            "dependencies",
            "python",
            "python:^3.8",
        )
        in ids
    )
    assert (
        make_id(
            "pyproject.toml",
            "tool",
            "poetry",
            "dev-dependencies",
            "cov",
            "cov:5.1",
        )
        in ids
    )
    assert (
        make_id(
            "pyproject.toml", "tool", "poetry", "scripts", "cfgnet", "main"
        )
        in ids
    )


def test_config_types(get_plugin):
    pyproject_plugin = get_plugin
    file = os.path.abspath("tests/files/pyproject.toml")

    artifact = pyproject_plugin.parse_file(file, "pyproject.toml")
    nodes = artifact.get_nodes()

    url_node = next(filter(lambda x: "homepage" in x.id, nodes))
    license_node = next(filter(lambda x: "license" in x.id, nodes))
    dep_node = next(filter(lambda x: "dependencies" in x.id, nodes))
    dev_dep_node = next(filter(lambda x: "dev-dependencies" in x.id, nodes))
    version_node = next(filter(lambda x: "version" in x.id, nodes))
    script_node = next(filter(lambda x: "scripts" in x.id, nodes))
    name_node = next(filter(lambda x: "name" in x.id, nodes))

    assert url_node.config_type == ConfigType.URL
    assert license_node.config_type == ConfigType.LICENSE
    assert dep_node.config_type == ConfigType.VERSION_NUMBER
    assert dev_dep_node.config_type == ConfigType.VERSION_NUMBER
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert script_node.config_type == ConfigType.COMMAND
    assert name_node.config_type == ConfigType.NAME
