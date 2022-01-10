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

from cfgnet.plugins.concept.docker_plugin import DockerPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = DockerPlugin()
    return plugin


def test_is_responsible(get_plugin):
    docker_plugin = get_plugin

    docker_file = docker_plugin.is_responsible("/path/to/Dockerfile")
    not_docker_file = docker_plugin.is_responsible("/path/to/file.ini")

    assert docker_file
    assert not not_docker_file


def test_parse_dockerfile(get_plugin):
    docker_plugin = get_plugin
    dockerfile = os.path.abspath("tests/files/Dockerfile")

    artifact = docker_plugin.parse_file(dockerfile, "Dockerfile")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 31

    # FILE PATH
    assert make_id("Dockerfile", "file", "Dockerfile") in ids

    # FROM
    assert make_id("Dockerfile", "from", "image", "java:8") in ids
    assert make_id("Dockerfile", "from", "name", "builder") in ids

    # ENV
    assert make_id("Dockerfile", "env", "myName", '"John Doe"') in ids
    assert make_id("Dockerfile", "env", "port", "8000") in ids
    assert make_id("Dockerfile", "env", "version", "42") in ids

    # ENTRYPOINT
    assert (
        make_id(
            "Dockerfile", "entrypoint", "exec_command", "lorem ipsum foo.bar"
        )
        in ids
    )
    assert make_id("Dockerfile", "entrypoint", "param0", "lorem") in ids
    assert make_id("Dockerfile", "entrypoint", "param1", "ipsum") in ids
    assert make_id("Dockerfile", "entrypoint", "param2", "foo.bar") in ids
    assert (
        make_id("Dockerfile", "entrypoint", "exec_command", "python ./app.py")
        in ids
    )
    assert make_id("Dockerfile", "entrypoint", "param0", "python") in ids
    assert make_id("Dockerfile", "entrypoint", "param1", "app.py") in ids

    # CMD
    assert (
        make_id("Dockerfile", "cmd", "exec_command", "java -jar app.jar")
        in ids
    )
    assert make_id("Dockerfile", "cmd", "param0", "java") in ids
    assert make_id("Dockerfile", "cmd", "param1", "-jar") in ids
    assert make_id("Dockerfile", "cmd", "param2", "app.jar") in ids

    # ADD
    assert make_id("Dockerfile", "add", "src", "foo.jar") in ids
    assert make_id("Dockerfile", "add", "dest", "bar.jar") in ids
    assert make_id("Dockerfile", "add", "chown", "1") in ids

    # COPY
    assert make_id("Dockerfile", "copy", "src", "foo.jar") in ids
    assert make_id("Dockerfile", "copy", "dest", "bar.jar") in ids
    assert make_id("Dockerfile", "copy", "chown", "55:mygroup") in ids
    assert make_id("Dockerfile", "copy", "from", "builder") in ids

    # EXPOSE
    assert make_id("Dockerfile", "expose", "1234") in ids
    assert make_id("Dockerfile", "expose", "port", "80") in ids
    assert make_id("Dockerfile", "expose", "protocol", "tcp") in ids
    assert make_id("Dockerfile", "expose", "port", "8080") in ids
    assert make_id("Dockerfile", "expose", "protocol", "udp") in ids

    # ADD Tab Char
    assert make_id("Dockerfile", "add", "src", "vendor") in ids
    assert make_id("Dockerfile", "add", "dest", "/vendor") in ids


def test_config_types(get_plugin):
    docker_plugin = get_plugin
    file = os.path.abspath("tests/files/Dockerfile")

    artifact = docker_plugin.parse_file(file, "docker-compose.yml")
    nodes = artifact.get_nodes()

    expose_port = next(
        filter(
            lambda x: x.id == make_id("Dockerfile", "expose", "port", "8080"),
            nodes,
        )
    )
    expose_protocol = next(
        filter(
            lambda x: x.id
            == make_id("Dockerfile", "expose", "protocol", "tcp"),
            nodes,
        )
    )
    copy_src = next(
        filter(
            lambda x: x.id == make_id("Dockerfile", "copy", "src", "foo.jar"),
            nodes,
        )
    )
    add_dest = next(
        filter(
            lambda x: x.id == make_id("Dockerfile", "add", "dest", "bar.jar"),
            nodes,
        )
    )
    from_image = next(
        filter(
            lambda x: x.id == make_id("Dockerfile", "from", "image", "java:8"),
            nodes,
        )
    )

    assert expose_port.config_type == ConfigType.PORT
    assert expose_protocol.config_type == ConfigType.PROTOCOL
    assert copy_src.config_type == ConfigType.PATH
    assert add_dest.config_type == ConfigType.PATH
    assert from_image.config_type == ConfigType.IMAGE
