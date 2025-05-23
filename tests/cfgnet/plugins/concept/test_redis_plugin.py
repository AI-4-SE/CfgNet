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
from cfgnet.plugins.concept.redis_plugin import RedisPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


def test_is_responsible():
    """Test if the plugin is responsible for the given file."""
    plugin = RedisPlugin()
    
    assert plugin.is_responsible("path/to/redis.conf")
    assert not plugin.is_responsible("path/to/other.conf")


def test_get_config_type():
    """Test configuration type inference."""
    plugin = RedisPlugin()
    
    assert plugin.get_config_type("port") == ConfigType.PORT
    assert plugin.get_config_type("bind") == ConfigType.IP_ADDRESS
    assert plugin.get_config_type("dir") == ConfigType.PATH
    assert plugin.get_config_type("maxmemory") == ConfigType.SIZE
    assert plugin.get_config_type("timeout") == ConfigType.TIME
    assert plugin.get_config_type("requirepass") == ConfigType.PASSWORD
    assert plugin.get_config_type("daemonize") == ConfigType.BOOLEAN
    assert plugin.get_config_type("databases") == ConfigType.NUMBER
    assert plugin.get_config_type("loglevel") == ConfigType.TYPE


def test_parse_config_file(tmp_path):
    """Test parsing of Redis configuration file."""
    plugin = RedisPlugin()
    redis_conf = "tests/files/redis.conf"
    artifact = plugin.parse_file(redis_conf, "redis.conf")
    nodes = artifact.get_nodes()
    ids = [node.id for node in nodes]

    assert len(ids) == 19

    assert make_id("redis.conf", "file", "redis.conf") in ids
    assert make_id("redis.conf", "port", "6379") in ids
    assert make_id("redis.conf", "bind", "127.0.0.1") in ids
    assert make_id("redis.conf", "protected-mode", "yes") in ids
    assert make_id("redis.conf", "requirepass", "yourstrongpassword") in ids
    assert make_id("redis.conf", "save", "900 1") in ids
    assert make_id("redis.conf", "save", "300 10") in ids
    assert make_id("redis.conf", "save", "60 10000") in ids
    assert make_id("redis.conf", "dbfilename", "dump.rdb") in ids
    assert make_id("redis.conf", "dir", "./") in ids
    assert make_id("redis.conf", "loglevel", "notice") in ids
    assert make_id("redis.conf", "logfile", '""') in ids
    assert make_id("redis.conf", "maxmemory", "256mb") in ids
    assert make_id("redis.conf", "maxmemory-policy", "allkeys-lru") in ids
    assert make_id("redis.conf", "appendonly", "no") in ids
    assert make_id("redis.conf", "rdbcompression", "yes") in ids
    assert make_id("redis.conf", "rdbchecksum", "yes") in ids
    assert make_id("redis.conf", "timeout", "0") in ids
    assert make_id("redis.conf", "tcp-keepalive", "300") in ids
    assert make_id("redis.conf", "timeout", "0") in ids
    assert make_id("redis.conf", "tcp-keepalive", "300") in ids