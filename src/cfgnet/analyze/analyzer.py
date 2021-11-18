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
import csv
import logging
import time

from typing import Optional, Set, Union
from cfgnet.vcs.git import Git
from cfgnet.network.network import Network, NetworkConfiguration
from cfgnet.conflicts.conflict import (
    MissingArtifactConflict,
    MissingOptionConflict,
    ModifiedOptionConflict,
)


class Analyzer:
    def __init__(self, cfg: NetworkConfiguration):
        self.cfg: NetworkConfiguration = cfg
        self.conflicts_cvs_path: Optional[str] = None
        self.time_last_progress_print: float = 0

        self._setup_dirs()

    def _setup_dirs(self) -> None:
        """Set up storage for analysis results."""
        data_dir = os.path.join(
            self.cfg.project_root_abs, self.cfg.cfgnet_path_rel
        )

        analysis_dir = os.path.join(data_dir, "analysis")

        if not os.path.exists(analysis_dir):
            os.makedirs(analysis_dir)

        self.conflicts_csv_path = os.path.join(analysis_dir, "conflicts.csv")

        if os.path.exists(self.conflicts_csv_path):
            os.remove(self.conflicts_csv_path)

    def _write_conflicts_to_csv(
        self,
        conflicts: Set[
            Union[
                ModifiedOptionConflict,
                MissingArtifactConflict,
                MissingOptionConflict,
            ]
        ],
    ) -> None:
        """
        Write all detected conflicts into a csv file.

        :param conflicts: Conflicts to be written to a csv file
        """
        fieldnames = [
            "occurred_at",
            "conflict_type",
            "conflict_id",
            "artifact",
            "option",
            "value",
            "old_value",
            "dependent_value",
        ]

        with open(
            self.conflicts_csv_path, "a+", encoding="utf-8"
        ) as conflict_file:
            writer = csv.DictWriter(conflict_file, fieldnames=fieldnames)
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

    def _print_progress(self, num_commit: int, final: bool = False) -> None:
        """Print the progress of th analysis."""
        if not final and time.time() - self.time_last_progress_print < 0.5:
            return

        if self.time_last_progress_print != 0:
            print("\r", end="")

        print(f"Analyzed commits: {num_commit}", end="")

        self.time_last_progress_print = time.time()

        if final:
            print()

    def analyze_commit_history(self) -> None:
        """Analyze the commit history."""
        repo = Git(project_root=self.cfg.project_root_abs)
        branch_pre_analysis = repo.get_current_branch_name()
        commit_hash_pre_analysis = repo.get_current_commit_hash()

        conflicts: Set = set()
        num_commit = 0

        try:
            commit = repo.restore_initial_commit()
            num_commit += 1

            while repo.has_next_commit():
                ref_network = Network.init_network(cfg=self.cfg)

                commit = repo.next_commit()
                num_commit += 1

                conflicts, _ = ref_network.validate()

                conflicts.update(conflicts)

                self._print_progress(num_commit=num_commit)

                if commit.hash == commit_hash_pre_analysis:
                    break

        except Exception as error:
            logging.error(
                "An exception occurred during analysis at commit %s.",
                commit.hash,
            )
            logging.error(error)
            raise

        finally:

            if branch_pre_analysis:
                # HEAD was a branch, so go back to that branch
                repo.checkout(branch_pre_analysis)
            else:
                # HEAD was detached, so got back to the commit
                repo.checkout(commit_hash_pre_analysis)

            self._write_conflicts_to_csv(conflicts)

            self._print_progress(num_commit=num_commit, final=True)
