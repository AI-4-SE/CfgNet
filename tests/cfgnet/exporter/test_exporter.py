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

from shutil import rmtree

from cfgnet.network.network import Network
from cfgnet.exporter.exporter import DotExporter, JSONExporter
from cfgnet.network.network import NetworkConfiguration
from tests.utility.temporary_repository import TemporaryRepository


NETWORK_DIR = os.path.dirname(os.path.realpath(__file__))


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
    )

    yield network_configuration

    cleanup()


def cleanup():
    files = os.listdir(NETWORK_DIR)
    pickle_files = [x for x in files if x.endswith((".dot", ".json", ".png"))]

    for file in pickle_files:
        path_to_file = os.path.join(NETWORK_DIR, file)
        os.remove(path_to_file)

    if os.path.exists(os.path.join(NETWORK_DIR, "graph")):
        rmtree(os.path.join(NETWORK_DIR, "graph"))


def test_dot_export_file(get_config):
    network = Network.init_network(cfg=get_config)
    file_path = os.path.join(NETWORK_DIR, "dot_file.dot")

    with open(file_path, "w+", encoding="utf-8") as export_file:
        DotExporter(network).export(export_file, False)
        print(type(export_file))

    assert os.path.isfile(file_path)


def test_dot_visualize_file(get_config):
    network = Network.init_network(cfg=get_config)
    file_name = os.path.join(NETWORK_DIR, "visualized")
    file_path = file_name + ".png"

    dot_exporter = DotExporter(network=network)
    dot_exporter.visualize(file_name, "png", False)

    assert os.path.exists(file_path)


def test_json_export_file(get_config):
    network = Network.init_network(cfg=get_config)
    file_path = os.path.join(NETWORK_DIR, "json_file.json")

    with open(file_path, "w+", encoding="utf-8") as export_file:
        JSONExporter(network).export(export_file, False)

    assert os.path.isfile(file_path)
