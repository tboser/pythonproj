"""End-to-end generation tests for the template.

For each variant, generate a project into a tmpdir and run its own
`just lint` + `just test`. If the generated project passes, the template
is healthy.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from copier import run_copy

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


skip_no_just = pytest.mark.skipif(not _have("just"), reason="just not installed")
skip_no_uv = pytest.mark.skipif(not _have("uv"), reason="uv not installed")


def _stage_template_source(tmp_path: Path) -> Path:
    """Copy the template to a non-git tmpdir so run_copy uses the working tree,
    not the last committed ref. Lets us iterate without committing first."""
    staged = tmp_path / "_template_source"
    shutil.copytree(
        TEMPLATE_ROOT,
        staged,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"),
        symlinks=True,
    )
    return staged


def _generate(tmp_path: Path, variant: str, package: str = "acme") -> Path:
    src = _stage_template_source(tmp_path)
    dst = tmp_path / package
    run_copy(
        src_path=str(src),
        dst_path=str(dst),
        data={
            "variant": variant,
            "project_name": package,
            "package_name": package,
            "description": f"Test {variant} project",
            "author_name": "Test User",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "python_version": "3.13",
            "license": "MIT",
            "open_source": True,
        },
        defaults=True,
        unsafe=True,
        quiet=True,
    )
    return dst


def _run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(
            f"Command {cmd} failed in {cwd}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


@skip_no_just
@skip_no_uv
@pytest.mark.parametrize("variant", ["library", "app", "cli"])
def test_generated_project_lints_and_tests(tmp_path: Path, variant: str) -> None:
    project = _generate(tmp_path, variant)
    assert (project / "pyproject.toml").exists()
    assert (project / "AGENTS.md").exists()
    assert (project / "CLAUDE.md").exists()
    _run(["just", "install"], project)
    _run(["just", "lint"], project)
    _run(["just", "test"], project)


@pytest.mark.parametrize("variant", ["library", "app", "cli"])
def test_generated_project_has_expected_files(tmp_path: Path, variant: str) -> None:
    project = _generate(tmp_path, variant, package="myproj")
    must_exist = [
        "pyproject.toml",
        "justfile",
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "SECURITY.md",
        ".editorconfig",
        ".pre-commit-config.yaml",
        ".python-version",
        ".gitignore",
        "LICENSE",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS",
        ".github/dependabot.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/workflows/lint.yml",
        ".github/workflows/test.yml",
        "src/myproj/__init__.py",
        "src/myproj/py.typed",
        "tests/test_smoke.py",
    ]
    for rel in must_exist:
        assert (project / rel).exists(), f"missing {rel}"

    library_only = [
        "mkdocs.yml",
        "docs/index.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        ".readthedocs.yaml",
        ".github/workflows/release.yml",
        ".github/workflows/docs.yml",
    ]
    app_only = [
        "Dockerfile",
        "compose.yaml",
        ".env.example",
        "src/myproj/settings.py",
        "src/myproj/main.py",
        "src/myproj/__main__.py",
    ]
    cli_only = [
        "src/myproj/cli.py",
        "src/myproj/__main__.py",
    ]

    expected = {"library": library_only, "app": app_only, "cli": cli_only}[variant]
    for rel in expected:
        assert (project / rel).exists(), f"missing {variant}-specific {rel}"

    for other_variant, files in {
        "library": library_only,
        "app": app_only,
        "cli": cli_only,
    }.items():
        if other_variant == variant:
            continue
        for rel in files:
            if rel in expected:
                continue
            assert not (project / rel).exists(), f"{variant} should not have {rel}"
