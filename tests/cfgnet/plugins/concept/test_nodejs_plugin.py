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

from cfgnet.plugins.concept.nodejs_plugin import NodejsPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = NodejsPlugin()
    return plugin


def test_is_responsible(get_plugin):
    nodejs_plugin = get_plugin

    package_json_file = nodejs_plugin.is_responsible(
        "tests/files/package.json"
    )
    no_package_json_file = nodejs_plugin.is_responsible(
        "tests/files/test,json"
    )

    assert package_json_file
    assert not no_package_json_file


def test_parsing_package_json_file(get_plugin):
    nodejs_plugin = get_plugin
    file = os.path.abspath("tests/files/package.json")

    artifact = nodejs_plugin.parse_file(file, "package.json")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 11

    assert make_id("package.json", "file", "package.json") in ids
    assert make_id("package.json", "name", "node-js-sample") in ids
    assert make_id("package.json", "version", "0.2.0") in ids
    assert make_id("package.json", "description", "Example Project") in ids
    assert make_id("package.json", "main", "index.js") in ids

    assert make_id("package.json", "scripts", "start", "node index.js") in ids
    assert make_id("package.json", "dependencies", "express", "^4.13.3") in ids
    assert (
        make_id(
            "package.json", "repo", "url", "https://github.com/example/example"
        )
        in ids
    )
    assert make_id("package.json", "keywords", "keywords/node", "node") in ids
    assert (
        make_id("package.json", "keywords", "keywords/heroku", "heroku") in ids
    )
    assert (
        make_id("package.json", "keywords", "keywords/express", "express")
        in ids
    )
