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

from cfgnet.plugins.plugin_manager import PluginManager


def test_get_all_plugins():
    all_plugins = PluginManager.get_plugins()

    assert len(set(all_plugins)) == 8


def test_get_responsible_plugin():
    docker_plugin = PluginManager.get_responsible_plugin("path/to/Dockerfile")
    maven_plugin = PluginManager.get_responsible_plugin("path/to/pom.xml")
    nodejs_plugin = PluginManager.get_responsible_plugin(
        "path/to/package.json"
    )
    docker_compose_plugin = PluginManager.get_responsible_plugin(
        "path/to/docker-compose.yml"
    )
    travis_plugin = PluginManager.get_responsible_plugin("path/to/.travis.yml")
    yaml_plugin = PluginManager.get_responsible_plugin("path/to/test.yaml")
    ini_plugin = PluginManager.get_responsible_plugin("path/to/tox.ini")
    properties_plugin = PluginManager.get_responsible_plugin(
        "path/to/applications.properties"
    )
    toml_plugin = PluginManager.get_responsible_plugin("path/to/test.toml")

    assert docker_plugin.concept_name == "docker"
    assert maven_plugin.concept_name == "maven"
    assert nodejs_plugin.concept_name == "nodejs"
    assert docker_compose_plugin.concept_name == "docker-compose"
    assert travis_plugin.concept_name == "travis"
    assert yaml_plugin.concept_name == "yaml"
    assert ini_plugin.concept_name == "configparser"
    assert properties_plugin.concept_name == "configparser"
    assert toml_plugin.concept_name == "toml"
