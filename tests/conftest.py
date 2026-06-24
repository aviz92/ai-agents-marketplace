"""Global fixtures shared across all marketplace test modules."""

from pathlib import Path

import pytest

import marketplace.installer as _installer
from marketplace.kind_catalog import loader as catalog
from marketplace.kind_catalog.models import Plugin, Rule, Skill


@pytest.fixture(autouse=True)
def _reset_template_env() -> None:
    """Clear the Jinja2 Environment cache before each test.

    Prevents a stale Environment (pointing at a previous marketplace root)
    from leaking into subsequent tests that monkeypatch get_marketplace_root.
    """
    _installer.clear_template_env_cache()


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """An empty project directory to install artifacts into."""
    return tmp_path / "project"


@pytest.fixture
def fake_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fake marketplace root that load_catalog() resolves to."""
    monkeypatch.setattr(catalog, "get_marketplace_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def sample_skill() -> Skill:
    return Skill(
        id="sample-skill",
        name="Sample Skill",
        description="A skill used in tests",
        version="1.0.0",
        content="# Sample skill body\n",
    )


@pytest.fixture
def sample_plugin() -> Plugin:
    return Plugin(
        id="sample-plugin",
        name="Sample Plugin",
        description="A plugin used in tests",
        version="1.0.0",
        content="# Sample plugin body\n",
    )


@pytest.fixture
def sample_rule() -> Rule:
    return Rule(
        id="sample-rule",
        name="Sample Rule",
        description="A rule used in tests",
        version="1.0.0",
        globs=["src/**/*.py"],
        always_apply=True,
        content="# Sample rule body\n",
    )
