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

from cfgnet.network.network import Network
from cfgnet.network.nodes import ProjectNode
from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture(name="init_network")
def init_network_():
    repo = TemporaryRepository(
        "tests/test_repos/maven_docker/0001-Add-Docker-and-maven-file.patch"
    )
    network = Network.init_network(project_root=repo.root)

    return network, repo.root


def test_init_network(init_network):
    network = init_network[0]
    repo_root = init_network[1]
    project_name = os.path.basename(os.path.abspath(repo_root))
    root = ProjectNode(name=project_name, root_dir=repo_root)

    print("repo_root: ", repo_root)
    print("project_name: ", project_name)

    assert network
    assert network.project_name == project_name
    assert network.root == root
