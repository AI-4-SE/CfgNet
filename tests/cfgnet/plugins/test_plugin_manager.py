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

    assert len(set(all_plugins)) == 2


def test_get_responsible_plugin():
    # Concept plugins
    docker_plugin = PluginManager.get_responsible_plugin("path/to/Dockerfile")
    maven_plugin = PluginManager.get_responsible_plugin("path/to/pom.xml")

    assert docker_plugin.concept_name == "docker"
    assert maven_plugin.concept_name == "maven"
