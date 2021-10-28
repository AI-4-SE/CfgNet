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
from click.testing import CliRunner, Result
from cfgnet.launcher import main

runner = CliRunner()


def test_invalid_command():
    result: Result = runner.invoke(main, ["invalidcommand", "."])
    assert result.exit_code != 0


def test_commands():
    result_init: Result = runner.invoke(main, ["init", "."])
    assert result_init.exit_code == 0

    result_validate: Result = runner.invoke(main, ["validate", "."])
    assert result_validate.exit_code == 0

    result_analyze: Result = runner.invoke(main, ["analyze", "."])
    assert result_analyze.exit_code == 0

    with TemporaryDirectory() as export_dir:

        json_export_filename = os.path.join(export_dir, "network.json")
        assert not os.path.exists(json_export_filename)
        result_export_json: Result = runner.invoke(
            main, ["export", "-fjson", f"-o{json_export_filename}", "."]
        )
        assert result_export_json.exit_code == 0

        dot_export_filename = os.path.join(export_dir, "network.dot")
        assert not os.path.exists(dot_export_filename)
        result_export_dot: Result = runner.invoke(
            main, ["export", "-fdot", f"-o{dot_export_filename}", "."]
        )
        assert result_export_dot.exit_code == 0
