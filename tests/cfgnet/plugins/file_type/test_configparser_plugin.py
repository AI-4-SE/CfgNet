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

from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = ConfigParserPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin
    assert plugin.is_responsible("/path/to/tox.ini")
    assert plugin.is_responsible("/path/to/file.properties")
    assert not plugin.is_responsible("/path/to/lorem.ipsum")


def test_parse_ini_file(get_plugin):
    """Test for parsing an ini file with configparser."""
    ini_file = os.path.abspath("tests/files/test.ini")
    plugin = get_plugin

    artifact = plugin.parse_file(ini_file, "test.ini")
    nodes = artifact.get_nodes()

    assert artifact is not None
    assert len(nodes) == 9
    assert nodes[0].id == make_id("test.ini", "file", "test.ini")
    assert nodes[1].id == make_id("test.ini", "abouttext", "%blurb")
    assert nodes[2].id == make_id("test.ini", "featureimage", "eclipse32.png")
    assert nodes[3].id == make_id(
        "test.ini", "welcomepage", "$nl$/welcome.xml"
    )
    assert nodes[4].id == make_id(
        "test.ini", "GJK_Browscap_Version", "version", "4476"
    )
    assert nodes[5].id == make_id(
        "test.ini",
        "GJK_Browscap_Version",
        "released",
        "Wed 17 Jun 2009 06:30:21 -0000",
    )
    assert nodes[6].id == make_id(
        "test.ini", "multiline values", "option1", "value1\nvalue2"
    )
    assert nodes[7].id == make_id(
        "test.ini", "multiline values", "option2", "value1\nvalue2"
    )
    assert nodes[8].id == make_id(
        "test.ini", "DefaultProperties", "browser", "DefaultProperties"
    )


def test_parse_tox_file(get_plugin):
    """Test for parsing a tox file with configparser."""
    properties_file = os.path.abspath("tests/files/tox.ini")
    plugin = get_plugin

    artifact = plugin.parse_file(properties_file, "tox.ini")
    nodes = artifact.get_nodes()

    assert artifact is not None
    assert len(nodes) == 8
    assert nodes[0].id == make_id("tox.ini", "file", "tox.ini")
    assert nodes[1].id == make_id("tox.ini", "tox", "isolated_build", "true")
    assert nodes[2].id == make_id(
        "tox.ini", "tox", "envlist", "['py36', 'py37', 'py38']"
    )
    assert nodes[3].id == make_id(
        "tox.ini", "gh-actions", "python", "3.6: py36\n3.7: py37\n3.8: py38"
    )
    assert nodes[4].id == make_id(
        "tox.ini", "testenv", "whitelist_externals", "poetry"
    )
    assert nodes[5].id == make_id(
        "tox.ini", "testenv", "deps", "pytest\npytest-cov\ncoverage"
    )
    assert nodes[6].id == make_id(
        "tox.ini",
        "testenv",
        "test",
        "pytest --cov-append --cov-report=html --cov=src tests",
    )
    assert nodes[7].id == make_id(
        "tox.ini", "testenv", "command", "py.test -v --capture=sys"
    )


def test_parse_properties_file(get_plugin):
    properties_file = os.path.abspath("tests/files/test.properties")
    plugin = get_plugin

    artifact = plugin.parse_file(properties_file, "test.properties")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert make_id("test.properties", "file", "test.properties") in ids
    assert make_id("test.properties", "org.example.eq.foo", "42") in ids
    assert make_id("test.properties", "org.example.eq.bar", "baz") in ids
    assert make_id("test.properties", "org.example.col.foo", "42") in ids
    assert make_id("test.properties", "org.example.col.bar", "baz") in ids
    assert (
        make_id("test.properties", "org.example.whitespace.foo", "42") in ids
    )
    assert (
        make_id("test.properties", "org.example.whitespace.bar", "42") in ids
    )
    assert (
        make_id("test.properties", "org.example.whitespace.baz", "42")
        in ids
    )
    assert (
        make_id(
            "test.properties",
            "org.example.multiline",
            "['Detroit', 'Chicago', 'Los Angeles']",
        )
        in ids
    )
    assert len(ids) == 9


def test_properties_file_with_sections(get_plugin):
    properties_file = os.path.abspath("tests/files/sections.properties")
    plugin = get_plugin

    artifact = plugin.parse_file(properties_file, "sections.properties")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
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
    assert len(ids) == 7
