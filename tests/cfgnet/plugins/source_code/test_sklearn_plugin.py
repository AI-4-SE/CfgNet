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

from cfgnet.plugins.source_code.sklearn_plugin import SklearnPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = SklearnPlugin()
    return plugin


def test_is_responsible(get_plugin):
    sklearn_plugin = get_plugin

    sklearn_file = sklearn_plugin.is_responsible(
        os.path.abspath("tests/files/sklearn.py")
    )
    not_sklearn_file = sklearn_plugin.is_responsible(
        os.path.abspath("tests/files/Dockerfile")
    )

    assert sklearn_file
    assert not not_sklearn_file


def test_parse_dockerfile(get_plugin):
    sklearn_plugin = get_plugin
    sklearn_file = os.path.abspath("tests/files/sklearn.py")

    artifact = sklearn_plugin.parse_file(sklearn_file, "sklearn.py")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 31

    # FILE PATH
    assert make_id("sklearn.py", "file", "sklearn.py") in ids

    # LogisticRegression
    assert (
        make_id("sklearn.py", "LogisticRegression", "variable", "logistic_reg")
        in ids
    )
    assert (
        make_id(
            "sklearn.py",
            "LogisticRegression",
            "multi_class",
            "multinomial",
        )
        in ids
    )
    assert (
        make_id("sklearn.py", "LogisticRegression", "solver", "lbfgs") in ids
    )
    assert make_id("sklearn.py", "LogisticRegression", "C", "a") in ids

    # RandomForestClassifier
    assert (
        make_id(
            "sklearn.py",
            "RandomForestClassifier",
            "variable",
            "rnd_forest",
        )
        in ids
    )
    assert (
        make_id("sklearn.py", "RandomForestClassifier", "n_estimators", "100")
        in ids
    )
    assert (
        make_id("sklearn.py", "RandomForestClassifier", "criterion", "2")
        in ids
    )

    # MLPCLassifier
    assert make_id("sklearn.py", "MLPClassifier", "variable", "mlp") in ids
    assert (
        make_id(
            "sklearn.py",
            "MLPClassifier",
            "hidden_layer_sizes",
            "(13, 13)",
        )
        in ids
    )

    # SVC
    assert make_id("sklearn.py", "SVC", "class_weight", "None") in ids
    assert make_id("sklearn.py", "SVC", "probability", "True") in ids

    # ColumnTransformer
    assert make_id("sklearn.py", "ColumnTransformer", "variable", "pre") in ids
    assert (
        make_id(
            "sklearn.py",
            "ColumnTransformer",
            "transformers",
            "[('OneHotEncoder', OneHotEncoder(drop=bin_cols)), ('Scale', StandardScaler())]",
        )
        in ids
    )
    assert (
        make_id("sklearn.py", "ColumnTransformer", "remainder", "passthrough")
        in ids
    )

    # GridSearchCV
    assert make_id("sklearn.py", "GridSearchCV", "variable", "grid_SCV") in ids
    assert make_id("sklearn.py", "GridSearchCV", "estimator", "pre") in ids
    assert make_id("sklearn.py", "GridSearchCV", "param_grid", "grid") in ids

    # OneHotEncoder
    assert make_id("sklearn.py", "OneHotEncoder", "drop", "bin_cols") in ids

    # RandomForrestGenerator
    assert (
        make_id("sklearn.py", "RandomForestRegressor", "variable", "rf") in ids
    )
    assert (
        make_id(
            "sklearn.py",
            "RandomForestRegressor",
            "n_jobs",
            "available_cpu_count()",
        )
        in ids
    )

    # OneHotEncoder
    assert (
        make_id("sklearn.py", "OneHotEncoder", "variable", "onehotencoder")
        in ids
    )
    assert (
        make_id("sklearn.py", "OneHotEncoder", "categorical_features", "[0]")
        in ids
    )

    # GridSearchCV
    assert (
        make_id("sklearn.py", "GridSearchCV", "variable", "grid_search") in ids
    )
    assert make_id("sklearn.py", "GridSearchCV", "n_jobs", "-1") in ids

    # DBSCAN
    assert make_id("sklearn.py", "DBSCAN", "variable", "db") in ids
    assert make_id("sklearn.py", "DBSCAN", "eps", "0.1") in ids
    assert make_id("sklearn.py", "DBSCAN", "min_samples", "1") in ids
    assert make_id("sklearn.py", "DBSCAN", "metric", "precomputed") in ids

    # LinearSVC
    assert make_id("sklearn.py", "LinearSVC", "variable", "linear_svc") in ids
    assert make_id("sklearn.py", "LinearSVC", "params", "default") in ids


def test_possible_values(get_plugin):
    sklearn_plugin = get_plugin
    sklearn_file = os.path.abspath("tests/files/sklearn.py")

    artifact = sklearn_plugin.parse_file(sklearn_file, "sklearn.py")
    nodes = artifact.get_nodes()

    param = next(
        filter(
            lambda x: x.id
            == make_id("sklearn.py", "LogisticRegression", "C", "a"),
            nodes,
        )
    )

    assert len(param.possible_values) == 3
