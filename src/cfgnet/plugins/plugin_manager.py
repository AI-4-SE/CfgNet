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
from cfgnet.plugins.concept.docker_plugin import DockerPlugin
from cfgnet.plugins.concept.maven_plugin import MavenPlugin
from cfgnet.plugins.concept.nodejs_plugin import NodejsPlugin
from cfgnet.plugins.concept.cypress_plugin import CypressPlugin
from cfgnet.plugins.concept.tsconfig_plugin import TsconfigPlugin
from cfgnet.plugins.concept.travis_plugin import TravisPlugin
from cfgnet.plugins.concept.docker_compose_plugin import DockerComposePlugin
from cfgnet.plugins.concept.pyproject_plugin import PyprojectPlugin
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin
from cfgnet.plugins.file_type.toml_plugin import TomlPlugin
from cfgnet.plugins.source_code.tensorflow_plugin import TensorflowPLugin
from cfgnet.plugins.source_code.pytorch_plugin import PytorchPLugin


class PluginManager:
    """Manager for plugin implementations."""

    concept_plugins: List[Plugin] = [
        DockerPlugin(),
        MavenPlugin(),
        NodejsPlugin(),
        CypressPlugin(),
        TsconfigPlugin(),
        DockerComposePlugin(),
        TravisPlugin(),
        PyprojectPlugin(),
    ]

    file_type_plugins: List[Plugin] = [
        ConfigParserPlugin(),
        YAMLPlugin(),
        TomlPlugin(),
    ]

    source_code_plugins: List[Plugin] = [
        TensorflowPLugin(),
        PytorchPLugin(),
    ]

    @staticmethod
    def get_plugins(only_concept_plugins: bool = False) -> List:
        """Return all plugins except source code plugins."""
        if only_concept_plugins:
            return PluginManager.concept_plugins

        return PluginManager.concept_plugins + PluginManager.file_type_plugins

    @staticmethod
    def get_responsible_plugin(
        plugins: List[Plugin], artifact_path: str
    ) -> Optional[Plugin]:
        """
        Identify plugin that is responsible for an artifact.

        :param artifact_path: Absolute path to the artifact
        :return: Responsible plugin or None if there is no such plugin
        """
        for plugin in plugins:
            if plugin.is_responsible(artifact_path):
                return plugin

        return None
