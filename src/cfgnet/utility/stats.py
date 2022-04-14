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

from typing import Dict, TYPE_CHECKING
from cfgnet.network.nodes import ArtifactNode

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class Stats:
    def __init__(self, network: "Network", file_path: str) -> None:
        self.network: "Network" = network
        self.file_path: str = file_path

    def calculate(self) -> None:
        """Calculate statistics for the configuration network."""
        data = self.parse_py_nodes()
        self._write_to_json(data)

    def _write_to_json(self, data: Dict) -> None:
        """Write data to a json file."""
        file_name = os.path.join(
            self.file_path, f"statistics_{self.network.project_name}.json"
        )

        with open(file_name, "w+", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)

    def parse_py_nodes(self):
        all_artifacts = self.network.get_nodes(node_type=ArtifactNode)
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
                    params = filter(
                        lambda x: "::::variable" not in x.id, option.children
                    )
                    parameters = {}
                    for param in params:
                        parameters[param.name] = param.children[0].name

                    artifact_data[
                        f"{option.name}_{option.location}"
                    ] = parameters

            project_data[artifact.rel_file_path] = artifact_data

        return project_data
