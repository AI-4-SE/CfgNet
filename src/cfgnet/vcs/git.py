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

from typing import Optional, Any, List, Union

from git.repo import Repo
from git.exc import InvalidGitRepositoryError
from git.refs.symbolic import SymbolicReference
from git.objects.commit import Commit
from git.objects.tree import Tree


class Git:
    repo: Repo

    def __init__(self, project_root: str) -> None:
        """Initialize the git repository."""
        try:
            self.repo = Repo(project_root)
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

    def checkout(self, commit: Union[Commit, SymbolicReference]) -> None:
        """Go to a specific commit."""
        self.repo.git.checkout(commit)

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
