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

from __future__ import annotations

import abc
import hashlib
import logging

from typing import Any, List, Optional, Set
from cfgnet.linker.link import Link
from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode


class Conflict(abc.ABC):
    """Base class for conflicts."""

    def __init__(self, link):
        self.link: Link = link
        self.fixed: bool = False
        self.occurred_at: Optional[str] = None
        self.fixed_at: Optional[str] = None
        self._count = 1

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def __hash__(self):
        pass

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def count(self) -> int:
        """
        Conflict count for evaluation.

        ModifiedOptionConflicts are counted as the number of dependents.
        All other conflicts count as one.
        """
        return self._count

    @abc.abstractmethod
    def is_involved(self, node: Any) -> bool:
        """
        Check if a node is involved in a conflict.

        :param node: node that may be involved in a conflict
        :return: true if node is involved in a conflict, else false
        """

    @staticmethod
    def count_total(conflicts: List[Conflict]) -> int:
        """Total conflict count across a list."""
        return sum((conflict.count() for conflict in conflicts))


class MissingArtifactConflict(Conflict):
    """Conflict that occurs when a linked artifact is missing."""

    def __init__(self, link: Link, missing_artifact: ArtifactNode):
        super().__init__(link)
        self.missing_artifact: ArtifactNode = missing_artifact
        self.id: str = hashlib.md5(
            missing_artifact.id.encode("utf-8")
        ).hexdigest()

    def __str__(self):
        return (
            f"MISSING ARTIFACT ({self.id})\n\n"
            + f"Artifact {self.missing_artifact.rel_file_path}'n\n"
            + "Possible solutions:\n\n"
            f"Restore artifact {self.missing_artifact.file_path}\n\n"
        )

    def __hash__(self):
        return int(self.id, base=16)

    def is_involved(self, node: Any) -> bool:
        return False


class MissingOptionConflict(Conflict):
    """Conflict that occurs when a linked option is missing."""

    def __init__(
        self,
        link: Link,
        missing_option: OptionNode,
        artifact: ArtifactNode,
        value: ValueNode,
    ):
        super().__init__(link)
        self.missing_option: OptionNode = missing_option
        self.artifact: ArtifactNode = artifact
        self.id: str = hashlib.md5(
            missing_option.id.encode("utf-8")
        ).hexdigest()
        self.value: ValueNode = value

    def __str__(self):
        return (
            f"MISSING OPTION CONFLICT ({self.id})\n\n"
            + f"Option {self.missing_option.name} in artifact "
            f"{self.artifact.rel_file_path} is missing\n\n"
            + f"In file {self.artifact.file_path}\n"
            + f"Re-add option {self.missing_option.display_option_id} "
            f'with value "{self.value.name}"\n\n'
        )

    def __hash__(self):
        return int(self.id, base=16)

    def is_involved(self, node: Any) -> bool:
        return False


class ModifiedOptionConflict(Conflict):
    """Conflict that occurs when a linked option has been modified."""

    def __init__(
        self,
        link: Link,
        artifact: ArtifactNode,
        option: OptionNode,
        value: ValueNode,
        old_value: ValueNode,
        dependent_artifact: ArtifactNode,
        dependent_option: OptionNode,
        dependent_value: ValueNode,
    ):
        super().__init__(link)
        self.artifact: ArtifactNode = artifact
        self.option: OptionNode = option
        self.value: ValueNode = value

        id_string: str = old_value.id + "->" + self.value.id
        self.id: str = hashlib.md5(id_string.encode("utf-8")).hexdigest()

        self.old_value: ValueNode = old_value
        self.dependents: Set = set([(dependent_artifact, dependent_option)])
        self.dependent_artifact: ArtifactNode = dependent_artifact
        self.dependent_option: OptionNode = dependent_option
        self.dependent_value: ValueNode = dependent_value

    def update_dependents(
        self, other_conflict: ModifiedOptionConflict
    ) -> None:
        """Add another conflict's dependent options and artifacts."""
        if other_conflict != self:
            logging.warning(
                "Will not add dependent options of a conflict with different cause."
            )

        self.dependents.update(other_conflict.dependents)

    def __str__(self):
        conflicts = ""
        dependents = list(self.dependents)
        dependents.sort(key=lambda d: str(d[0]))
        for dependent_artifact, dependent_option in dependents:
            conflicts += (
                "-----------------------------------------\n"
                + f"In file {dependent_artifact.file_path}:{dependent_option.location}\n"
                + f"Link with option {dependent_option.display_option_id} is missing\n"
                + f"Modify option {dependent_option.display_option_id}:\n"
                + f'"{self.old_value.name}" to "{self.value.name}"\n'
            )
        return (
            f"MODIFIED OPTION CONFLICT ({self.id})\n\n"
            + f"Modified Option: {self.option.display_option_id} "
            f"in artifact {self.artifact.rel_file_path}\n"
            + f"Value changed from {self.old_value.name} to {self.value.name}\n\n"
            "" + "Conflicts:\n" + f"{conflicts}\n\n"
        )

    def __hash__(self):
        return int(self.id, base=16)

    def is_involved(self, node: Any) -> bool:
        if node.parent in (self.option, self.dependent_option):
            return True
        return False

    def count(self):
        """Get the number of dependent options."""
        return len(self.dependents)


class MultiValueConflict(Conflict):
    """Occurs when a linked option with multiple values has been modified."""

    def __init__(
        self,
        link: Link,
        artifact: ArtifactNode,
        option: OptionNode,
        dependent_option: OptionNode,
        dependent_artifact: ArtifactNode,
        multi_value: bool = False,
    ):
        super().__init__(link)
        self.artifact: ArtifactNode = artifact
        self.option: OptionNode = option

        id_string: str = (
            str(self.link)
            + str(self.option.name)
            + str(self.artifact.rel_file_path)
        )
        self.id: str = hashlib.md5(id_string.encode("utf-8")).hexdigest()

        self.dependent_artifact: ArtifactNode = dependent_artifact
        self.dependent_option: OptionNode = dependent_option
        self.multi_value: bool = multi_value

    def __str__(self):
        return (
            f"MULTIVALUE ({self.id})\n\n"
            + f"Option {self.option.name} \
            in artifact {self.artifact.rel_file_path}\n\n"
        )

    def __hash__(self):
        return int(self.id, base=16)

    def is_involved(self, node: Any) -> bool:
        return False
