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

from cfgnet.plugins.source_code.tensorflow_plugin import TensorflowPLugin


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = TensorflowPLugin()
    return plugin


def test_is_responsible(get_plugin):
    sklearn_plugin = get_plugin

    sklearn_file = sklearn_plugin.is_responsible(
        os.path.abspath("tests/files/tensorflow.py")
    )
    not_sklearn_file = sklearn_plugin.is_responsible(
        os.path.abspath("tests/files/Dockerfile")
    )

    assert sklearn_file
    assert not not_sklearn_file
