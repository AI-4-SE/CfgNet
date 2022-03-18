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
from collections import OrderedDict
from typing import Optional, Iterable

from cfgnet.network.network import Network
from cfgnet.network.nodes import OptionNode, ArtifactNode, ValueNode
from cfgnet.conflicts.conflict import Conflict
from cfgnet.vcs.git import Commit


class CommitStatistics:
    writer: Optional[csv.DictWriter] = None

    def __init__(self, commit=None):
        self.commit_hash = None
        self.commit_number = 0
        self.total_num_artifact_nodes = 0
        self.num_configuration_files_changed = 0
        self.total_config_files = set()
        self.config_files_changed = set()
        self.total_option_nodes = 0
        self.total_value_nodes = 0
        self.num_value_nodes_added = 0
        self.num_value_nodes_removed = 0
        self.num_value_nodes_changed = 0
        self.total_links = 0
        self.links_added = 0
        self.links_removed = 0
        self.conflicts_detected = 0

        self._value_node_ids = set()
        self._value_node_parent_ids = set()
        self._links = set()
        self._conflicts = set()

        if commit:
            self.commit_hash = commit.hexsha

    @staticmethod
    # pylint: disable=protected-access
    def calc_stats(
        commit: Commit,
        commit_number: int,
        network: Network,
        conflicts: Iterable[Conflict],
        prev: "CommitStatistics",
    ) -> "CommitStatistics":
        stats = CommitStatistics(commit=commit)

        # commit data
        stats.commit_number = commit_number
        stats.commit_hash = commit.hexsha

        # artifact data
        artifact_nodes = network.get_nodes(ArtifactNode)
        stats.total_num_artifact_nodes = len(artifact_nodes)
        stats.total_config_files = {
            node.rel_file_path for node in artifact_nodes
        }
        files_changed = set(commit.stats.files.keys())
        stats.config_files_changed = stats.total_config_files.intersection(
            files_changed
        )
        stats.num_configuration_files_changed = len(stats.config_files_changed)

        # option data
        option_nodes = network.get_nodes(OptionNode)
        stats.total_option_nodes = len(option_nodes)

        # value data
        value_nodes = network.get_nodes(ValueNode)
        stats.total_value_nodes = len(value_nodes)
        stats._value_node_ids = {node.id for node in value_nodes}
        stats._value_node_parent_ids = {node.parent.id for node in value_nodes}

        stats.num_value_nodes_added = len(
            stats._value_node_ids.difference(prev._value_node_ids)
        )
        stats.num_value_nodes_removed = len(
            prev._value_node_ids.difference(stats._value_node_ids)
        )

        stats.num_value_nodes_changed = 0
        value_parents_in_common = stats._value_node_parent_ids.intersection(
            prev._value_node_parent_ids
        )
        for node in value_parents_in_common:

            def same_parent(node_id, parent=node):
                return node_id.startswith(parent)

            value_prev = list(filter(same_parent, prev._value_node_ids))[0]
            value_new = list(filter(same_parent, stats._value_node_ids))[0]
            if value_prev != value_new:
                stats.num_value_nodes_changed += 1
                stats.num_value_nodes_added -= 1
                stats.num_value_nodes_removed -= 1

        # link data
        stats._links = network.links
        stats.total_links = len(stats._links)
        stats.links_added = len(stats._links.difference(prev._links))
        stats.links_removed = len(prev._links.difference(stats._links))

        # conflict data
        stats.conflicts_detected = len(list(conflicts))

        return stats

    @staticmethod
    def setup_writer(commit_stats_file) -> None:
        CommitStatistics.writer = csv.DictWriter(
            commit_stats_file, fieldnames=CommitStatistics.fieldnames()
        )
        CommitStatistics.writer.writeheader()

    @staticmethod
    def write_row(stats):
        if CommitStatistics.writer is not None:
            CommitStatistics.writer.writerow(stats.data_dict())

    @staticmethod
    def fieldnames():
        return list(CommitStatistics().data_dict().keys())

    def data_dict(self):
        data = OrderedDict(
            {
                "commit_number": self.commit_number,
                "commit_hash": self.commit_hash,
                "total_num_artifact_nodes": self.total_num_artifact_nodes,
                "num_configuration_files_changed": self.num_configuration_files_changed,
                "total_config_files": sorted(self.total_config_files),
                "config_files_changed": sorted(self.config_files_changed),
                "total_option_nodes": self.total_option_nodes,
                "total_value_nodes": self.total_value_nodes,
                "num_value_nodes_changed": self.num_value_nodes_changed,
                "num_value_nodes_added": self.num_value_nodes_added,
                "num_value_nodes_removed": self.num_value_nodes_removed,
                "total_links": self.total_links,
                "links_added": self.links_added,
                "links_removed": self.links_removed,
                "conflicts_detected": self.conflicts_detected,
            }
        )
        return data
