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

from cfgnet.plugins.concept.anisible_plugin import AnsiblePlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = AnsiblePlugin()
    return plugin


def test_is_responsible(get_plugin):
    ansible_plugin = get_plugin

    ansible_file = ansible_plugin.is_responsible(
        "tests/files/ansible.cfg"
    )

    no_ansible_file = ansible_plugin.is_responsible(
        "tests/files/test.cfg"
    )

    assert ansible_file
    assert not no_ansible_file


def test_parsing_mysql_file_file(get_plugin):
    php_plugin = get_plugin
    file = os.path.abspath("tests/files/ansible.cfg")

    artifact = php_plugin.parse_file(file, "ansible.cfg")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    assert artifact is not None
    assert make_id("ansible.cfg", "file", "ansible.cfg") in ids
    assert make_id("ansible.cfg", "defaults", "action_warnings", "True") in ids
    assert make_id("ansible.cfg", "defaults", "home", "~/.ansible") in ids
    assert make_id("ansible.cfg", "defaults", "fact_caching_timeout", "86400") in ids
    assert make_id("ansible.cfg", "defaults", "executable", "/bin/sh") in ids
    assert make_id("ansible.cfg", "defaults", "internal_poll_interval", "0.001") in ids
    assert make_id("ansible.cfg", "galaxy", "cache_dir", '{{ ANSIBLE_HOME ~ /galaxy_cache }}') in ids
    assert make_id("ansible.cfg", "galaxy", "collection_skeleton_ignore", "['^.git$', '^.*/.git_keep$']") in ids
    assert make_id("ansible.cfg", "galaxy", "server", "https://test.ansible.com") in ids
    assert make_id("ansible.cfg", "jinja2", "dont_type_filters", "['string', 'ppretty', 'json']") in ids
    assert make_id("ansible.cfg", "runas_become_plugin", "password", "test123") in ids
    assert make_id("ansible.cfg", "runas_become_plugin", "user", "user") in ids


def test_config_types(get_plugin):
    ansible_plugin = get_plugin
    ansible_file = os.path.abspath("tests/files/ansible.cfg")
    artifact = ansible_plugin.parse_file(ansible_file, "ansible.cfg")
    nodes = artifact.get_nodes()

    path_node = next(filter(lambda x: x.id == make_id("ansible.cfg", "defaults", "home", "~/.ansible"), nodes))
    timeout_node = next(filter(lambda x: x.id == make_id("ansible.cfg", "defaults", "fact_caching_timeout", "86400"), nodes))
    number_node = next(filter(lambda x: x.id == make_id("ansible.cfg", "defaults", "internal_poll_interval", "0.001"), nodes))
    url_node = next(filter(lambda x: x.id == make_id("ansible.cfg", "galaxy", "server", "https://test.ansible.com"), nodes))
    password_node = next(filter(lambda x: x.id == make_id("ansible.cfg", "runas_become_plugin", "password", "test123"), nodes))
    user_node = next(filter(lambda x: x.id == make_id("ansible.cfg", "runas_become_plugin", "user", "user"), nodes))

    assert path_node.config_type == ConfigType.PATH
    assert timeout_node.config_type == ConfigType.TIME
    assert number_node.config_type == ConfigType.PATH
    assert url_node.config_type == ConfigType.URL
    assert user_node.config_type == ConfigType.USERNAME
    assert password_node.config_type == ConfigType.PASSWORD
