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

    assert len(all_plugins) == 9


def test_get_responsible_plugin():
    plugins = PluginManager.get_plugins()

    docker_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/Dockerfile"
    )
    maven_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/pom.xml"
    )
    nodejs_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/package.json"
    )
    docker_compose_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/docker-compose.yml"
    )
    travis_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/.travis.yml"
    )
    cypress_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/cypress.json"
    )
    tsconfig_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/tsconfig.json"
    )
    poetry_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/pyproject.toml"
    )
    spring_plugin = PluginManager.get_responsible_plugin(
        plugins, "path/to/application.properties"
    )

    assert docker_plugin.concept_name == "docker"
    assert maven_plugin.concept_name == "maven"
    assert nodejs_plugin.concept_name == "nodejs"
    assert docker_compose_plugin.concept_name == "docker-compose"
    assert travis_plugin.concept_name == "travis"
    assert cypress_plugin.concept_name == "cypress"
    assert tsconfig_plugin.concept_name == "tsconfig"
    assert poetry_plugin.concept_name == "poetry"
    assert spring_plugin.concept_name == "spring"
