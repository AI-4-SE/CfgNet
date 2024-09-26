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

from cfgnet.plugins.concept.zookeeper_plugin import ZookeeperPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = ZookeeperPlugin()
    return plugin


def test_is_responsible(get_plugin):
    zookeeper_plugin = get_plugin

    zookeeper_file = zookeeper_plugin.is_responsible("tests/files/zoo.cfg")
    not_zookeeper_file = zookeeper_plugin.is_responsible("tests/files/test.xml")

    assert zookeeper_file
    assert not not_zookeeper_file


def test_parse_zookeeper_file(get_plugin):
    zookeeper_plugin = get_plugin
    zookeeper_file = os.path.abspath("tests/files/zoo.cfg")
    artifact = zookeeper_plugin.parse_file(zookeeper_file, "zoo.cfg")

    value_nodes = artifact.get_nodes()
    ids = [node.id for node in value_nodes]

    assert artifact is not None
    assert len(value_nodes) == 21

    assert make_id("zoo.cfg", "file", "zoo.cfg") in ids
    assert make_id("zoo.cfg", "ticktime", "2000") in ids
    assert make_id("zoo.cfg", "initlimit", "20") in ids
    assert make_id("zoo.cfg", "synclimit", "10") in ids
    assert make_id("zoo.cfg", "clientport", "5181") in ids
    assert make_id("zoo.cfg", "datadir", "/opt/mapr/zkdata") in ids
    assert make_id("zoo.cfg", "maxclientcnxns", "1000") in ids
    assert make_id("zoo.cfg", "autopurge.purgeinterval", "24") in ids
    assert make_id("zoo.cfg", "superuser", "mapr") in ids
    assert make_id("zoo.cfg", "readuser", "anyone") in ids
    assert make_id("zoo.cfg", "mapr.cldbkeyfile.location", "/opt/mapr/conf/cldb.key") in ids
    assert make_id("zoo.cfg", "authmech", "MAPR-SECURITY") in ids
    assert make_id("zoo.cfg", "mapr.usemaprserverticket", "true") in ids
    assert make_id("zoo.cfg", "quorum.auth.learner.logincontext", "QuorumLearner") in ids
    assert make_id("zoo.cfg", "quorum.cnxn.threads.size", "20") in ids
    assert make_id("zoo.cfg", "sslquorum", "true") in ids
    assert make_id("zoo.cfg", "servercnxnfactory", "org.apache.zookeeper.server.NettyServerCnxnFactory") in ids
    assert make_id("zoo.cfg", "ssl.quorum.keystore.location", "/opt/mapr/conf/ssl_keystore.p12") in ids
    assert make_id("zoo.cfg", "ssl.quorum.keystore.password", "test1234!") in ids
    assert make_id("zoo.cfg", "ssl.quorum.protocol", "TLS") in ids
    assert make_id("zoo.cfg", "snapshot.trust.empty", "true") in ids
    

def test_zookeeper_config_types(get_plugin):
    zookeeper_plugin = get_plugin
    zookeeper_file = os.path.abspath("tests/files/zoo.cfg")
    artifact = zookeeper_plugin.parse_file(zookeeper_file, "zoo.cfg")
    nodes = artifact.get_nodes()

    size_node = next(filter(lambda x: x.id == make_id("zoo.cfg", "initlimit", "20",), nodes))
    port_node = next(filter(lambda x: x.id == make_id("zoo.cfg", "clientport", "5181",), nodes))
    time_node = next(filter(lambda x: x.id == make_id("zoo.cfg", "autopurge.purgeinterval", "24"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("zoo.cfg", "snapshot.trust.empty", "true"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("zoo.cfg", "ssl.quorum.keystore.location", "/opt/mapr/conf/ssl_keystore.p12"), nodes))

    assert size_node.config_type == ConfigType.SIZE
    assert port_node.config_type == ConfigType.PORT
    assert time_node.config_type == ConfigType.TIME
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert path_node.config_type == ConfigType.PATH
