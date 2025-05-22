# This file is part of the CfgNet network module.
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
from typing import Optional
from cfgnet.config_types.config_types import ConfigType
from cfgnet.config_types.type_registry import TypeRegistry
from cfgnet.network.nodes import ArtifactNode, ProjectNode
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin


class KubernetesPlugin(YAMLPlugin):
    """Plugin for parsing Kubernetes configuration files."""

    def __init__(self):
        super().__init__("kubernetes")
        self.type_registry = TypeRegistry()

    def is_responsible(self, abs_file_path: str) -> bool:
        """
        Check if this plugin is responsible for the given file.

        :param abs_file_path: Absolute path to the file
        :return: True if the plugin is responsible for the file, False otherwise
        """
        # First check if it's a YAML file
        if not super().is_responsible(abs_file_path):
            return False

        # Check for concrete Kubernetes file names
        kubernetes_file_patterns = {
            "deployment.yaml",
            "service.yaml",
            "configmap.yaml",
            "secret.yaml",
            "ingress.yaml",
            "pod.yaml",
            "statefulset.yaml",
            "daemonset.yaml",
            "job.yaml",
            "cronjob.yaml",
            "persistentvolume.yaml",
            "persistentvolumeclaim.yaml",
            "namespace.yaml",
            "role.yaml",
            "rolebinding.yaml",
            "serviceaccount.yaml",
            "networkpolicy.yaml",
            "horizontalpodautoscaler.yaml",
            "verticalpodautoscaler.yaml",
            "customresourcedefinition.yaml",
        }

        file_name = os.path.basename(abs_file_path)
        return file_name in kubernetes_file_patterns

    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        """
        Get the configuration type for a given option name and value.

        :param option_name: Name of the option
        :param value: Value of the option
        :return: Configuration type
        """
        return self.type_registry.infer_type(option_name, value, "kubernetes")