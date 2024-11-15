#!/bin/env python3

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

from cfgnet.network.nodes import ValueNode
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.network.network import Network
from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture(name="repo")
def get_repo_():
    return TemporaryRepository("tests/test_repos/ignorefile")


def test_ignorefile(repo):
    cfg = NetworkConfiguration(
        project_root_abs=os.path.abspath(repo.root),
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False
    )

    network = Network.init_network(cfg)

    assert len(network.get_nodes(ValueNode)) > 2

    ignorefile_contents = "*.xml\nignored_dir"

    cfgnet_dir = os.path.join(cfg.project_root_abs, cfg.cfgnet_path_rel)
    if not os.path.exists(cfgnet_dir):
        os.makedirs(cfgnet_dir)
    ignorefile_path = cfg.ignorefile_path()
    with open(ignorefile_path, "w+", encoding="utf-8") as ignorefile:
        ignorefile.write(ignorefile_contents)

    network = Network.init_network(cfg)

    assert len(network.get_nodes(ValueNode)) == 2
