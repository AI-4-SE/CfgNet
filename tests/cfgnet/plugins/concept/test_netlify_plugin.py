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
from cfgnet.plugins.concept.netlify_plugin import NetlifyPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    """Get the Netlify plugin."""
    return NetlifyPlugin()


def test_is_responsible(get_plugin):
    """Test if the plugin is responsible for the given file."""
    assert get_plugin.is_responsible("netlify.toml")
    assert get_plugin.is_responsible("/path/to/netlify.toml")
    assert not get_plugin.is_responsible("other.toml")
    assert not get_plugin.is_responsible("netlify.yml")


def test_parse_netlify_file(get_plugin):
    """Test parsing of a netlify.toml file."""
    test_file = os.path.join("tests/files/netlify.toml")
    netlify_plugin = get_plugin
    artifact = netlify_plugin.parse_file(test_file, "netlify.toml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert len(nodes) == 8
    assert make_id("netlify.toml", "file", "netlify.toml") in ids
    assert make_id("netlify.toml", "build", "command", "npm run build") in ids
    assert make_id("netlify.toml", "build", "publish", "dist") in ids
    assert make_id("netlify.toml", "build", "environment", "NODE_VERSION", "18") in ids
    assert make_id("netlify.toml", "redirects", "from", "/old-path") in ids
    assert make_id("netlify.toml", "redirects", "to", "/new-path") in ids
    assert make_id("netlify.toml", "redirects", "status", "301") in ids


def test_config_types(get_plugin):
    netlify_plugin = get_plugin
    netlify_file = os.path.abspath("tests/files/netlify.toml")
    artifact = netlify_plugin.parse_file(netlify_file, "netlify.toml")
    nodes = artifact.get_nodes()

    command_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "netlify.toml",
                "build",
                "command",
                "npm run build",
            ),
            nodes,
        )
    )

    path_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "netlify.toml",
                "build",
                "publish",
                "dist",
            ),
            nodes,
        )
    )

    assert command_node.config_type == ConfigType.COMMAND
    assert path_node.config_type == ConfigType.PATH
