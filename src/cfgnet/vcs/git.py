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

import logging

from typing import Optional, Any, List, Set

from git import Repo
from git.exc import InvalidGitRepositoryError
from git.refs.symbolic import SymbolicReference
from git.objects.commit import Commit as GitCommit
from git.objects.tree import Tree


class Commit:
    """Data structure of commits."""

    def __init__(self, commithash, msg, diffs):
        self.hash: str = commithash
        self.message: str = msg
        self.diffs: Optional[Set[Any]] = diffs


class Git:
    repo: Repo
    commit_history: List[GitCommit]
    commit_index: int

    def __init__(self, project_root: str) -> None:
        """Initialize the git repository."""
        try:
            self.repo = Repo(project_root)
            self.commit_history = list(
                self.repo.iter_commits(rev=self.repo.heads[0])
            )
            self.commit_history.reverse()
            self.commit_index = len(self.commit_history) - 1
        except InvalidGitRepositoryError:
            logging.error(
                '"%s" does not represent a git repository', project_root
            )
        except IndexError:
            logging.error(
                "You are probably in detached HEAD state. "
                "We can't do anything here. Sorry."
            )

    def get_current_branch_name(self) -> Optional[SymbolicReference]:
        """Return current branch name or None if HEAD is detached."""
        if self.repo.head.is_detached:
            return None
        return self.repo.active_branch

    def get_current_commit_hash(self) -> Any:
        """Return current commit hash."""
        return self.repo.head.object.hexsha

    def get_tracked_files(self) -> List:
        """Return tracked files."""
        tree = self.repo.tree()

        files: List[Any] = []

        self._iter_tree([tree], files)

        return files

    def checkout(self, commit: GitCommit) -> None:
        """Go to a specific commit."""
        self.repo.git.checkout(commit)

    def restore_initial_commit(self) -> Commit:
        """Restore initial commit."""
        if len(self.commit_history) > 0:
            self.repo.git.checkout(self.commit_history[0])
            self.commit_index = 0

        return Commit(
            self.commit_history[0].hexsha, self.commit_history[0].message, None
        )

    def has_next_commit(self) -> bool:
        """Return if there is a next commit."""
        return self.commit_index < len(self.commit_history) - 1

    def next_commit(self) -> Commit:
        """Go to next commit."""
        current_commit = self.commit_history[self.commit_index]
        self.commit_index += 1

        next_commit = self.commit_history[self.commit_index]
        self.repo.git.checkout(next_commit, force=True)

        diff_index = current_commit.diff(next_commit, create_patch=False)
        diffs = {}

        change_types = {"M", "R", "T"}

        for diff in diff_index:
            if diff.change_type in change_types:
                if diff.a_mode == 0o160000 or diff.b_mode == 0o160000:
                    logging.warning("skipped submodule at %s.", diff.a_path)
                    continue
                blob_old = diff.a_blob
                file_path_old = blob_old.abspath

                content_old = blob_old.data_stream.read().decode("latin-1")
                content_new = diff.b_blob.data_stream.read().decode("latin-1")

                diffs[file_path_old] = {"old": content_old, "new": content_new}

        return Commit(next_commit.hexsha, next_commit.message, diffs)

    def has_unstaged_changes(self) -> bool:
        """Return if there are unstaged changes in the working directory."""
        changed_files = [item.a_path for item in self.repo.index.diff(None)]
        if len(changed_files) > 0:
            return True
        return False

    def _iter_tree(self, trees: List[Tree], files: List[Any]) -> None:
        for tree in trees:
            for blob in tree.blobs:
                files.append(blob.path)
            if tree.trees:
                self._iter_tree(tree.trees, files)
