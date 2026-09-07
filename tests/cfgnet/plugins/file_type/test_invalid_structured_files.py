"""Regression tests for malformed structured configuration files."""

import pytest

from cfgnet.network.nodes import ProjectNode
from cfgnet.plugins.file_type.json_plugin import JsonPlugin
from cfgnet.plugins.file_type.toml_plugin import TomlPlugin
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin


@pytest.mark.parametrize(
    ("plugin", "suffix", "content"),
    [
        (JsonPlugin(), ".json", '{"option": }'),
        (TomlPlugin(), ".toml", "option = ["),
        (YAMLPlugin(), ".yaml", "option: [unclosed"),
    ],
)
def test_invalid_files_do_not_create_artifacts(
    tmp_path, plugin, suffix, content
):
    """Failed parsing must not leave a seemingly valid empty artifact behind."""
    file_path = tmp_path / f"invalid{suffix}"
    file_path.write_text(content, encoding="utf-8")
    root = ProjectNode("project", str(tmp_path))

    artifact = plugin.parse_file(str(file_path), file_path.name, root)

    assert artifact is None
    assert not root.children


@pytest.mark.parametrize(
    ("plugin", "suffix", "content"),
    [
        (JsonPlugin(), ".json", "{}"),
        (TomlPlugin(), ".toml", ""),
        (YAMLPlugin(), ".yaml", ""),
    ],
)
def test_valid_empty_files_create_artifacts(tmp_path, plugin, suffix, content):
    """An empty but valid document remains distinct from a parsing failure."""
    file_path = tmp_path / f"empty{suffix}"
    file_path.write_text(content, encoding="utf-8")
    root = ProjectNode("project", str(tmp_path))

    artifact = plugin.parse_file(str(file_path), file_path.name, root)

    assert artifact is not None
    assert root.children == [artifact]
