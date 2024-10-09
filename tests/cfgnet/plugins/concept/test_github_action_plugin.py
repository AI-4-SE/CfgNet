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

from cfgnet.plugins.concept.github_actions_plugin import GitHubActionPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = GitHubActionPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/.github/workflows/ci.yml")
    assert not plugin.is_responsible("tests/files/test.yml")


def test_config_types(get_plugin):
    plugin = get_plugin
    file_name = os.path.abspath("tests/files/.github/workflows/ci.yml")
    artifact = plugin.parse_file(file_name, "ci.yml")
    nodes = artifact.get_nodes()

    name_node = next(filter(lambda x: x.id == make_id("ci.yml", "name", "Code Quality"), nodes))
    version_node = next(filter(lambda x: x.id == make_id("ci.yml", "jobs", "code_style", "steps", "with", "python-version", "3.9"), nodes))
    command_node = next(filter(lambda x: x.id == make_id("ci.yml", "jobs", "code_style", "steps", "run", "poetry install"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("ci.yml", "jobs", "code_style", "steps", "with", "virtualenvs-create", "true"), nodes))

    assert name_node.config_type == ConfigType.NAME
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert command_node.config_type == ConfigType.COMMAND
    assert boolean_node.config_type == ConfigType.BOOLEAN
