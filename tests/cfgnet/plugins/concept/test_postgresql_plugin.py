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

from cfgnet.plugins.concept.postgresql_plugin import PostgreSQLPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = PostgreSQLPlugin()
    return plugin


def test_is_responsible(get_plugin):
    postgrsql_plugin = get_plugin

    postgresql_file = postgrsql_plugin.is_responsible(
        "tests/files/postgresql.conf"
    )

    no_postgresql_file = postgrsql_plugin.is_responsible(
        "tests/files/test.conf"
    )

    assert postgresql_file
    assert not no_postgresql_file


def test_parse_postgresql_file(get_plugin):
    postgresql_plugin = get_plugin
    file = os.path.abspath("tests/files/postgresql.conf")

    artifact = postgresql_plugin.parse_file(file, "postgresql.conf")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    assert artifact is not None
    assert len(nodes) == 23

    assert make_id("postgresql.conf", "port", "5432") in ids
    assert make_id("postgresql.conf", "effective_cache_size", "512MB") in ids
    assert make_id("postgresql.conf", "random_page_cost", "1.1") in ids
    assert make_id("postgresql.conf", "effective_io_concurrency", "200") in ids
    assert make_id("postgresql.conf", "log_filename", "postgresql.log") in ids
    assert make_id("postgresql.conf", "max_wal_senders", "5") in ids
    assert make_id("postgresql.conf", "autovacuum", "on") in ids


def test_config_types(get_plugin):
    postgresql_plugin = get_plugin
    file = os.path.abspath("tests/files/postgresql.conf")

    artifact = postgresql_plugin.parse_file(file, "postgresql.conf")
    nodes = artifact.get_nodes()

    port_node = next(filter(lambda x: x.id == make_id("postgresql.conf", "port", "5432"), nodes))
    size_node = next(filter(lambda x: x.id == make_id("postgresql.conf", "effective_cache_size", "512MB"), nodes))
    number_node = next(filter(lambda x: x.id == make_id("postgresql.conf", "random_page_cost", "1.1"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("postgresql.conf", "log_filename", "postgresql.log"), nodes))

    assert path_node.config_type == ConfigType.PATH
    assert number_node.config_type == ConfigType.NUMBER
    assert size_node.config_type == ConfigType.SIZE
    assert port_node.config_type == ConfigType.PORT
