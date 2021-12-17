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

from cfgnet.plugins.concept.docker_compose_plugin import DockerComposePlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = DockerComposePlugin()
    return plugin


def test_is_responsible(get_plugin):
    docker_compose_plugin = get_plugin
    docker_compose_file = "tests/files/docker-compose.yml"
    docker_compose_dev_file = "tests/files/docker-compose.dev.yml"
    no_docker_compose_file = "tests/files/Dockerfile"

    default_file = docker_compose_plugin.is_responsible(docker_compose_file)
    dev_file = docker_compose_plugin.is_responsible(docker_compose_dev_file)
    no_docker_compose = docker_compose_plugin.is_responsible(
        no_docker_compose_file
    )

    assert default_file
    assert dev_file
    assert not no_docker_compose


def test_parsing_docker_compose_file(get_plugin):
    docker_compose_plugin = get_plugin
    file = os.path.abspath("tests/files/docker-compose.yml")

    artifact = docker_compose_plugin.parse_file(file, "docker-compose.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 3

    assert make_id("docker-compose.yml", "file", "docker-compose.yml") in ids
    assert make_id("docker-compose.yml", "ports", "in", "5000") in ids
    assert make_id("docker-compose.yml", "ports", "out", "5000") in ids
