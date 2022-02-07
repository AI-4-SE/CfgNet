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


from cfgnet.config_types.config_types import ConfigType
from cfgnet.network.nodes import OptionNode, ValueNode


def test_config_types_option_value():
    option_port = OptionNode("port", "1", ConfigType.PORT)
    port = ValueNode("8000")
    option_port.add_child(port)

    assert option_port.config_type == ConfigType.PORT
    assert port.config_type == ConfigType.PORT


def test_config_types_nested_option():

    option_path = OptionNode("path", "1", ConfigType.PATH)
    nested_option = OptionNode("port", "2", ConfigType.PORT)
    option_path.add_child(nested_option)
    port = ValueNode("8000")
    nested_option.add_child(port)

    assert option_path.config_type == ConfigType.PATH
    assert nested_option.config_type == ConfigType.PORT
    assert port.config_type == ConfigType.PORT


def test_config_types_nested_options_unknown():

    option_dependency = OptionNode(
        "dependencies", "1", ConfigType.VERSION_NUMBER
    )
    nested_option = OptionNode("pylint", "2")
    option_dependency.add_child(nested_option)
    version = ValueNode("3.2.1")
    nested_option.add_child(version)

    assert option_dependency.config_type == ConfigType.VERSION_NUMBER
    assert nested_option.config_type == ConfigType.VERSION_NUMBER
    assert version.config_type == ConfigType.VERSION_NUMBER


def test_file_paths():
    abs_file_path = "/home/user/github/cfgnet/src/launcher.py"
    rel_file_path = "../cfgnet/src/network/network.py"
    no_file_path = "test_string"

    assert ConfigType.is_filepath(abs_file_path)
    assert ConfigType.is_filepath(rel_file_path)
    assert not ConfigType.is_filepath(no_file_path)


def test_domain_name():
    domain_name = "http://www.example.com"
    not_domain_name = "example.com"

    assert ConfigType.is_domain_name(domain_name)
    assert not ConfigType.is_domain_name(not_domain_name)


def test_boolean():
    boolean_true = True
    boolean_on = "on"
    boolean_no = "No"
    not_boolean = "test"

    assert ConfigType.is_boolean(str(boolean_true))
    assert ConfigType.is_boolean(boolean_on)
    assert ConfigType.is_boolean(boolean_no)
    assert not ConfigType.is_boolean(not_boolean)


def test_ip_address():
    ip1 = "127.0.0.1"
    ip2 = "255.255.255.255"
    not_ip = "1.1.1.01"

    assert ConfigType.is_ip_address(ip1)
    assert ConfigType.is_ip_address(ip2)
    assert not ConfigType.is_ip_address(not_ip)


def test_email():
    email = "user2@gmail.com"
    not_email = "example.com"

    assert ConfigType.is_email(email)
    assert not ConfigType.is_email(not_email)


def test_port():
    port = "8080"
    not_port = "-200"

    assert ConfigType.is_port(port)
    assert not ConfigType.is_port(not_port)


def test_version_number():
    version = "1.1.1"
    version_snapshot = "3.9.0-SNAPSHOT"
    not_version = "0.1.0.1"

    assert ConfigType.is_version_number(version)
    assert ConfigType.is_version_number(version_snapshot)
    assert not ConfigType.is_version_number(not_version)
