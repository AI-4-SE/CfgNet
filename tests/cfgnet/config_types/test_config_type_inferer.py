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


from cfgnet.config_types.config_type_inferer import ConfigTypeInferer
from cfgnet.config_types.config_types import ConfigType


def test_get_config_type():

    assert ConfigTypeInferer.get_config_type("port", "8080") == ConfigType.PORT
    assert ConfigTypeInferer.get_config_type("max_length", "100") == ConfigType.SIZE
    assert ConfigTypeInferer.get_config_type("usr", "test") == ConfigType.USERNAME
    assert ConfigTypeInferer.get_config_type("timeout", "10") == ConfigType.TIME
    assert ConfigTypeInferer.get_config_type("file_path", "target/main.jar") == ConfigType.PATH
    assert ConfigTypeInferer.get_config_type("url", "https://test.com/") == ConfigType.URL
    assert ConfigTypeInferer.get_config_type("ip", "192.168.34.164") == ConfigType.IP_ADDRESS
    assert ConfigTypeInferer.get_config_type("email", "test@gmail.com") == ConfigType.EMAIL
    assert ConfigTypeInferer.get_config_type("speed", "1 bps") == ConfigType.SPEED
    assert ConfigTypeInferer.get_config_type("memory", "516 GB") == ConfigType.MEMORY
    assert ConfigTypeInferer.get_config_type("artifact_id", "artifact_name") == ConfigType.ID
    assert ConfigTypeInferer.get_config_type("disable_button", "true") == ConfigType.MODE
    assert ConfigTypeInferer.get_config_type("password", "test1234") == ConfigType.PASSWORD
    assert ConfigTypeInferer.get_config_type("count_leafs", "5") == ConfigType.COUNT
    assert ConfigTypeInferer.get_config_type("domain_name", "https://192.168.34.164:8080") == ConfigType.DOMAIN_NAME
    assert ConfigTypeInferer.get_config_type("language", "DE") == ConfigType.LANGUAGE
    assert ConfigTypeInferer.get_config_type("server_name", "MainServer15") == ConfigType.NAME
    assert ConfigTypeInferer.get_config_type("number", "123123123") == ConfigType.NUMBER
    assert ConfigTypeInferer.get_config_type("version_number", "1.12.12") == ConfigType.VERSION_NUMBER
    assert ConfigTypeInferer.get_config_type("test", "true") == ConfigType.BOOLEAN


def test_file_paths():
    abs_file_path = "/home/user/github/cfgnet/src/launcher.py"
    rel_file_path = "../cfgnet/src/network/network.py"
    no_file_path = "test_string"

    assert ConfigTypeInferer.get_config_type("", abs_file_path) == ConfigType.PATH
    assert ConfigTypeInferer.get_config_type("", rel_file_path) == ConfigType.PATH
    assert ConfigTypeInferer.get_config_type("", no_file_path) == ConfigType.UNKNOWN


def test_port():
    port = "8080"
    not_port = "-200"

    assert ConfigTypeInferer.get_config_type("port", port) == ConfigType.PORT
    assert ConfigTypeInferer.get_config_type("", not_port) == ConfigType.UNKNOWN


def test_version_number():
    version = "1.1.1"
    version_snapshot = "3.9.0-SNAPSHOT"

    assert ConfigTypeInferer.get_config_type("version", version) == ConfigType.VERSION_NUMBER
    assert ConfigTypeInferer.get_config_type("version_snapshot", version_snapshot) == ConfigType.VERSION_NUMBER
