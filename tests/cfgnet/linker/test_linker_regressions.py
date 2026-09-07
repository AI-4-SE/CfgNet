"""Regression tests for skipped values and per-network linker selection."""

import pytest

from cfgnet.linker.equality_linker import EqualityLinker
from cfgnet.linker.linker_manager import LinkerManager
from cfgnet.network.network import Network
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.network.nodes import ArtifactNode, OptionNode, ProjectNode, ValueNode


@pytest.fixture
def network(tmp_path):
    """Build a network with two artifacts containing matching values."""
    cfg = NetworkConfiguration(
        project_root_abs=str(tmp_path),
        enable_static_blacklist=True,
        enable_internal_links=False,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False,
    )
    root = ProjectNode('project', str(tmp_path))
    result = Network('project', root, cfg)
    for filename in ('a.json', 'b.json'):
        artifact = ArtifactNode(filename, filename, 'json', root)
        for name, value in (('empty', ''), ('level', 'DEBUG'), ('port', '8000')):
            option = OptionNode(name, '1')
            artifact.add_child(option)
            option.add_child(ValueNode(value))
    return result


@pytest.mark.parametrize('skipped_value', ['', 'DEBUG'])
def test_skipped_value_does_not_stop_linking(network, skipped_value):
    """A skipped value must not prevent subsequent valid links."""
    linker = EqualityLinker()
    linker.network = network
    linker.enable_internal_links = False
    # Put each regression trigger first, independently of artifact metadata.
    values = network.get_nodes(ValueNode)
    linker._find_target_nodes = lambda: sorted(
        values, key=lambda node: node.name != skipped_value
    )
    linker.create_links()
    assert len(network.links) == 1
    link = next(iter(network.links))
    assert link.node_a.name == link.node_b.name == '8000'


def test_network_configuration_controls_linkers(network, monkeypatch):
    """Defaults enable linking; explicit disabling survives save and load."""
    monkeypatch.setattr(LinkerManager, 'all_linkers', [EqualityLinker()])
    monkeypatch.setattr(LinkerManager, 'enabled_linkers', [])
    LinkerManager.apply_linkers(network)
    assert len(network.links) == 1

    network.links.clear()
    network.cfg.enabled_linkers = []
    network.save()
    restored = Network.load_network(network.project_root)
    # A different CLI invocation's selection must not override saved settings.
    monkeypatch.setattr(LinkerManager, 'enabled_linkers', LinkerManager.all_linkers)
    LinkerManager.apply_linkers(restored)
    assert not restored.links

    restored.cfg.enabled_linkers = ['equality']
    LinkerManager.apply_linkers(restored)
    assert len(restored.links) == 1
