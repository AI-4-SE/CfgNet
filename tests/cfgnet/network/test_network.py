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
from cfgnet.network.nodes import (
    ArtifactNode,
    OptionNode,
    ProjectNode,
    ValueNode,
)
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


def test_get_nodes(init_network):
    network = init_network[0]

    project_nodes = network.get_nodes(ProjectNode)
    artifact_nodes = network.get_nodes(ArtifactNode)
    option_nodes = network.get_nodes(OptionNode)
    value_nodes = network.get_nodes(ValueNode)

    assert all(isinstance(node, ProjectNode) for node in project_nodes)
    assert all(isinstance(node, ArtifactNode) for node in artifact_nodes)
    assert all(isinstance(node, OptionNode) for node in option_nodes)
    assert all(isinstance(node, ValueNode) for node in value_nodes)


def test_find_node(init_network):
    network = init_network[0]
    artifact_nodes = network.get_nodes(ArtifactNode)
    value_nodes = network.get_nodes(ValueNode)

    maven_file = next(filter(lambda x: "pom.xml" in x.name, artifact_nodes))
    executable = next(filter(lambda x: "ExecutableName" in x.id, value_nodes))
    config = next(filter(lambda x: "config" in x.name, value_nodes))
    config_option = config.parent

    searched_maven_file = network.find_node(maven_file)
    searched_executable = network.find_node(executable)
    searched_config_option = network.find_node(config_option)

    assert searched_maven_file == maven_file
    assert searched_config_option == config_option
    assert searched_executable == executable
