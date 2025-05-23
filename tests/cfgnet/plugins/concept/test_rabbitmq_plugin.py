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
from cfgnet.plugins.concept.rabbitmq_plugin import RabbitMQPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id
from cfgnet.network.nodes import ValueNode


def test_is_responsible():
    """Test if the plugin is responsible for the given file."""
    plugin = RabbitMQPlugin()
    
    assert plugin.is_responsible("path/to/rabbitmq.conf")
    assert not plugin.is_responsible("path/to/other.conf")


def test_get_config_type():
    """Test configuration type inference."""
    plugin = RabbitMQPlugin()
    
    assert plugin.get_config_type("listeners.tcp.default") == ConfigType.PORT
    assert plugin.get_config_type("cluster_nodes") == ConfigType.TYPE
    assert plugin.get_config_type("log.file") == ConfigType.PATH
    assert plugin.get_config_type("vm_memory_high_watermark") == ConfigType.SIZE
    assert plugin.get_config_type("heartbeat") == ConfigType.NUMBER
    assert plugin.get_config_type("default_pass") == ConfigType.PASSWORD
    assert plugin.get_config_type("loopback_users") == ConfigType.BOOLEAN
    assert plugin.get_config_type("auth_mechanisms") == ConfigType.TYPE


def test_parse_config_file():
    """Test parsing of RabbitMQ configuration file."""
    plugin = RabbitMQPlugin()
    rabbitmq_file = "tests/files/rabbitmq.conf"

    artifact = plugin.parse_file(rabbitmq_file, "rabbitmq.conf")    
    
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    print(ids)

    assert artifact is not None
    assert len(nodes) == 9

    # Test Pod resource
    assert make_id("rabbitmq.conf", "file", "rabbitmq.conf") in ids
    assert make_id("rabbitmq.conf", "listeners.tcp.default", "5672") in ids
    assert make_id("rabbitmq.conf", "loopback_users.guest", "false") in ids
    assert make_id("rabbitmq.conf", "default_user", "myuser") in ids
    assert make_id("rabbitmq.conf", "default_pass", "mypassword") in ids
    assert make_id("rabbitmq.conf", "log.console", "true") in ids
    assert make_id("rabbitmq.conf", "log.console.level", "info") in ids
    assert make_id("rabbitmq.conf", "management.listener.port", "15672") in ids
    assert make_id("rabbitmq.conf", "management.listener.ip", "0.0.0.0") in ids