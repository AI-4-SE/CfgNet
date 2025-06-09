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


TOTAL_OPTIONS = ["8", "17", "17", "16", "17", "17", "21", "21"]
TOTAL_VALUES = ["6", "13", "13", "12", "13", "13", "16", "16"]
NUM_VALUE_NODES_CHANGED = ["0", "0", "1", "0", "0", "3", "0", "1"]
NUM_VALUE_NODES_ADDED = ["6", "7", "0", "0", "1", "0", "3", "0"]
NUM_VALUE_NODES_REMOVED = ["0", "0", "0", "1", "0", "0", "0", "0"]
NUM_CONFIG_FILES_CHANGED = ["1", "1", "1", "1", "1", "2", "1", "1"]
TOTAL_LINKS = ["0", "0", "0", "0", "0", "0", "1", "0"]
LINKS_ADDED = ["0", "0", "0", "0", "0", "0", "1", "0"]
LINKS_REMOVED = ["0", "0", "0", "0", "0", "0", "0", "1"]
CONFLICTS_DETECTED = ["0", "0", "0", "0", "0", "0", "0", "1"]


@pytest.fixture(name="get_repo")
def get_repo_():
    repo = TemporaryRepository("tests/test_repos/commit_stats")
    return repo


@pytest.fixture(name="get_csv_path")
def get_config_(get_repo):
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(get_repo.root),
        enable_static_blacklist=False,
        enable_dynamic_blacklist=False,
        enable_internal_links=False,
    )

    analyzer = Analyzer(network_configuration)
    analyzer.analyze_commit_history()

    project_name = network_configuration.project_name()
    data_dir = os.path.join(
        network_configuration.project_root_abs,
        network_configuration.cfgnet_path_rel,
    )
    analysis_dir = os.path.join(data_dir, "analysis")
    stats_csv_path = os.path.join(
        analysis_dir, f"commit_stats_{project_name}.csv"
    )

    return stats_csv_path


def test_number_of_commits(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        assert len(rows) == 8


def test_total_option_number(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert rows[i]["total_option_nodes"] == TOTAL_OPTIONS[i]


def test_num_config_file_changed(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert (
                rows[i]["num_configuration_files_changed"]
                == NUM_CONFIG_FILES_CHANGED[i]
            )


def test_total_value_nodes(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            print("added: ", i)
            assert rows[i]["total_value_nodes"] == TOTAL_VALUES[i]


def test_num_value_nodes_added(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            print("added: ", i)
            assert rows[i]["num_value_nodes_added"] == NUM_VALUE_NODES_ADDED[i]


def test_num_value_nodes_removed(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            print("removed: ", i)
            assert (
                rows[i]["num_value_nodes_removed"]
                == NUM_VALUE_NODES_REMOVED[i]
            )


def test_num_value_nodes_changed(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert (
                rows[i]["num_value_nodes_changed"]
                == NUM_VALUE_NODES_CHANGED[i]
            )


def test_total_links(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert rows[i]["total_links"] == TOTAL_LINKS[i]


def test_links_added(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert rows[i]["links_added"] == LINKS_ADDED[i]


def test_links_removed(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert rows[i]["links_removed"] == LINKS_REMOVED[i]


def test_conflicts_detected(get_csv_path):
    with open(get_csv_path, "r", encoding="utf-8") as csv_stats_file:
        reader = csv.DictReader(csv_stats_file)
        rows = list(reader)

        for i in range(len(rows)):
            assert rows[i]["conflicts_detected"] == CONFLICTS_DETECTED[i]
