"""CLI regression tests for reference updates during validation."""

from pathlib import Path

from click.testing import CliRunner

from cfgnet.launcher import main
from cfgnet.network.network import Network
from tests.utility.temporary_repository import TemporaryRepository


def test_conflicts_preserve_reference_on_repeated_validation():
    """Unresolved conflicts remain detectable without changing the reference."""
    repo = TemporaryRepository(
        'tests/test_repos/maven_docker/0001-Add-Docker-and-maven-file.patch'
    )
    runner = CliRunner()
    result = runner.invoke(main, ['init', repo.root])
    assert result.exit_code == 0, result.output
    reference = next(Path(repo.root).glob('.cfgnet/network/*.pickle'))
    original = reference.read_bytes()

    repo.apply_patch(
        'tests/test_repos/maven_docker/0002-Provoke-two-conflicts.patch'
    )
    for _ in range(2):
        result = runner.invoke(main, ['validate', repo.root])
        assert result.exit_code == 1, result.output
        assert reference.read_bytes() == original
        conflicts, _ = Network.load_network(repo.root).validate()
        assert conflicts


def test_conflict_free_validation_updates_reference():
    """Matching changes become the reference for subsequent validation."""
    repo = TemporaryRepository(
        'tests/test_repos/equal_values/0001-Add-two-package.json-files.patch'
    )
    runner = CliRunner()
    result = runner.invoke(main, ['init', repo.root])
    assert result.exit_code == 0, result.output
    original_pairs = Network.load_network(repo.root).get_pairs()

    repo.apply_patch(
        'tests/test_repos/equal_values/0002-Change-config-values-equally.patch'
    )
    conflicts, expected = Network.load_network(repo.root).validate()
    assert not conflicts
    assert expected.get_pairs() != original_pairs

    result = runner.invoke(main, ['validate', repo.root])
    assert result.exit_code == 0, result.output
    assert Network.load_network(repo.root).get_pairs() == expected.get_pairs()
    result = runner.invoke(main, ['validate', repo.root])
    assert result.exit_code == 0, result.output


def test_accept_conflicts_updates_reference():
    """Acceptance reports conflicts and saves the current network and config."""
    repo = TemporaryRepository(
        'tests/test_repos/maven_docker/0001-Add-Docker-and-maven-file.patch'
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ['init', '--enable-static-blacklist', repo.root]
    )
    assert result.exit_code == 0, result.output
    original = Network.load_network(repo.root)

    repo.apply_patch(
        'tests/test_repos/maven_docker/0002-Provoke-two-conflicts.patch'
    )
    conflicts, expected = original.validate()
    assert conflicts

    result = runner.invoke(main, ['validate', '--accept', repo.root])
    assert result.exit_code == 0, result.output
    for conflict in conflicts:
        assert str(conflict) in result.output
    accepted = Network.load_network(repo.root)
    assert accepted.get_pairs() == expected.get_pairs()
    assert accepted.cfg == original.cfg

    result = runner.invoke(main, ['validate', repo.root])
    assert result.exit_code == 0, result.output
    conflicts, _ = accepted.validate()
    assert not conflicts
