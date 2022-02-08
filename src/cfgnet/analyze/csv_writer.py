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
import csv

from typing import Set, Union

from cfgnet.conflicts.conflict import (
    MissingArtifactConflict,
    MissingOptionConflict,
    ModifiedOptionConflict,
)


class CSVWriter:
    @staticmethod
    def write_conflicts_to_csv(
        csv_path,
        conflicts: Set[
            Union[
                ModifiedOptionConflict,
                MissingArtifactConflict,
                MissingOptionConflict,
            ]
        ],
    ) -> None:
        """
        Write conflicts into a csv file.

        :param csv_path: path to store csv file
        :param conflicts: Conflicts to be written to a csv file
        """
        field_names = [
            "occurred_at",
            "prev_commit",
            "conflict_id",
            "conflict_type",
            "config_types",
            "link",
            "changed_artifact",
            "changed_option",
            "cmd",
        ]

        with open(csv_path, "a+", encoding="utf-8") as conflict_file:
            writer = csv.DictWriter(conflict_file, fieldnames=field_names)
            writer.writeheader()

            for conflict in conflicts:
                node_a = conflict.link.node_a
                node_b = conflict.link.node_b

                config_types = f"{node_a.config_type}<->{node_b.config_type}"

                data = {
                    "occurred_at": conflict.occurred_at,
                    "prev_commit": conflict.prev_commit,
                    "conflict_type": conflict.__class__.__name__,
                    "conflict_id": conflict.id,
                    "config_types": config_types,
                    "link": conflict.link,
                }

                if isinstance(conflict, ModifiedOptionConflict):
                    artifact = conflict.artifact

                    cmd = f"git show {conflict.occurred_at} -- {artifact.rel_file_path}"

                    data.update(
                        {
                            "changed_artifact": conflict.artifact.rel_file_path,
                            "changed_option": str(conflict.option),
                            "cmd": cmd,
                        }
                    )

                if isinstance(conflict, MissingOptionConflict):
                    artifact = conflict.artifact

                    cmd = f"git show {conflict.occurred_at} -- {artifact.rel_file_path}"

                    data.update(
                        {
                            "changed_artifact": conflict.artifact.rel_file_path,
                            "changed_option": str(conflict.missing_option),
                            "cmd": cmd,
                        }
                    )

                writer.writerow(data)
