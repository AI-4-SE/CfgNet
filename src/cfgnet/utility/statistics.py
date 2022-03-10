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
        self.total_artifact_nodes = 0
        self.total_option_nodes = 0
        self.num_value_nodes_added = 0
        self.num_value_nodes_removed = 0
        self.num_value_nodes_changed = 0
        self.total_links = 0
        self.total_links_changed = 0
        self.num_configuration_files_changed = 0
        self.num_detected_conflicts = 0
        self.num_fixed_conflicts = 0

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

        stats._value_node_ids = {
            node.id for node in network.get_nodes(ValueNode)
        }
        stats._value_node_parent_ids = {
            node.parent.id for node in network.get_nodes(ValueNode)
        }

        stats.commit_number = commit_number
        artifact_nodes = network.get_nodes(ArtifactNode)
        stats.total_artifact_nodes = len(artifact_nodes)
        stats.total_option_nodes = len(network.get_nodes(OptionNode))
        stats.num_value_nodes_added = len(
            prev._value_node_ids.difference(stats._value_node_parent_ids)
        )
        stats.num_value_nodes_removed = len(
            stats._value_node_ids.difference(prev._value_node_parent_ids)
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

        stats._links = set(network.links)
        stats.total_links = len(stats._links)
        stats.total_links_changed = len(
            prev._links.symmetric_difference(stats._links)
        )

        config_files = {node.rel_file_path for node in artifact_nodes}
        files_changed = set(commit.stats.files.keys())
        config_files_changed = config_files.intersection(files_changed)
        stats.num_configuration_files_changed = len(config_files_changed)

        stats._conflicts = set(conflicts)
        new_conflicts = stats._conflicts.difference(prev._conflicts)
        fixed_conflicts = prev._conflicts.difference(stats._conflicts)
        stats.num_detected_conflicts = Conflict.count_total(new_conflicts)
        stats.num_fixed_conflicts = Conflict.count_total(fixed_conflicts)

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
                "total_option_nodes": self.total_option_nodes,
                "num_value_nodes_changed": self.num_value_nodes_changed,
                "total_artifact_nodes": self.total_artifact_nodes,
                "total_links": self.total_links,
                "total_links_changed": self.total_links_changed,
                "num_configuration_files_changed": self.num_configuration_files_changed,
                "num_detected_conflicts": self.num_detected_conflicts,
                "num_fixed_conflicts": self.num_fixed_conflicts,
                "num_value_nodes_added": self.num_value_nodes_added,
                "num_value_nodes_removed": self.num_value_nodes_removed,
            }
        )
        return data
