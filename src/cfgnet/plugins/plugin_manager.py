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

from typing import List, Optional

from cfgnet.plugins.plugin import Plugin
from cfgnet.plugins.concept.docker_compose_plugin import DockerComposePlugin
from cfgnet.plugins.concept.docker_plugin import DockerPlugin
from cfgnet.plugins.concept.maven_plugin import MavenPlugin
from cfgnet.plugins.concept.travis_plugin import TravisPlugin
from cfgnet.plugins.file_type.ini_plugin import IniPlugin
from cfgnet.plugins.file_type.json_plugin import JsonPlugin
from cfgnet.plugins.file_type.properties_plugin import PropertiesPlugin
from cfgnet.plugins.file_type.toml_plugin import TomlPlugin
from cfgnet.plugins.file_type.xml_plugin import XmlPlugin
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin


class PluginManager:
    """Manager for plugin implementations."""

    concept_plugins: List[Plugin] = [
        DockerPlugin(),
        MavenPlugin(),
        TravisPlugin(),
        DockerComposePlugin(),
    ]
    file_type_plugins: List[Plugin] = [
        IniPlugin(),
        PropertiesPlugin(),
        TomlPlugin(),
        YAMLPlugin(),
        XmlPlugin(),
        JsonPlugin(),
    ]

    @staticmethod
    def get_plugins() -> List:
        """Return all plugins except vcs plugins."""
        return PluginManager.concept_plugins + PluginManager.file_type_plugins

    @staticmethod
    def get_responsible_plugin(artifact_path: str) -> Optional[Plugin]:
        """
        Identify plugin that is responsible for an artifact.

        :param artifact_path: Absolute path to the artifact
        :return: Responsible plugin or None if there is no such plugin
        """
        for plugin in PluginManager.get_plugins():
            if plugin.is_enabled():
                if plugin.is_responsible(artifact_path):
                    return plugin

        return None
