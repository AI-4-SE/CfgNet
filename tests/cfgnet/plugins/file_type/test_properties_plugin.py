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

from cfgnet.plugins.file_type.properties_plugin import PropertiesPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = PropertiesPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin
    assert plugin.is_responsible("/path/to/file.properties")
    assert not plugin.is_responsible("/path/to/file.ini")


def test_parse_properties_file(get_plugin):
    properties_file = os.path.abspath("tests/files/test.properties")
    plugin = get_plugin

    artifact = plugin.parse_file(properties_file, "test.properties")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 11
    assert make_id("test.properties", "file", "test.properties") in ids
    assert make_id("test.properties", "org.example.eq.foo", "42") in ids
    assert make_id("test.properties", "org.example.eq.bar", '"baz"') in ids
    assert make_id("test.properties", "org.example.col.foo", "42") in ids
    assert make_id("test.properties", "org.example.col.bar", '"baz"') in ids
    assert (
        make_id("test.properties", "org.example.whitespace.foo", "42") in ids
    )
    assert (
        make_id("test.properties", "org.example.whitespace.bar", "42") in ids
    )
    assert (
        make_id("test.properties", "org.example.whitespace.baz", "42    ")
        in ids
    )
    assert (
        make_id(
            "test.properties",
            "org.example.singleline",
            "Detroit,Chicago,Los Angeles",
        )
        in ids
    )
    assert (
        make_id(
            "test.properties",
            "org.example.multiline",
            "Detroit,Chicago,Los Angeles",
        )
        in ids
    )
    assert (
        make_id(
            "test.properties",
            "org.example.characters" "",
            "newline\ntab\tbackslash\\and\u263aunicode",
        )
        in ids
    )


def test_properties_file_with_sections(get_plugin):
    properties_file = os.path.abspath("tests/files/sections.properties")
    plugin = get_plugin

    artifact = plugin.parse_file(properties_file, "sections.properties")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 7
    assert make_id("sections.properties", "file", "sections.properties") in ids
    assert make_id("sections.properties", "expunge.delay", "60") in ids
    assert make_id("sections.properties", "expunge.interval", "60") in ids
    assert (
        make_id("sections.properties", "environment", "dns", "10.147.28.6")
        in ids
    )
    assert (
        make_id("sections.properties", "environment", "mshost", "localhost")
        in ids
    )
    assert (
        make_id(
            "sections.properties",
            "cloudstack",
            "private.gateway",
            "10.147.29.1",
        )
        in ids
    )
    assert (
        make_id(
            "sections.properties", "cloudstack", "guest.gateway", "10.147.31.1"
        )
        in ids
    )
