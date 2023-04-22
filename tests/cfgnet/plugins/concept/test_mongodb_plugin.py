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

from cfgnet.plugins.concept.mongodb_plugin import MongoDBPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = MongoDBPlugin()
    return plugin


def test_is_responsible(get_plugin):
    mongodb_plugin = get_plugin

    mongodb_file = mongodb_plugin.is_responsible(
        "tests/files/mongod.conf"
    )

    no_mongodb_file = mongodb_plugin.is_responsible(
        "tests/files/test.conf"
    )

    assert mongodb_file
    assert not no_mongodb_file


def test_parse_postgresql_file(get_plugin):
    mongodb_plugin = get_plugin
    file = os.path.abspath("tests/files/mongod.conf")

    artifact = mongodb_plugin.parse_file(file, "mongod.conf")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    for node in nodes:
        print(node, node.config_type, node.parent.location)

    assert artifact is not None
    assert len(nodes) == 9

    assert make_id("mongod.conf", "file", "mongod.conf") in ids
    assert make_id("mongod.conf", "systemLog", "destination", "file") in ids
    assert make_id("mongod.conf", "systemLog", "path", "/var/log/mongodb/mongod.log") in ids
    assert make_id("mongod.conf", "systemLog", "logAppend", "true") in ids
    assert make_id("mongod.conf", "storage", "journal", "enabled", "true") in ids
    assert make_id("mongod.conf", "processManagement", "fork", "true") in ids
    assert make_id("mongod.conf", "net", "bindIp", "127.0.0.1") in ids
    assert make_id("mongod.conf", "net", "port", "27017") in ids
    assert make_id("mongod.conf", "setParameter", "enableLocalhostAuthBypass", "false") in ids


def test_config_types(get_plugin):
    mongodb_plugin = get_plugin
    file = os.path.abspath("tests/files/mongod.conf")

    artifact = mongodb_plugin.parse_file(file, "mongod.conf")
    nodes = artifact.get_nodes()

    port_node = next(filter(lambda x: x.id == make_id("mongod.conf", "net", "port", "27017"), nodes))
    ip_node = next(filter(lambda x: x.id == make_id("mongod.conf", "net", "bindIp", "127.0.0.1"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("mongod.conf", "systemLog", "path", "/var/log/mongodb/mongod.log"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("mongod.conf", "storage", "journal", "enabled", "true"), nodes))

    assert port_node.config_type == ConfigType.PORT
    assert ip_node.config_type == ConfigType.IP_ADDRESS
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert path_node.config_type == ConfigType.PATH
