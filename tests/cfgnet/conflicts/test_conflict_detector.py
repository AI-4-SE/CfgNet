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
import pytest

from cfgnet.conflicts.conflict import (
    MissingOptionConflict,
    ModifiedOptionConflict,
)
from cfgnet.conflicts.conflict_detector import ConflictDetector
from cfgnet.network.network import Network
from cfgnet.network.network import NetworkConfiguration
from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture(name="get_networks")
def get_networks_():
    """Return the conflicts and the updated simple git repository."""
    repo = TemporaryRepository(
        "tests/test_repos/maven_docker/0001-Add-Docker-and-maven-file.patch"
    )
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_dynamic_blacklist=False,
        disable_internal_links=False,
    )
    ref_network = Network.init_network(cfg=network_configuration)

    repo.apply_patch(
        "tests/test_repos/maven_docker/0002-Provoke-two-conflicts.patch"
    )
    new_network = Network.init_network(cfg=network_configuration)

    return ref_network, new_network


def test_detect_conflicts(get_networks):
    ref_network = get_networks[0]
    new_network = get_networks[1]

    conflicts = ConflictDetector.detect(
        ref_network=ref_network, new_network=new_network
    )

    modified_option_conflict = list(
        filter(lambda x: isinstance(x, ModifiedOptionConflict), conflicts)
    )
    missing_option_conflict = list(
        filter(lambda x: isinstance(x, MissingOptionConflict), conflicts)
    )

    assert len(conflicts) == 2
    assert len(modified_option_conflict) == 1
    assert len(missing_option_conflict) == 1
