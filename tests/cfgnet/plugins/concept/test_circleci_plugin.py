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

from cfgnet.plugins.concept.circleci_plugin import CircleCiPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = CircleCiPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin
    circle_file = os.path.abspath("tests/files/.circleci/config.yml")
    no_circle_file = os.path.abspath("tests/files/config.yml")

    circle_file = plugin.is_responsible(circle_file)
    no_circle_file = plugin.is_responsible(no_circle_file)

    assert circle_file
    assert not no_circle_file


def test_parse_circle_file(get_plugin):
    plugin = get_plugin
    circle_file = os.path.abspath("tests/files/.circleci/config.yml")

    artifact = plugin.parse_file(circle_file, "config.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    for id in ids:
        print(id)

    assert artifact is not None
    assert len(nodes) == 16

    assert make_id("config.yml", "file", "config.yml") in ids
    assert make_id("config.yml", "jobs", "build", "docker", "offset:0", "image", "circleci/node:14") in ids
    assert make_id("config.yml", "jobs", "build", "steps", "checkout") in ids
    assert make_id("config.yml", "jobs", "build", "steps", "offset:0", "run", "name", "Install dependencies") in ids
    assert make_id("config.yml", "jobs", "build", "steps", "offset:0", "run", "command", "npm install") in ids
    assert make_id("config.yml", "jobs", "build", "steps", "offset:1", "persist_to_workspace", "root", ".") in ids
    assert make_id("config.yml", "jobs", "build", "steps", "offset:1", "persist_to_workspace", "paths", "dist") in ids
    assert make_id("config.yml", "jobs", "build", "steps", "offset:1", "persist_to_workspace", "paths", "src") in ids
    assert make_id("config.yml", "jobs", "deploy", "docker", "offset:0", "image", "circleci/node:14") in ids
    assert make_id("config.yml", "jobs", "deploy", "steps", "offset:0", "attach_workspace", "at", "/workspace") in ids
    assert make_id("config.yml", "jobs", "deploy", "steps", "offset:1", "run", "name", "Deploy application") in ids
    assert make_id("config.yml", "jobs", "deploy", "steps", "offset:1", "run", "command", 'echo "Deploying application..."') in ids
    assert make_id("config.yml", "workflows", "version", "2") in ids
    assert make_id("config.yml", "workflows", "build_and_deploy", "jobs", "build") in ids
    assert make_id("config.yml", "workflows", "build_and_deploy", "jobs", "offset:0", "deploy", "requires", "build") in ids

    
def test_config_types(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/.circleci/config.yml")

    artifact = plugin.parse_file(file, "config.yml")
    nodes = artifact.get_nodes()

    version_node = next(filter(lambda x: x.id == make_id("config.yml", "workflows", "version", "2"), nodes))
    command_node = next(filter(lambda x: x.id == make_id("config.yml", "jobs", "build", "steps", "offset:0", "run", "command", "npm install"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("config.yml", "jobs", "deploy", "steps", "offset:0", "attach_workspace", "at", "/workspace"), nodes))
    image_node = next(filter(lambda x: x.id == make_id("config.yml", "jobs", "build", "docker", "offset:0", "image", "circleci/node:14"), nodes))

    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert command_node.config_type == ConfigType.COMMAND
    assert path_node.config_type == ConfigType.PATH
    assert image_node.config_type == ConfigType.IMAGE
