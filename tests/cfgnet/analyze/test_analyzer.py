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
import pytest

from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.analyze.analyzer import Analyzer


from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture(name="get_repo")
def get_repo_():
    repo = TemporaryRepository("tests/test_repos/maven_docker")
    return repo


@pytest.fixture(name="get_config")
def get_config_(get_repo):
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(get_repo.root),
        enable_static_blacklist=False,
        enable_dynamic_blacklist=False,
    )

    return network_configuration


def test_analyze(get_config):
    analyzer = Analyzer(get_config)

    analyzer.analyze_commit_history()

    data_dir = os.path.join(
        get_config.project_root_abs, get_config.cfgnet_path_rel
    )
    analysis_dir = os.path.join(data_dir, "analysis")
    conflicts_csv_path = os.path.join(analysis_dir, "conflicts.csv")

    assert os.path.exists(conflicts_csv_path)

    with open(conflicts_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        assert len(rows) == 2