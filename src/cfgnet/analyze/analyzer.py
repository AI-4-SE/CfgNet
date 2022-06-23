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

import re
import os
import logging
import time

from typing import Optional, Set, Tuple
from cfgnet.vcs.git import Git
from cfgnet.vcs.git_history import GitHistory
from cfgnet.network.network import Network, NetworkConfiguration
from cfgnet.analyze.csv_writer import CSVWriter


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

        self.conflicts_csv_path = os.path.join(
            analysis_dir, f"conflicts_{self.cfg.project_name()}.csv"
        )

        if os.path.exists(self.conflicts_csv_path):
            os.remove(self.conflicts_csv_path)

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
        history = GitHistory(repo)
        commit = history.restore_initial_commit()

        try:
            ref_network = Network.init_network(cfg=self.cfg)

            while history.has_next_commit():
                prev_commit = commit
                commit = history.next_commit()

                detected_conflicts, ref_network = ref_network.validate(
                    [prev_commit.hexsha, commit.hexsha]
                )

                conflicts.update(detected_conflicts)

                self._print_progress(num_commit=history.commit_index + 1)

                if commit.hexsha == commit_hash_pre_analysis:
                    break

        except Exception as error:
            logging.error(
                "An exception occurred during analysis at commit %s.",
                commit.hexsha,
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

            CSVWriter.write_conflicts_to_csv(
                csv_path=self.conflicts_csv_path, conflicts=conflicts
            )

            self._print_progress(
                num_commit=history.commit_index + 1, final=True
            )

            avg_init_time, avg_detect_time = self.compute_performance()

            logging.debug("Latest commit analyzed: %s", commit.hexsha)
            logging.debug(
                "Total analyzed commits %s", str(history.commit_index + 1)
            )
            logging.info("Total detected conflicts: %s", str(len(conflicts)))

            logging.info(
                "Average Network Initialization time: [%s s]",
                avg_init_time,
            )
            logging.info(
                "Average Conflict Detection time: [%s s]", avg_detect_time
            )

    def compute_performance(self) -> Tuple:
        init_line = re.compile(r"Network Initialization:")
        detect_line = re.compile(r"Conflict Detection:")
        init_times = []
        detect_times = []

        try:
            with open(
                self.cfg.logfile_path(), "r", encoding="utf-8"
            ) as log_file:
                for line in log_file.readlines():
                    if init_line.search(line):
                        match = re.search(r"\[.+\]", line)
                        if match:
                            init_time = match.group(0)
                            init_time = (
                                init_time.replace(r"[", "")
                                .replace("]", "")
                                .split(" ")[0]
                            )
                            init_times.append(float(init_time))
                    if detect_line.search(line):
                        match = re.search(r"\[.+\]", line)
                        if match:
                            detect_time = match.group(0)
                            detect_time = (
                                detect_time.replace(r"[", "")
                                .replace("]", "")
                                .split(" ")[0]
                            )
                            detect_times.append(float(detect_time))
        except FileNotFoundError:
            logging.debug("File not found: %s ", self.cfg.logfile_path())
            return None, None

        logging.debug("Len Init Times: %s", str(len(init_times)))
        logging.debug("Len Detect Times: %s", str(len(detect_times)))

        avg_init_time = round((sum(init_times) / len(init_times)), 6)
        avg_detect_time = round((sum(detect_times) / len(detect_times)), 6)

        return avg_init_time, avg_detect_time
