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

        :param conflicts: Conflicts to be written to a csv file
        """
        field_names = [
            "occurred_at",
            "conflict_type",
            "conflict_id",
            "artifact",
            "option",
            "value",
            "old_value",
            "dependent_value",
        ]

        with open(csv_path, "a+", encoding="utf-8") as conflict_file:
            writer = csv.DictWriter(conflict_file, fieldnames=field_names)
            writer.writeheader()

            for conflict in conflicts:
                data = {
                    "occurred_at": conflict.occurred_at,
                    "conflict_type": conflict.__class__.__name__,
                    "conflict_id": conflict.id,
                }

                if isinstance(conflict, ModifiedOptionConflict):
                    data.update(
                        {
                            "artifact": conflict.artifact.rel_file_path,
                            "option": conflict.option.display_option_id,
                            "value": conflict.value.name,
                            "old_value": conflict.old_value.name,
                            "dependent_value": conflict.dependent_value.name,
                        }
                    )

                writer.writerow(data)
