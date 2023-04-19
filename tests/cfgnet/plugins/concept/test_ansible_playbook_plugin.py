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

from cfgnet.plugins.concept.ansible_playbook_plugin import AnsiblePlaybookPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = AnsiblePlaybookPlugin()
    return plugin


def test_is_responsible(get_plugin):
    ansible_playbook_plugin = get_plugin

    master_playbook = ansible_playbook_plugin.is_responsible(
        "tests/files/site.yml"
    )

    playbook = ansible_playbook_plugin.is_responsible(
        "tests/files/dbserver-playbook.yml"
    )

    playbook_dir = ansible_playbook_plugin.is_responsible(
        "tests/playbooks/test.yml"
    )

    no_ansible_file = ansible_playbook_plugin.is_responsible(
        "tests/files/test.yml"
    )

    assert master_playbook
    assert playbook
    assert playbook_dir
    assert not no_ansible_file


def test_parsing_mysql_file_file(get_plugin):
    ansible_playbook_plugin = get_plugin
    file = os.path.abspath("tests/files/playbook.yml")

    artifact = ansible_playbook_plugin.parse_file(file, "playbook.yml")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    assert artifact is not None
    assert len(nodes) == 34
    assert make_id("playbook.yml", "offset:0", "remote_user", "root") in ids
    assert make_id("playbook.yml", "offset:0", "tasks", "offset:0", "ansible.builtin.yum", "name", "httpd") in ids
    assert make_id("playbook.yml", "offset:2", "tasks", "offset:0", "win_get_url", "url", "https://test.html") in ids
    assert make_id("playbook.yml", "offset:3", "tasks", "offset:0", "win_user", "password", "test123") in ids
    assert make_id("playbook.yml", "offset:3", "tasks", "offset:0", "win_user", "state", "present") in ids
    assert make_id("playbook.yml", "offset:4", "tasks", "offset:0", "ansible.builtin.git", "dest", "/home/www") in ids
    assert make_id("playbook.yml", "offset:4", "tasks", "offset:0", "ansible.builtin.git", "accept_hostkey", "true") in ids
    assert make_id("playbook.yml", "offset:4", "tasks", "offset:0", "ansible.builtin.git", "version", "master") in ids
    assert make_id("playbook.yml", "offset:4", "hosts", "localhost") in ids


def test_config_types(get_plugin):
    ansible_playbook_plugin = get_plugin
    playbook_file = os.path.abspath("tests/files/playbook.yml")
    artifact = ansible_playbook_plugin.parse_file(playbook_file, "playbook.yml")
    nodes = artifact.get_nodes()

    path_node = next(filter(lambda x: x.id == make_id("playbook.yml", "offset:4", "tasks", "offset:0", "ansible.builtin.git", "dest", "/home/www"), nodes))
    name_node = next(filter(lambda x: x.id == make_id("playbook.yml", "offset:0", "tasks", "offset:0", "ansible.builtin.yum", "name", "httpd"), nodes))
    state_node = next(filter(lambda x: x.id == make_id("playbook.yml", "offset:3", "tasks", "offset:0", "win_user", "state", "present"), nodes))
    url_node = next(filter(lambda x: x.id == make_id("playbook.yml", "offset:2", "tasks", "offset:0", "win_get_url", "url", "https://test.html"), nodes))
    password_node = next(filter(lambda x: x.id == make_id("playbook.yml", "offset:3", "tasks", "offset:0", "win_user", "password", "test123"), nodes))
    host_node = next(filter(lambda x: x.id == make_id("playbook.yml", "offset:4", "hosts", "localhost"), nodes))

    assert path_node.config_type == ConfigType.PATH
    assert name_node.config_type == ConfigType.NAME
    assert state_node.config_type == ConfigType.STATE
    assert url_node.config_type == ConfigType.URL
    assert host_node.config_type == ConfigType.HOST
    assert password_node.config_type == ConfigType.PASSWORD
