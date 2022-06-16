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

from cfgnet.plugins.concept.travis_plugin import TravisPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = TravisPlugin()
    return plugin


def test_is_responsible(get_plugin):
    travis_plugin = get_plugin
    travis_file = os.path.abspath("tests/files/.travis.yml")
    no_travis_file = os.path.abspath("tests/files/Dockerfile")

    travis_file_result = travis_plugin.is_responsible(travis_file)
    no_travis_file_result = travis_plugin.is_responsible(no_travis_file)

    assert travis_file_result
    assert not no_travis_file_result


def test_parsing_travis_file(get_plugin):
    travis_plugin = get_plugin
    travis_file = os.path.abspath("tests/files/.travis.yml")

    artifact = travis_plugin.parse_file(travis_file, ".travis.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 21

    assert make_id(".travis.yml", "python", "3.8") in ids
    assert make_id(".travis.yml", "python", "3.7") in ids
    assert make_id(".travis.yml", "env", "TEST_SUITE=units") in ids
    assert make_id(".travis.yml", "git", "depth", "3") in ids
    assert make_id(".travis.yml", "git", "quiet", "true") in ids
    assert make_id(".travis.yml", "file", ".travis.yml") in ids
    assert (
        make_id(
            ".travis.yml",
            "jobs",
            "include",
            "name/unit-tests",
            "python",
            "3.5",
        )
        in ids
    )
    assert (
        make_id(
            ".travis.yml",
            "jobs",
            "include",
            "name/unit-tests",
            "env",
            "TEST_SUITE=suite_unit",
        )
        in ids
    )
    assert (
        make_id(
            ".travis.yml",
            "jobs",
            "include",
            "name/unit-tests",
            "name",
            "unit-tests",
        )
        in ids
    )
    assert (
        make_id(
            ".travis.yml",
            "jobs",
            "include",
            "name/pypy-tests",
            "python",
            "pypy",
        )
        in ids
    )
    assert (
        make_id(
            ".travis.yml",
            "jobs",
            "include",
            "name/pypy-tests",
            "env",
            "TEST_SUITE=suite_pypy",
        )
        in ids
    )
    assert (
        make_id(
            ".travis.yml",
            "jobs",
            "include",
            "name/pypy-tests",
            "name",
            "pypy-tests",
        )
        in ids
    )

    assert make_id(".travis.yml", "env", "FOLDER=integration/user") in ids
    assert make_id(".travis.yml", "version", "version:>= 1.0.0") in ids
    assert make_id(".travis.yml", "os", "linux") in ids
    assert make_id(".travis.yml", "dist", "trusty") in ids
    assert make_id(".travis.yml", "language", "ruby") in ids
    assert make_id(".travis.yml", "services", "docker") in ids
    assert make_id(".travis.yml", "arch", "amd64") in ids
    assert make_id(".travis.yml", "after_success", "python run pytest") in ids


def test_config_types(get_plugin):
    travis_plugin = get_plugin
    file = os.path.abspath("tests/files/.travis.yml")

    artifact = travis_plugin.parse_file(file, ".travis.yml")
    nodes = artifact.get_nodes()

    version_node = next(
        filter(
            lambda x: x.id
            == make_id(
                ".travis.yml",
                "version",
                "version:>= 1.0.0",
            ),
            nodes,
        )
    )

    platform_node = next(
        filter(
            lambda x: x.id == make_id(".travis.yml", "os", "linux"),
            nodes,
        )
    )

    name_node = next(
        filter(
            lambda x: x.id == make_id(".travis.yml", "dist", "trusty"),
            nodes,
        )
    )

    script_node = next(
        filter(
            lambda x: x.id
            == make_id(".travis.yml", "after_success", "python run pytest"),
            nodes,
        )
    )

    env_node = next(
        filter(
            lambda x: x.id
            == make_id(".travis.yml", "env", "TEST_SUITE=units"),
            nodes,
        )
    )

    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert name_node.config_type == ConfigType.NAME
    assert platform_node.config_type == ConfigType.PLATFORM
    assert script_node.config_type == ConfigType.COMMAND
    assert env_node.config_type == ConfigType.ENVIRONMENT
