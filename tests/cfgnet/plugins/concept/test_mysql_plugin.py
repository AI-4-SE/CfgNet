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

from cfgnet.plugins.concept.mysql_plugin import MysqlPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = MysqlPlugin()
    return plugin


def test_is_responsible(get_plugin):
    mysql_plugin = get_plugin

    my_cnf_file = mysql_plugin.is_responsible(
        "tests/files/my.cnf"
    )

    my_ini_file = mysql_plugin.is_responsible(
        "tests/files/my.ini"
    )
    no_mysql_file = mysql_plugin.is_responsible(
        "tests/files/test.json"
    )

    assert my_cnf_file
    assert my_ini_file
    assert not no_mysql_file


def test_parsing_mysql_file_file(get_plugin):
    mysql_plugin = get_plugin
    file = os.path.abspath("tests/files/my.cnf")

    artifact = mysql_plugin.parse_file(file, "my.cnf")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    assert artifact is not None
    assert len(nodes) == 7

    assert make_id("my.cnf", "file", "my.cnf") in ids
    assert make_id("my.cnf", "client", "password", "test1234") in ids
    assert make_id("my.cnf", "mysqld", "user", "mysql") in ids
    assert make_id("my.cnf", "mysqld", "port", "3306") in ids
    assert make_id("my.cnf", "mysqld", "datadir", "/var/lib/mysql") in ids
    assert make_id("my.cnf", "mysqld", "bind_address", "127.0.0.1") in ids
    assert make_id("my.cnf", "mysqld", "key_buffer_size", "16M") in ids


def test_config_types(get_plugin):
    mysql_plugin = get_plugin
    file = os.path.abspath("tests/files/my.cnf")

    artifact = mysql_plugin.parse_file(file, "my.cnf")
    nodes = artifact.get_nodes()

    password = next(
        filter(
            lambda x: x.id == make_id("my.cnf", "client", "password", "test1234"),
            nodes,
        )
    )
    user = next(
        filter(
            lambda x: x.id == make_id("my.cnf", "mysqld", "user", "mysql"),
            nodes,
        )
    )
    path = next(
        filter(
            lambda x: x.id == make_id("my.cnf", "mysqld", "datadir", "/var/lib/mysql"),
            nodes,
        )
    )
    ip_address = next(
        filter(
            lambda x: x.id == make_id("my.cnf", "mysqld", "bind_address", "127.0.0.1"),
            nodes,
        )
    )
    size = next(
        filter(
            lambda x: x.id == make_id("my.cnf", "mysqld", "key_buffer_size", "16M"),
            nodes,
        )
    )

    assert password.config_type == ConfigType.PASSWORD
    assert user.config_type == ConfigType.USERNAME
    assert path.config_type == ConfigType.PATH
    assert ip_address.config_type == ConfigType.IP_ADDRESS
    assert size.config_type == ConfigType.SIZE
