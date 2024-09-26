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
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = DockerComposePlugin()
    return plugin


def test_is_responsible(get_plugin):
    docker_compose_plugin = get_plugin

    default_file = docker_compose_plugin.is_responsible(
        "tests/files/docker-compose.yml"
    )
    dev_file = docker_compose_plugin.is_responsible(
        "tests/files/docker-compose.dev.yml"
    )
    no_docker_compose = docker_compose_plugin.is_responsible(
        "tests/files/Dockerfile"
    )

    assert default_file
    assert dev_file
    assert not no_docker_compose


def test_parse_docker_compose_file(get_plugin):
    docker_compose_plugin = get_plugin
    file = os.path.abspath("tests/files/docker-compose.yml")

    artifact = docker_compose_plugin.parse_file(file, "docker-compose.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 20

    assert make_id("docker-compose.yml", "file", "docker-compose.yml") in ids
    assert make_id("docker-compose.yml", "version", "version:3.9") in ids
    assert (
        make_id("docker-compose.yml", "services", "web", "ports", "host", "8000")
        in ids
    )
    assert (
        make_id(
            "docker-compose.yml", "services", "web", "ports", "container", "5000"
        )
        in ids
    )
    assert (
        make_id("docker-compose.yml", "services", "web", "init", "true") in ids
    )
    assert (
        make_id("docker-compose.yml", "services", "backend", "image", "/test")
        in ids
    )
    assert (
        make_id(
            "docker-compose.yml",
            "services",
            "db",
            "environment",
            "POSTGRES_USER",
            "user",
        )
        in ids
    )
    assert (
        make_id(
            "docker-compose.yml",
            "services",
            "db",
            "environment",
            "POSTGRES_PASSWORD",
            "pwd",
        )
        in ids
    )
    assert make_id("docker-compose.yml", "ipam", "driver", "default") in ids
    assert (
        make_id("docker-compose.yml", "ipam", "config", "subnet", "1.1.1.1/1")
        in ids
    )
    assert make_id("docker-compose.yml", "userns_mode", "host") in ids
    assert make_id("docker-compose.yml", "restart", "no") in ids
    assert make_id("docker-compose.yml", "healthcheck", "test", "CMD") in ids
    assert (
        make_id("docker-compose.yml", "healthcheck", "interval", "1m30s")
        in ids
    )
    assert make_id("docker-compose.yml", "expose", "3000") in ids
    assert make_id("docker-compose.yml", "env_file", ".env") in ids
    assert make_id("docker-compose.yml", "entrypoint", "/test.sh") in ids
    assert make_id("docker-compose.yml", "dns", "8.8.8.8") in ids
    assert (
        make_id("docker-compose.yml", "credential_spec", "file", "test.json")
        in ids
    )
    assert make_id("docker-compose.yml", "cpu_rt_runtime", "400ms") in ids


def test_config_types(get_plugin):
    docker_compose_plugin = get_plugin
    file = os.path.abspath("tests/files/docker-compose.yml")

    artifact = docker_compose_plugin.parse_file(file, "docker-compose.yml")
    nodes = artifact.get_nodes()
  
    port_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "docker-compose.yml",
                "services",
                "web",
                "ports",
                "container",
                "5000",
            ),
            nodes,
        )
    )

    ip_node = next(
        filter(
            lambda x: x.id == make_id("docker-compose.yml", "dns", "8.8.8.8"),
            nodes,
        )
    )

    mode_node = next(
        filter(
            lambda x: x.id == make_id("docker-compose.yml", "restart", "no"),
            nodes,
        )
    )

    boolean_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "docker-compose.yml", "services", "web", "init", "true"
            ),
            nodes,
        )
    )

    time_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "docker-compose.yml",
                "healthcheck",
                "interval",
                "1m30s",
            ),
            nodes,
        )
    )

    command_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "docker-compose.yml",
                "healthcheck",
                "test",
                "CMD",
            ),
            nodes,
        )
    )

    user_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "docker-compose.yml",
                "services",
                "db",
                "environment",
                "POSTGRES_USER",
                "user",
            ),
            nodes,
        )
    )

    password_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "docker-compose.yml",
                "services",
                "db",
                "environment",
                "POSTGRES_PASSWORD",
                "pwd",
            ),
            nodes,
        )
    )

    assert port_node.config_type == ConfigType.PORT
    assert ip_node.config_type == ConfigType.IP_ADDRESS
    assert mode_node.config_type == ConfigType.MODE
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert time_node.config_type == ConfigType.TIME
    assert command_node.config_type == ConfigType.COMMAND
    assert user_node.config_type == ConfigType.USERNAME
    assert password_node.config_type == ConfigType.PASSWORD
