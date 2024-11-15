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
    MissingArtifactConflict,
    MissingOptionConflict,
    ModifiedOptionConflict,
)
from cfgnet.conflicts.conflict_detector import ConflictDetector
from cfgnet.network.network import Network
from cfgnet.network.network import NetworkConfiguration
from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture(name="get_maven_docker_networks")
def get_maven_docker_networks():
    """Return the conflicts and the updated simple git repository."""
    repo = TemporaryRepository(
        "tests/test_repos/maven_docker/0001-Add-Docker-and-maven-file.patch"
    )
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False
    )
    ref_network = Network.init_network(cfg=network_configuration)

    repo.apply_patch(
        "tests/test_repos/maven_docker/0002-Provoke-two-conflicts.patch"
    )
    new_network = Network.init_network(cfg=network_configuration)

    return ref_network, new_network


@pytest.fixture(name="get_docker_networks")
def get_docker_networks():
    """Return the conflicts and the updated docker repository."""
    repo = TemporaryRepository(
        "tests/test_repos/docker_repo/0001-Add-Dockerfile.patch"
    )
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_internal_links=True,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False
    )
    ref_network = Network.init_network(cfg=network_configuration)

    repo.apply_patch(
        "tests/test_repos/docker_repo/0002-Provoke-internal-conflict.patch"
    )
    new_network = Network.init_network(cfg=network_configuration)

    return ref_network, new_network


@pytest.fixture(name="get_port_db_networks")
def get_port_db_networks():
    """Return the conflicts and the updated port database repository."""
    repo = TemporaryRepository(
        "tests/test_repos/port_db_repo/0001-Init-port-database-repo.patch"
    )
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False
    )
    ref_network = Network.init_network(cfg=network_configuration)

    repo.apply_patch(
        "tests/test_repos/port_db_repo/0002-Change-port-and-db-credentials.patch"
    )
    new_network = Network.init_network(cfg=network_configuration)

    return ref_network, new_network


@pytest.fixture(name="get_nodejs_networks")
def get_nodejs_networks():
    """Return the conflicts and the updated node.js repository."""
    repo = TemporaryRepository(
        "tests/test_repos/node_example/0001-Init-repository.patch"
    )
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=True,
        enable_file_type_plugins=False,
        system_level=False
    )
    ref_network = Network.init_network(cfg=network_configuration)

    repo.apply_patch(
        "tests/test_repos/node_example/0002-Remove-option-and-artifact.patch"
    )
    new_network = Network.init_network(cfg=network_configuration)

    return ref_network, new_network


@pytest.fixture(name="get_networks_equally_changed")
def get_networks_equally_changed():
    """Return the conflicts and the updated simple git repository."""
    repo = TemporaryRepository(
        "tests/test_repos/equal_values/0001-Add-two-package.json-files.patch"
    )
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False
    )
    ref_network = Network.init_network(cfg=network_configuration)

    repo.apply_patch(
        "tests/test_repos/equal_values/0002-Change-config-values-equally.patch"
    )
    new_network = Network.init_network(cfg=network_configuration)

    return ref_network, new_network


def test_detect_maven_docker_conflicts(get_maven_docker_networks):
    ref_network = get_maven_docker_networks[0]
    new_network = get_maven_docker_networks[1]

    conflicts = ConflictDetector.detect(
        ref_network=ref_network, new_network=new_network, enable_all_conflicts=False
    )

    modified_option_conflict = list(
        filter(lambda x: isinstance(x, ModifiedOptionConflict), conflicts)
    )

    assert len(conflicts) == 2
    assert len(modified_option_conflict) == 2


def test_detect_internal_docker_conflicts(get_docker_networks):
    ref_network = get_docker_networks[0]
    new_network = get_docker_networks[1]

    conflicts = ConflictDetector.detect(
        ref_network=ref_network, new_network=new_network, enable_all_conflicts=False
    )

    modified_option_conflict = list(
        filter(lambda x: isinstance(x, ModifiedOptionConflict), conflicts)
    )

    assert len(conflicts) == 1
    assert len(modified_option_conflict) == 1


def test_detect_port_db_conflicts(get_port_db_networks):
    ref_network = get_port_db_networks[0]
    new_network = get_port_db_networks[1]

    conflicts = ConflictDetector.detect(
        ref_network=ref_network, new_network=new_network, enable_all_conflicts=False
    )

    modified_option_conflict = list(
        filter(lambda x: isinstance(x, ModifiedOptionConflict), conflicts)
    )

    assert len(conflicts) == 3
    assert len(modified_option_conflict) == 3


def test_detect_all_nodejs_conflicts(get_nodejs_networks):
    ref_network = get_nodejs_networks[0]
    new_network = get_nodejs_networks[1]

    conflicts = ConflictDetector.detect(
        ref_network=ref_network, new_network=new_network, enable_all_conflicts=True
    )

    missing_artifact_conflict = list(
        filter(lambda x: isinstance(x, MissingArtifactConflict), conflicts)
    )

    missing_option_conflict = list(
        filter(lambda x: isinstance(x, MissingOptionConflict), conflicts)
    )

    assert len(conflicts) == 2
    assert len(missing_artifact_conflict) == 1
    assert len(missing_option_conflict) == 1


def test_equally_changed_values(get_networks_equally_changed):
    ref_network = get_networks_equally_changed[0]
    new_network = get_networks_equally_changed[1]

    conflicts = ConflictDetector.detect(
        ref_network=ref_network, new_network=new_network, enable_all_conflicts=False
    )

    assert len(conflicts) == 0
