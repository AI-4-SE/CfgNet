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

import os

from src.cfgnet.vcs.git import Git
from src.cfgnet.vcs.git_history import GitHistory

ROOT_DIR = os.path.dirname(os.path.abspath("CfgNet"))


def test_init_git_repo():
    repo = Git(project_root=ROOT_DIR)
    history = GitHistory(repo)

    assert repo is not None
    assert history.commits is not None
    assert history.commit_index is not None
    assert not history.has_next_commit()
    assert len(repo.get_tracked_files()) > 0
