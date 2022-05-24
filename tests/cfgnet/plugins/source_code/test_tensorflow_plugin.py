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
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = TensorflowPLugin()
    return plugin


def test_is_responsible(get_plugin):
    sklearn_plugin = get_plugin

    sklearn_file = sklearn_plugin.is_responsible(
        os.path.abspath("tests/files/tf.py")
    )
    not_sklearn_file = sklearn_plugin.is_responsible(
        os.path.abspath("tests/files/Dockerfile")
    )

    assert sklearn_file
    assert not not_sklearn_file


def test_parse_tf_file(get_plugin):
    tf_plugin = get_plugin
    tf_file = os.path.abspath("tests/files/tf.py")

    artifact = tf_plugin.parse_file(tf_file, "tf.py")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 19

    assert make_id("tf.py", "file", "tf.py") in ids
    assert make_id("tf.py", "TFRecordWriter", "variable", "writer") in ids
    assert make_id("tf.py", "TFRecordWriter", "path", "path/to/file") in ids
    assert make_id("tf.py", "SparseConditionalAccumulator", "variable", "q") in ids
    assert make_id("tf.py", "SparseConditionalAccumulator", "dtype", "tf.float32") in ids
    assert make_id("tf.py", "SparseConditionalAccumulator", "name", "Q") in ids
    assert make_id("tf.py", "SparseConditionalAccumulator", "shape", "tf.TensorShape([1, 5, 2, 8])") in ids
    assert make_id("tf.py", "RNNEstimator", "variable", "estm") in ids
    assert make_id("tf.py", "RNNEstimator", "head", "tf.estimator.RegressionHead()") in ids
    assert make_id("tf.py", "RNNEstimator", "sequence_feature_columns", "['test']") in ids
    assert make_id("tf.py", "RNNEstimator", "cell_type", "lstm") in ids
    assert make_id("tf.py", "RNNEstimator", "units", "[32, 16]") in ids
    assert make_id("tf.py", "ClusterSpec", "variable", "spec") in ids
    assert make_id("tf.py", "ClusterSpec", "cluster", "{'ps': ['1'], 'worker': ['2']}") in ids
    assert make_id("tf.py", "SimpleClusterResolver", "variable", "simple_resolver") in ids
    assert make_id("tf.py", "SimpleClusterResolver", "cluster_spec", "spec") in ids
    assert make_id("tf.py", "Graph", "params", "default") in ids
    assert make_id("tf.py", "RegressionHead", "params", "default") in ids
    assert make_id("tf.py", "TensorShape", "dims", "[1, 5, 2, 8]") in ids
