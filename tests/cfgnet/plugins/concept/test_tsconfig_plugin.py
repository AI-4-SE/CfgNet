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

from cfgnet.plugins.concept.tsconfig_plugin import TsconfigPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = TsconfigPlugin()
    return plugin


def test_is_responsible(get_plugin):
    tsconfig_plugin = get_plugin

    tsconfig_file = tsconfig_plugin.is_responsible("tests/files/tsconfig.json")
    no_tsconfig_file = tsconfig_plugin.is_responsible("tests/files/cypress.json")

    assert tsconfig_file
    assert not no_tsconfig_file


def test_parse_tsconfig_file(get_plugin):
    tsconfig_plugin = get_plugin
    file = os.path.abspath("tests/files/tsconfig.json")

    artifact = tsconfig_plugin.parse_file(file, "tsconfig.json")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 7

    assert make_id("tsconfig.json", "file", "tsconfig.json") in ids
    assert (
        make_id("tsconfig.json", "compilerOptions", "module", "system") in ids
    )
    assert (
        make_id(
            "tsconfig.json", "compilerOptions", "preserveConstEnums", "True"
        )
        in ids
    )
    assert (
        make_id("tsconfig.json", "compilerOptions", "outFile", "../../test.js")
        in ids
    )
    assert (
        make_id("tsconfig.json", "compilerOptions", "sourceMap", "True") in ids
    )
    assert (
        make_id("tsconfig.json", "include", "include/src/**/*", "src/**/*")
        in ids
    )
    assert (
        make_id(
            "tsconfig.json", "exclude", "exclude/node_modules", "node_modules"
        )
        in ids
    )


def test_config_types(get_plugin):
    tsconfig_plugin = get_plugin
    file = os.path.abspath("tests/files/tsconfig.json")

    artifact = tsconfig_plugin.parse_file(file, "tsconfig.json")
    nodes = artifact.get_nodes()

    boolean_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "tsconfig.json",
                "compilerOptions",
                "preserveConstEnums",
                "True",
            ),
            nodes,
        )
    )
    path_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "tsconfig.json", "compilerOptions", "outFile", "../../test.js"
            ),
            nodes,
        )
    )
    exclude_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "tsconfig.json",
                "exclude",
                "exclude/node_modules",
                "node_modules",
            ),
            nodes,
        )
    )

    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert path_node.config_type == ConfigType.PATH
    assert exclude_node.config_type == ConfigType.PATH
