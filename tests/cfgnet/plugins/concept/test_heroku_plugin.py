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

import pytest
from cfgnet.plugins.concept.heroku_plugin import HerokuPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    """Get the Heroku plugin."""
    return HerokuPlugin()


def test_is_responsible(get_plugin):
    """Test if the plugin is responsible for the given file."""
    assert get_plugin.is_responsible("heroku.yml")
    assert get_plugin.is_responsible("/path/to/heroku.yml")
    assert not get_plugin.is_responsible("other.yml")
    assert not get_plugin.is_responsible("heroku.yaml")


def test_parse_heroku_file(get_plugin):
    """Test parsing of a heroku.yml file."""
    test_file = "tests/files/heroku.yml"
    artifact = get_plugin.parse_file(test_file, "heroku.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert artifact.concept_name == "heroku"
    assert len(nodes) == 3

    assert make_id("heroku.yml", "file", "heroku.yml") in ids
    assert make_id("heroku.yml", "build", "docker", "web", "Dockerfile") in ids
    assert make_id("heroku.yml", "run", "web", "bundle exec rails server -p $PORT") in ids
