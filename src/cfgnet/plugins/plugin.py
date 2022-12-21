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

import abc
import logging
import os

from typing import Optional
from cfgnet.network.nodes import ProjectNode, ArtifactNode


class Plugin(abc.ABC):
    """Plugin for parsing a specific configuration concept."""

    def __init__(self, concept_name: str, threshold: Optional[int] = None):
        """
        Initialize plugin.

        :param concept_name: Name of the concept.
        :param threshold: file size threshold, by default None.
        """
        self.concept_name: str = concept_name
        self.file_size_threshold: Optional[int] = threshold

    @abc.abstractmethod
    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        """
        Parse the file to extract configuration options and values.

        :param abs_file_path: Absolute path to the file
        :param rel_file_path: Relative path to the file
        :param root: The ArtifactNode will be appended to this ProjectNode
        :return: ArtifactNode that will be added to the configuration network
        """

    @abc.abstractmethod
    def is_responsible(self, abs_file_path: str) -> bool:
        """
        Return true if the plugin is responsible for the file.

        :param abs_file_path: Absolute path to the file.
        """

    def parse_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode] = None,
    ) -> Optional[ArtifactNode]:
        """
        Parse a configuration file to extract configuration options and values.

        Returns a sub-network using the artifact node as root. The artifact node
        is used in tests to check the plugins.
        :param abs_file_path: absolute file path
        :param rel_file_path: relative file path
        :param root: project root of the file to parse
        :returns: artifact node that represents a sub-network of the parsed file
        """
        if self.is_responsible(abs_file_path):
            self._warn_if_large_file(abs_file_path)

            artifact = self._parse_config_file(
                abs_file_path, rel_file_path, root
            )
            return artifact

        return None

    def _warn_if_large_file(self, file_path: str) -> None:
        """Log a warning if the file size in bytes exceeds the threshold."""
        if not self.file_size_threshold:
            return
        if (
            os.path.exists(file_path)
            and os.path.getsize(file_path) > self.file_size_threshold
        ):
            logging.warning(
                "Large file '%s' might not be configuration.", file_path
            )
