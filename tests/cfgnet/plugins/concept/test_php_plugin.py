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

from cfgnet.plugins.concept.php_plugin import PhpPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = PhpPlugin()
    return plugin


def test_is_responsible(get_plugin):
    php_plugin = get_plugin

    php_file = php_plugin.is_responsible(
        "tests/files/php.ini"
    )

    no_php_file = php_plugin.is_responsible(
        "tests/files/test.ini"
    )

    assert php_file
    assert not no_php_file


def test_parsing_php_file(get_plugin):
    php_plugin = get_plugin
    file = os.path.abspath("tests/files/php.ini")

    artifact = php_plugin.parse_file(file, "php.ini")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    assert artifact is not None
    assert len(nodes) == 7

    assert make_id("php.ini", "file", "php.ini") in ids
    assert make_id("php.ini", "PHP", "memory_limit", "128M") in ids
    assert make_id("php.ini", "PHP", "error_reporting", "E_ALL | E_STRICT") in ids
    assert make_id("php.ini", "PHP", "include_path", "/test/path") in ids
    assert make_id("php.ini", "PHP", "allow_url_fopen", "On") in ids
    assert make_id("php.ini", "MySQL", "mysql.default_port", "3306") in ids
    assert make_id("php.ini", "MySQL", "mysql.default_user", "user") in ids


def test_config_types(get_plugin):
    php_plugin = get_plugin
    file = os.path.abspath("tests/files/php.ini")

    artifact = php_plugin.parse_file(file, "php.ini")
    nodes = artifact.get_nodes()

    port = next(
        filter(
            lambda x: x.id == make_id("php.ini", "MySQL", "mysql.default_port", "3306"),
            nodes,
        )
    )
    user = next(
        filter(
            lambda x: x.id == make_id("php.ini", "MySQL", "mysql.default_user", "user"),
            nodes,
        )
    )

    path = next(
        filter(
            lambda x: x.id == make_id("php.ini", "PHP", "include_path", "/test/path"),
            nodes,
        )
    )
    size = next(
        filter(
            lambda x: x.id == make_id("php.ini", "PHP", "memory_limit", "128M"),
            nodes,
        )
    )

    assert port.config_type == ConfigType.PORT
    assert user.config_type == ConfigType.USERNAME
    assert path.config_type == ConfigType.PATH
    assert size.config_type == ConfigType.SIZE
