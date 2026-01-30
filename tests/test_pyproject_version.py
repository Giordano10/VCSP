"""
Tests to ensure packaging metadata defines a real version.
"""
from pathlib import Path
import tomllib


def test_pyproject_version_is_defined() -> None:
    """Ensure pyproject.toml declares a non-placeholder version."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as handle:
        data = tomllib.load(handle)
    project = data.get("project", {})
    version = project.get("version")
    assert project.get("name") == "vcsp-guard"  # noqa: S101
    assert version is not None  # noqa: S101
    assert version != "0.0.0"  # noqa: S101
