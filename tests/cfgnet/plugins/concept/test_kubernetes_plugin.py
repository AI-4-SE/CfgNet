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

import pytest

from cfgnet.plugins.concept.kubernetes_plugin import KubernetesPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = KubernetesPlugin()
    return plugin


def test_is_responsible(get_plugin):
    kubernetes_plugin = get_plugin

    # Test valid Kubernetes files
    assert kubernetes_plugin.is_responsible("/path/to/deployment.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/service.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/configmap.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/secret.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/ingress.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/pod.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/statefulset.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/daemonset.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/job.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/cronjob.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/persistentvolume.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/persistentvolumeclaim.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/namespace.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/role.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/rolebinding.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/serviceaccount.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/networkpolicy.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/horizontalpodautoscaler.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/verticalpodautoscaler.yaml")
    assert kubernetes_plugin.is_responsible("/path/to/customresourcedefinition.yaml")

    # Test invalid files
    assert not kubernetes_plugin.is_responsible("/path/to/not-k8s.yaml")
    assert not kubernetes_plugin.is_responsible("/path/to/random.txt")
    assert not kubernetes_plugin.is_responsible("/path/to/config.json")
    assert not kubernetes_plugin.is_responsible("/path/to/deployment.yml")  # Wrong extension
    assert not kubernetes_plugin.is_responsible("/path/to/k8s-deployment.yaml")  # Wrong pattern
    assert not kubernetes_plugin.is_responsible("/path/to/deployment.yaml.txt")  # Wrong extension


def test_parse_kubernetes_file(get_plugin):
    kubernetes_plugin = get_plugin
    artifact = kubernetes_plugin.parse_file("tests/files/deployment.yaml", "deployment.yaml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) > 0

    # Test Pod resource
    assert make_id("deployment.yaml", "kind", "Pod") in ids
    assert make_id("deployment.yaml", "metadata", "name", "test-pod") in ids
    assert make_id("deployment.yaml", "metadata", "labels", "app", "test-app") in ids
    assert make_id("deployment.yaml", "metadata", "labels", "environment", "test") in ids
    assert make_id("deployment.yaml", "spec", "containers", "name", "nginx-container") in ids
    assert make_id("deployment.yaml", "spec", "containers", "image", "nginx:1.21") in ids
    assert make_id("deployment.yaml", "spec", "containers", "ports", "containerPort", "80") in ids
    assert make_id("deployment.yaml", "spec", "containers", "ports", "protocol", "TCP") in ids
    assert make_id("deployment.yaml", "spec", "containers", "env", "name", "DB_HOST") in ids
    assert make_id("deployment.yaml", "spec", "containers", "env", "value", "localhost") in ids
    assert make_id("deployment.yaml", "spec", "containers", "resources", "requests", "memory", "64Mi") in ids
    assert make_id("deployment.yaml", "spec", "containers", "resources", "limits", "cpu", "500m") in ids

    # Test Deployment resource
    assert make_id("deployment.yaml", "kind", "Deployment") in ids
    assert make_id("deployment.yaml", "metadata", "name", "test-deployment") in ids
    assert make_id("deployment.yaml", "spec", "replicas", "3") in ids
    assert make_id("deployment.yaml", "spec", "template", "spec", "containers", "name", "web-server") in ids

    # Test Service resource
    assert make_id("deployment.yaml", "kind", "Service") in ids
    assert make_id("deployment.yaml", "metadata", "name", "test-service") in ids
    assert make_id("deployment.yaml", "spec", "type", "ClusterIP") in ids
    assert make_id("deployment.yaml", "spec", "ports", "port", "80") in ids
    assert make_id("deployment.yaml", "spec", "ports", "targetPort", "80") in ids

    # Test ConfigMap resource
    assert make_id("deployment.yaml", "kind", "ConfigMap") in ids
    assert make_id("deployment.yaml", "metadata", "name", "test-config") in ids
    assert make_id("deployment.yaml", "data", "database_url", "postgresql://localhost:5432/mydb") in ids
    assert make_id("deployment.yaml", "data", "environment", "development") in ids

    # Test Secret resource
    assert make_id("deployment.yaml", "kind", "Secret") in ids
    assert make_id("deployment.yaml", "metadata", "name", "test-secret") in ids
    assert make_id("deployment.yaml", "type", "Opaque") in ids
    assert make_id("deployment.yaml", "data", "username", "dGVzdC11c2Vy") in ids

    # Test Ingress resource
    assert make_id("deployment.yaml", "kind", "Ingress") in ids
    assert make_id("deployment.yaml", "metadata", "name", "test-ingress") in ids
    assert make_id("deployment.yaml", "metadata", "annotations", "nginx.ingress.kubernetes.io/rewrite-target", "/") in ids
    assert make_id("deployment.yaml", "spec", "rules", "host", "test.example.com") in ids
    assert make_id("deployment.yaml", "spec", "rules", "http", "paths", "path", "/api") in ids
    assert make_id("deployment.yaml", "spec", "rules", "http", "paths", "pathType", "Prefix") in ids


def test_config_types(get_plugin):
    kubernetes_plugin = get_plugin
    artifact = kubernetes_plugin.parse_file("tests/files/deployment.yaml", "deployment.yaml")
    nodes = artifact.get_nodes()

    # Test name config type
    name_node = next(
        filter(
            lambda x: x.id == make_id("deployment.yaml", "metadata", "name", "test-pod"),
            nodes,
        )
    )
    assert name_node.config_type == ConfigType.NAME

    # Test image config type
    image_node = next(
        filter(
            lambda x: x.id == make_id("deployment.yaml", "spec", "containers", "image", "nginx:1.21"),
            nodes,
        )
    )
    assert image_node.config_type == ConfigType.IMAGE

    # Test port config type
    port_node = next(
        filter(
            lambda x: x.id == make_id("deployment.yaml", "spec", "containers", "ports", "containerPort", "80"),
            nodes,
        )
    )
    assert port_node.config_type == ConfigType.PORT

    # Test URL config type
    url_node = next(
        filter(
            lambda x: x.id == make_id("deployment.yaml", "data", "database_url", "postgresql://localhost:5432/mydb"),
            nodes,
        )
    )

    assert url_node.config_type == ConfigType.URL
