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

from cfgnet.plugins.concept.angular_plugin import AngularPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = AngularPlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    angular_file = plugin.is_responsible("tests/files/angular.json")
    no_angular_file = plugin.is_responsible("tests/files/test.json")

    assert angular_file
    assert not no_angular_file


def test_parse_angular_file(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/angular.json")

    artifact = plugin.parse_file(file, "angular.json")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}
    
    assert artifact is not None
    assert len(nodes) == 13

    assert make_id("angular.json", "file", "angular.json") in ids
    assert make_id("angular.json", "$schema", "./node_modules/@angular/cli/lib/config/schema.json") in ids
    assert make_id("angular.json", "version", "1") in ids
    assert make_id("angular.json", "projects", "my-app", "architect", "configurations", "production", "fileReplacements", "replace", "src/environments/environment.ts") in ids
    assert make_id("angular.json", "projects", "my-app", "architect", "configurations", "production", "fileReplacements", "with", "src/environments/environment.prod.ts") in ids
    assert make_id("angular.json", "projects", "my-app", "test", "builder", "@angular-devkit/build-angular:karma") in ids
    assert make_id("angular.json", "projects", "my-app", "projectType", "application") in ids
    assert make_id("angular.json", "projects", "my-app", "architect", "configurations", "production", "buildOptimizer", "True") in ids
    assert make_id("angular.json", "projects", "my-app", "architect", "configurations", "production", "fileReplacements", "with", "src/environments/environment.prod.ts") in ids
    assert make_id("angular.json", "projects", "my-app", "test", "options", "main", "src/test.ts") in ids
    assert make_id("angular.json", "projects", "my-app", "sourceRoot", "src") in ids
    assert make_id("angular.json", "projects", "my-app", "root", "") in ids
    assert make_id("angular.json", "newProjectRoot", "projects") in ids


def test_config_types(get_plugin):
    plugin = get_plugin
    file = os.path.abspath("tests/files/angular.json")
    artifact = plugin.parse_file(file, "angular.json")
    nodes = artifact.get_nodes()

    version_node = next(filter(lambda x: x.id == make_id("angular.json", "version", "1"), nodes))
    path_node = next(filter(lambda x: x.id == make_id("angular.json", "projects", "my-app", "sourceRoot", "src"), nodes))
    path2_node = next(filter(lambda x: x.id == make_id("angular.json", "projects", "my-app", "architect", "configurations", "production", "fileReplacements", "with", "src/environments/environment.prod.ts"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("angular.json", "projects", "my-app", "architect", "configurations", "production", "buildOptimizer", "True"), nodes))
    
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert path_node.config_type == ConfigType.PATH
    assert path2_node.config_type == ConfigType.PATH
    assert boolean_node.config_type == ConfigType.BOOLEAN
