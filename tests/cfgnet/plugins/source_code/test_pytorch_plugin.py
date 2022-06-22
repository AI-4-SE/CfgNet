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

from cfgnet.plugins.source_code.pytorch_plugin import PytorchPLugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = PytorchPLugin()
    return plugin


def is_responsible(get_plugin):
    pytorch_plugin = get_plugin

    pytorch_file = pytorch_plugin.is_responsible(
        os.path.abspath("tests/files/pytorch.py")
    )
    not_pytorch_file = pytorch_plugin.is_responsible(
        os.path.abspath("tests/files/Dockerfile")
    )

    assert pytorch_file
    assert not not_pytorch_file


def test_parse_pytorch_file(get_plugin):
    tf_plugin = get_plugin
    tf_file = os.path.abspath("tests/files/pytorch.py")

    artifact = tf_plugin.parse_file(tf_file, "pytorch.py")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert len(nodes) == 27

    assert make_id("pytorch.py", "file", "pytorch.py") in ids
    assert make_id("pytorch.py", "Sequential", "variable", "model") in ids
    assert make_id("pytorch.py", "Sequential", "*args", "torch.nn.Flatten(0, 1)") in ids
    assert make_id("pytorch.py", "MSELoss", "variable", "loss") in ids
    assert make_id("pytorch.py", "MSELoss", "reduction", "sum") in ids
    assert make_id("pytorch.py", "RMSprop", "variable", "optim_rms") in ids
    assert make_id("pytorch.py", "RMSprop", "params", "model.parameters()") in ids
    assert make_id("pytorch.py", "RMSprop", "lr", "learning_rate") in ids
    assert make_id("pytorch.py", "SGD", "variable", "optim_sgd") in ids
    assert make_id("pytorch.py", "SGD", "params", "model.parameters()") in ids
    assert make_id("pytorch.py", "SGD", "lr", "1e-08") in ids
    assert make_id("pytorch.py", "SGD", "momentum", "0.9") in ids

    assert make_id("pytorch.py", "Sequential", "variable", "model2") in ids
    assert make_id("pytorch.py", "Sequential", "*args", "OrderedDict([('conv1', torch.nn.Conv2d(1, 20, 5)), ('relu1', torch.nn.ReLU())])") in ids

    assert make_id("pytorch.py", "Polynomial3", "base_class_0", "torch.nn.Module") in ids
    assert make_id("pytorch.py", "Polynomial3", "Parameter", "variable", "self.a") in ids
    assert make_id("pytorch.py", "Polynomial3", "Parameter", "data", "torch.randn(())") in ids
    assert make_id("pytorch.py", "Polynomial3", "Linear", "variable", "self.linear") in ids
    assert make_id("pytorch.py", "Polynomial3", "Linear", "in_features", "1") in ids
    assert make_id("pytorch.py", "Polynomial3", "Linear", "out_features", "0") in ids

    assert make_id("pytorch.py", "Flatten", "start_dim", "0") in ids
    assert make_id("pytorch.py", "Flatten", "end_dim", "1") in ids

    assert make_id("pytorch.py", "Conv2d", "in_channels", "1") in ids
    assert make_id("pytorch.py", "Conv2d", "out_channels", "20") in ids
    assert make_id("pytorch.py", "Conv2d", "kernel_size", "5") in ids
    assert make_id("pytorch.py", "ReLU", "params", "default") in ids
    assert make_id("pytorch.py", "randn", "*size", "()")
