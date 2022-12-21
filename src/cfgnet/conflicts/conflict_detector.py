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

from typing import Optional, Set, TYPE_CHECKING
from cfgnet.conflicts.conflict import (
    MissingArtifactConflict,
    MissingOptionConflict,
    ModifiedOptionConflict,
)
from cfgnet.network.nodes import OptionNode
from cfgnet.linker.link import Link

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class ConflictDetector:
    """Static class responsible for conflict detection."""

    @staticmethod
    def detect(
        ref_network: "Network",
        new_network: "Network",
        enable_all_conflicts: bool,
        commit_hash: Optional[str] = None,
    ) -> Set:
        """
        Detect conflicts.

        :param ref_network: Reference network
        :param new_network: Modified network
        :param commit_hash: Commit in which the conflict was detected
        :param enable_all_conflicts: Enable the detection of all conflicts
        :return: Set of detected conflicts
        """
        conflicts: Set = set()

        missing_links = ref_network.links.difference(new_network.links)

        for link in missing_links:
            if enable_all_conflicts:
                if missing_artifact_conflict := ConflictDetector._detect_missing_artifact(
                    link, new_network
                ):
                    conflicts.add(missing_artifact_conflict)
                    continue

                if missing_option_conflict := ConflictDetector._detect_missing_options(
                    link, new_network
                ):
                    conflicts.add(missing_option_conflict)
                    continue

            if modified_option_conflict := ConflictDetector._detect_modified_options(
                link, new_network
            ):
                # If a conflict with the same cause already exists,
                # update that conflict with the new conflicts dependent option.
                existing_conflicts = [
                    conflict
                    for conflict in conflicts
                    if conflict == modified_option_conflict
                ]
                if len(existing_conflicts) > 0:
                    existing_conflict = existing_conflicts[0]
                    existing_conflict.update_dependents(
                        modified_option_conflict
                    )
                else:
                    conflicts.add(modified_option_conflict)
                continue

        if commit_hash:
            for conflict in conflicts:
                conflict.occurred_at = commit_hash

        return conflicts

    @staticmethod
    def _detect_missing_artifact(
        link: Link, new_network: "Network"
    ) -> Optional[MissingArtifactConflict]:
        """Detect a missing artifact conflict."""
        artifact_a = new_network.find_artifact_node(link.artifact_a)
        artifact_b = new_network.find_artifact_node(link.artifact_b)

        missing_artifacts = []

        if artifact_a is None:
            missing_artifacts.append(link.artifact_a)
        if artifact_b is None:
            missing_artifacts.append(link.artifact_b)

        if len(missing_artifacts) == 1:
            return MissingArtifactConflict(
                link=link, missing_artifact=missing_artifacts[0]
            )
        return None

    @staticmethod
    def _detect_missing_options(
        link: Link, new_network: "Network"
    ) -> Optional[MissingOptionConflict]:
        """Detect a missing option conflict."""
        artifact_a = new_network.find_artifact_node(link.artifact_a)
        artifact_b = new_network.find_artifact_node(link.artifact_b)

        if artifact_a is None or artifact_b is None:
            return None

        option_a = new_network.find_option_node(link.option_stack_a[-1])
        option_b = new_network.find_option_node(link.option_stack_b[-1])

        missing_options = []

        node = None

        if option_a is None:
            missing_options.append(link.option_stack_a[-1])
            node = "a"
        if option_b is None:
            missing_options.append(link.option_stack_b[-1])
            node = "b"

        if len(missing_options) == 1:
            if node == "a":
                return MissingOptionConflict(
                    link=link,
                    missing_option=missing_options[0],
                    artifact=link.artifact_a,
                    value=link.node_a,
                )
            if node == "b":
                return MissingOptionConflict(
                    link=link,
                    missing_option=missing_options[0],
                    artifact=link.artifact_b,
                    value=link.node_b,
                )

        return None

    # pylint: disable=too-many-return-statements
    @staticmethod
    def _detect_modified_options(
        link: Link, new_network: "Network"
    ) -> Optional[ModifiedOptionConflict]:
        """Detect either a modified option or a multi value conflict."""
        artifact_a = new_network.find_artifact_node(link.artifact_a)
        artifact_b = new_network.find_artifact_node(link.artifact_b)

        if artifact_a is None or artifact_b is None:
            return None

        option_a = new_network.find_option_node(link.option_stack_a[-1])
        option_b = new_network.find_option_node(link.option_stack_b[-1])

        if option_a is None or option_b is None:
            return None

        # Skip conflict creation if option has no children
        if not option_a.children:
            logging.warning("Option %s does not contain a children.", option_a)
            return None

        if not option_b.children:
            logging.warning("Option %s does not contain a children.", option_b)
            return None

        # Skip conflict creation #200
        if isinstance(option_a.children[0], OptionNode) or isinstance(
            option_b.children[0], OptionNode
        ):
            return None

        value_a = new_network.find_value_node(link.node_a)
        value_b = new_network.find_value_node(link.node_b)

        # check if both values changed equally
        if value_a is None and value_b is None:
            if option_a.prevalue_node and option_b.prevalue_node:
                if option_a.children[0].name == option_b.children[0].name:
                    return None

        multi_value = (
            len(link.option_stack_a[-1].children) > 1
            or len(link.option_stack_b[-1].children) > 1
            or len(option_a.children) > 1
            or len(option_b.children) > 1
        )
        if multi_value:
            logging.warning("Conflict involves options with multiple values.")

        new_conflict: Optional[ModifiedOptionConflict] = None

        if value_a is None:
            if multi_value:
                # Skip creating MultiValueConflict
                return None

            new_conflict = ModifiedOptionConflict(
                link=link,
                artifact=link.artifact_a,
                option=option_a,
                value=option_a.children[0],
                old_value=link.node_a,
                dependent_artifact=link.artifact_b,
                dependent_option=link.option_stack_b[-1],
                dependent_value=link.node_b,
            )

        if value_b is None:
            if multi_value:
                # Skip creating MultiValueConflict
                return None

            new_conflict = ModifiedOptionConflict(
                link=link,
                artifact=link.artifact_b,
                option=option_b,
                value=option_b.children[0],
                old_value=link.node_b,
                dependent_artifact=link.artifact_a,
                dependent_option=link.option_stack_a[-1],
                dependent_value=link.node_a,
            )

        return new_conflict
