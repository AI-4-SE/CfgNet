"""Regression tests for selecting the checked-out history during history analysis."""

import pytest

from cfgnet.analyze.analyzer import Analyzer
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.vcs.git import Git
from cfgnet.vcs.git_history import GitHistory
from tests.utility.temporary_repository import TemporaryRepository


@pytest.fixture
def repository():
    """Create a main branch and an alphabetically later feature branch."""
    temporary = TemporaryRepository('tests/test_repos/port_db_repo')
    repo = temporary.repo
    repo.git.branch('-M', 'main')
    repo.create_head('zzz-feature', 'HEAD~1').checkout()
    return temporary


@pytest.mark.parametrize('detached', [False, True])
def test_select_checked_out_history(repository, detached):
    """Use HEAD even when origin and the first local branch point elsewhere."""
    repo = repository.repo
    repo.git.update_ref('refs/remotes/origin/main', 'main')
    repo.git.symbolic_ref('refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
    if detached:
        repo.git.checkout('HEAD~1')
    expected = list(repo.iter_commits('HEAD'))[::-1]
    history = GitHistory(Git(repository.root))
    assert history.commits == expected
    assert history.commits[-1] != repo.heads.main.commit


def test_no_main_branch_required(repository):
    """A repository with only a feature branch remains analyzable."""
    repository.repo.delete_head('main', force=True)
    history = GitHistory(Git(repository.root))
    assert history.commits[-1] == repository.repo.head.commit


@pytest.mark.parametrize('detached', [False, True])
def test_analyze_checked_out_history_and_restore_head(repository, detached, capsys):
    """Analysis stops at the original commit and restores the original HEAD."""
    repo = repository.repo
    original_commit = repo.head.commit
    if detached:
        repo.git.checkout(original_commit.hexsha)
    cfg = NetworkConfiguration(
        project_root_abs=repository.root,
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False,
        enable_file_type_plugins=False,
        system_level=False,
    )
    Analyzer(cfg).analyze_commit_history()
    assert 'Analyzed commits: 2' in capsys.readouterr().out
    assert repo.head.commit == original_commit
    assert repo.head.is_detached == detached
    if not detached:
        assert repo.active_branch.name == 'zzz-feature'
