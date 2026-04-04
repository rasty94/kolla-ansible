import os
import pytest

from pathlib import Path


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for tests that need files."""
    d = tmp_path / "config"
    d.mkdir()
    return d


@pytest.fixture
def sample_globals_yaml(tmp_path):
    """Return path to a sample globals.yml for short tests."""
    f = tmp_path / "globals.yml"
    f.write_text("---\nexample_var: test\n")
    return f


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch, tmp_path):
    """Ensure tests don't depend on user env or filesystem paths."""
    # set a predictable HOME and KOLLA_CONFIG_DIR
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("KOLLA_CONFIG_DIR", str(tmp_path / "config"))
    return tmp_path
