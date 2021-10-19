#!/bin/env python3

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

import platform
from glob import glob
from os import path
from tempfile import TemporaryDirectory
from typing import List

from git import Repo
from git.objects import Commit as GitCommit


class TemporaryRepository:
    """
    Data class for a temporary repository.

    This class will only be used in the tests.
    """

    def __init__(self, patch_str: str = None):
        """
        Initialize temporary git repository and apply all patch files in the patch_str path.

        patch_str may be the path to a specific patch file or a directory where multiple patch files can be found.
        If patch_str is None an empty repository will be created.

        :param patch_str: string representation of the path to the patch file(s)
        """
        self._temp_dir: TemporaryDirectory = TemporaryDirectory()
        self.repo: Repo = Repo.init(self._temp_dir.name)
        self.root: str = self._temp_dir.name
        self.repo.git.config("user.name", "ci")
        self.repo.git.config("user.email", "ci")

        if patch_str is not None:
            patch_dir = path.abspath(patch_str)
            if path.isfile(patch_dir):
                self.repo.git.am(patch_dir)
            else:
                for patch in sorted(glob(path.join(patch_dir, "*.patch"))):
                    self.repo.git.am(patch)

    def apply_patch(self, patch_str: str) -> None:
        """
        Apply a single patch file to this repository.

        :param patch_str: string representation of the path to the patch file
        :return: none
        """
        patch = path.abspath(patch_str)
        self.repo.git.am(patch)

    def apply_patches(self, patch_dir_str: str) -> None:
        """
        Apply all patch files in the patch_dir_str directory to this repository.

        :param patch_dir_str: string representation of the directory where the patch files are
        :return: none
        """
        patch_dir = path.abspath(patch_dir_str)
        for patch in sorted(glob(path.join(patch_dir, "*.patch"))):
            self.repo.git.am(patch)

    def get_commit_history(self) -> List[GitCommit]:
        """
        Get a list of all commits of this repository (from oldest to latest).

        :return: list of all commits of this repository
        """
        commit_history = list(self.repo.iter_commits(rev=self.repo.heads[0]))
        commit_history.reverse()
        return commit_history

    def get_root_name(self) -> str:
        """
        Get root name depending on the operating system.

        :return: root name
        """
        operating_system = platform.system()

        if operating_system == "Windows":
            return self.root.split("\\")[-1]
        elif operating_system == "Linux":
            return self.root.split("/")[-1]
        elif operating_system == "Darwin":
            return self.root.split("/")[-1]
        else:
            return self.root
