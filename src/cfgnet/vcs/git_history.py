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

from typing import List
import logging

from git.repo import Repo
from git.objects.commit import Commit
from cfgnet.vcs.git import Git, Diffs


class GitHistory:
    repo: Repo
    commits: List[Commit]
    commit_index: int
    CHANGE_TYPES = {"M", "R", "T"}

    def __init__(self, git: Git):
        self.repo = git.repo
        self.commits = list(self.repo.iter_commits(rev=self.repo.heads[0]))
        self.commits.reverse()
        self.commit_index = len(self.commits) - 1

    def restore_initial_commit(self) -> Diffs:
        initial_commit = self.commits[0]
        if len(self.commits) > 0:
            self.repo.git.checkout(initial_commit)
            self.commit_index = 0

        return Diffs(initial_commit, diffs=None)

    def has_next_commit(self) -> bool:
        return self.commit_index < len(self.commits) - 1

    def next_commit(self) -> Diffs:
        current_commit: Commit = self.commits[self.commit_index]
        self.commit_index += 1

        next_commit: Commit = self.commits[self.commit_index]
        self.repo.git.checkout(next_commit, force=True)

        diffs = {}
        for diff in current_commit.diff(next_commit, create_patch=False):
            if diff.change_type not in self.CHANGE_TYPES:
                continue
            if diff.a_mode == 0o160000 or diff.b_mode == 0o160000:
                logging.warning("Skipped submodule at %s.", diff.a_path)
                continue

            blob_old = diff.a_blob
            file_path_old = blob_old.abspath
            blob_new = diff.b_blob

            content_old = blob_old.data_stream.read().decode("latin-1")
            content_new = blob_new.data_stream.read().decode("latin-1")

            diffs[file_path_old] = {
                "old": content_old,
                "new": content_new,
            }

        return Diffs(next_commit, diffs)
