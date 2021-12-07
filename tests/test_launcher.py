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
from tempfile import TemporaryDirectory
import pytest

from click.testing import CliRunner, Result
from cfgnet.launcher import main
from cfgnet.linker.linker_manager import LinkerManager
from tests.utility.temporary_repository import TemporaryRepository


runner = CliRunner()

ROOT_DIR = os.path.abspath(os.curdir)


@pytest.fixture(name="get_repo")
def get_repo_():
    repo = TemporaryRepository("tests/test_repos/maven_docker")
    return repo


def test_invalid_command():
    result: Result = runner.invoke(main, ["invalidcommand", ROOT_DIR])
    assert result.exit_code != 0


def test_commands(get_repo):
    result_init: Result = runner.invoke(main, ["init", ROOT_DIR])
    assert result_init.exit_code == 0

    result_validate: Result = runner.invoke(main, ["validate", ROOT_DIR])
    assert result_validate.exit_code == 0

    result_analyze: Result = runner.invoke(main, ["analyze", get_repo.root])
    assert result_analyze.exit_code == 0

    with TemporaryDirectory() as export_dir:

        json_export_filename = os.path.join(export_dir, "network.json")
        assert not os.path.exists(json_export_filename)
        result_export_json: Result = runner.invoke(
            main, ["export", "-fjson", f"-o{json_export_filename}", ROOT_DIR]
        )
        assert result_export_json.exit_code == 0

        dot_export_filename = os.path.join(export_dir, "network.dot")
        assert not os.path.exists(dot_export_filename)
        result_export_dot: Result = runner.invoke(
            main, ["export", "-fdot", f"-o{dot_export_filename}", ROOT_DIR]
        )
        assert result_export_dot.exit_code == 0


def test_linker_options():
    result: Result = runner.invoke(
        main, ["init", ROOT_DIR, "--disable-linker", "equality"]
    )
    assert len(LinkerManager.enabled_linkers) == 0
    assert result.exit_code == 0
