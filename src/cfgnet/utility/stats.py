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
import json
import logging
from typing import Dict
from cfgnet.network.network import Network
from cfgnet.network.nodes import ArtifactNode, ValueNode


class Stats:
    """Module to extract hyperparameter."""

    @staticmethod
    def get_stats(network) -> None:
        """Calculate different kinds of statistics."""
        if not os.path.isdir(network.cfg.statistic_path()):
            os.mkdir(network.cfg.statistic_path())

        file_path = network.cfg.statistic_path()

        Stats._get_parameter(network, file_path)
        Stats._get_config_files(network, file_path)

    @staticmethod
    def _get_config_files(network, file_path) -> None:
        """Extract all config files and write them into a csv file."""
        all_artifacts = network.get_nodes(node_type=ArtifactNode)

        file_name = os.path.join(
            file_path, f"{network.project_name}_files.csv"
        )

        with open(file_name, "w+", encoding="utf-8") as outfile:
            for artifact in all_artifacts:
                outfile.write(artifact.rel_file_path)

    @staticmethod
    def _get_parameter(network, file_path) -> None:
        """Extract hyperparameter and write them into a json file."""
        data = Stats._extract_params(network)

        file_name = os.path.join(
            file_path, f"{network.project_name}_params.json"
        )

        with open(file_name, "w+", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)

    @staticmethod
    def _extract_params(network: Network) -> Dict:
        """Extract hyperparameter from a configuration network."""
        all_artifacts = network.get_nodes(node_type=ArtifactNode)
        artifacts = list(
            filter(
                lambda x: isinstance(x, ArtifactNode) and x.id.endswith(".py"),
                all_artifacts,
            )
        )

        project_data = {}

        for artifact in artifacts:
            artifact_data = {}
            for option in artifact.children:
                if option.name != "file":
                    parameters = {}
                    try:
                        for param in option.children:
                            node = param.children[0]
                            if isinstance(node, ValueNode):

                                if node.possible_values:
                                    values = []
                                    for value in node.possible_values.values():
                                        values.append(value)
                                    parameters[param.name] = {
                                        "value": node.name,
                                        "possible_values": values,
                                    }
                                else:
                                    parameters[param.name] = {
                                        "value": node.name,
                                        "possible_values": [],
                                    }
                            else:
                                logging.warning(
                                    "Option node %s contain a node which is not of type ValueNode.",
                                    param.name,
                                )
                    except (IndexError, AttributeError) as error:
                        logging.warning(
                            "Option cannot be extracted due to %s.", error
                        )

                    artifact_data[
                        f"{option.name}_{option.location}"
                    ] = parameters

            project_data[artifact.rel_file_path] = artifact_data

        return project_data
