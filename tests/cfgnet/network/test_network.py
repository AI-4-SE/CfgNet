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
import hashlib

from cfgnet.network.network import Network
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.network.nodes import (
    ArtifactNode,
    OptionNode,
    ProjectNode,
    ValueNode,
)
from cfgnet.conflicts.conflict import ModifiedOptionConflict
from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture(name="get_repo")
def get_repo_():
    repo = TemporaryRepository(
        "tests/test_repos/maven_docker/0001-Add-Docker-and-maven-file.patch"
    )
    return repo


@pytest.fixture(name="get_config")
def get_config_(get_repo):
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(get_repo.root),
        enable_static_blacklist=False,
        enable_dynamic_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False
    )

    return network_configuration


def test_init_network(get_repo, get_config):
    network = Network.init_network(cfg=get_config)
    project_name = os.path.basename(os.path.abspath(get_repo.root))
    root = ProjectNode(name=project_name, root_dir=get_repo.root)

    assert network
    assert network.root == root
    assert len(network.links) == 2
    assert os.path.isdir(network.cfg.data_dir_path())


def test_links(get_config):
    network = Network.init_network(cfg=get_config)
    expected_links = {
        "target/example-app-1.0.jar",
        "pom.xml",
    }

    link_targets = {
        str(link).rsplit("::::", maxsplit=1)[-1] for link in network.links
    }

    assert len(network.links) == 2
    assert expected_links == link_targets


def test_enable_internal_links(get_config):
    config = get_config
    config.enable_internal_links = True
    network = Network.init_network(cfg=config)

    for node in network.get_nodes(node_type=ValueNode):
        if "Dockerfile" in node.id:
            print("Node: ", node, node.config_type)

    for link in network.links:
        print("=======================")
        print("Link: ", link)
        print(f"{link.node_a.config_type}<->{link.node_b.config_type}")

    expected_links = {
        "app.jar",
        "target/example-app-1.0.jar",
        "pom.xml",
        "builder",
        "version:5.9",
    }

    link_targets = {
        str(link).rsplit("::::", maxsplit=1)[-1] for link in network.links
    }

    assert len(network.links) == 5
    assert expected_links == link_targets


def test_get_nodes(get_config):
    network = Network.init_network(cfg=get_config)

    project_nodes = network.get_nodes(ProjectNode)
    artifact_nodes = network.get_nodes(ArtifactNode)
    option_nodes = network.get_nodes(OptionNode)
    value_nodes = network.get_nodes(ValueNode)

    assert all(isinstance(node, ProjectNode) for node in project_nodes)
    assert all(isinstance(node, ArtifactNode) for node in artifact_nodes)
    assert all(isinstance(node, OptionNode) for node in option_nodes)
    assert all(isinstance(node, ValueNode) for node in value_nodes)


def test_find_node(get_config):
    network = Network.init_network(cfg=get_config)
    artifact_nodes = network.get_nodes(ArtifactNode)
    value_nodes = network.get_nodes(ValueNode)

    maven_file = next(filter(lambda x: "pom.xml" in x.name, artifact_nodes))
    executable = next(filter(lambda x: "ExecutableName" in x.id, value_nodes))
    config = next(filter(lambda x: "config" in x.name, value_nodes))
    config_option = config.parent

    searched_maven_file = network.find_artifact_node(maven_file)
    searched_executable = network.find_value_node(executable)
    searched_config_option = network.find_option_node(config_option)
    node_not_found = network.find_value_node(config_option)

    assert searched_maven_file == maven_file
    assert searched_config_option == config_option
    assert searched_executable == executable
    assert not node_not_found


def test_save_network(get_config):
    network = Network.init_network(cfg=get_config)

    file_name = hashlib.md5(network.project_root.encode()).hexdigest()
    network_file = os.path.join(
        network.cfg.network_dir_path(), file_name + ".pickle"
    )

    network.save()

    assert os.path.exists(network_file)


def test_load_network(get_config):
    network = Network.init_network(cfg=get_config)

    network.save()
    loaded_network = Network.load_network(
        project_root=network.cfg.project_root_abs
    )

    assert loaded_network


def test_validate_network(get_repo, get_config):
    repo = get_repo
    ref_network = Network.init_network(cfg=get_config)
    ref_network.save()

    repo.apply_patch(
        "tests/test_repos/maven_docker/0002-Provoke-two-conflicts.patch"
    )

    conflicts, _ = ref_network.validate()

    modified_option_conflicts = list(
        filter(lambda x: isinstance(x, ModifiedOptionConflict), conflicts)
    )

    assert len(conflicts) == 2
    assert len(modified_option_conflicts) == 2


def test_export_network(get_config):
    network = Network.init_network(cfg=get_config)
    export_file = os.path.join(network.cfg.export_dir_path(), "dot_file")

    network.export("dot_file", "dot", False)

    assert os.path.exists(export_file)


def test_visualize_network(get_config):
    network = Network.init_network(cfg=get_config)
    export_file = os.path.join(network.cfg.export_dir_path(), "png_file.png")

    network.visualize("png_file", "png", False)

    assert os.path.exists(export_file)
