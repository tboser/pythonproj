# pythonproj — opinionated Python project template

A [Copier](https://copier.readthedocs.io/) template for bootstrapping Python
projects with the stack I actually use and the AI-development guardrails I
actually want.

- [Quickstart](#quickstart)
- [Variants](#variants)
- [The stack](#the-stack)
- [What you get](#what-you-get)
- [Working in a generated project](#working-in-a-generated-project)
  - [The `just` commands](#the-just-commands)
  - [Typical dev loop](#typical-dev-loop)
  - [Writing tests](#writing-tests)
  - [Library: cutting a release](#library-cutting-a-release)
  - [Library: docs](#library-docs)
  - [App: Docker + settings](#app-docker--settings)
  - [CLI: adding commands](#cli-adding-commands)
  - [Managing dependencies](#managing-dependencies)
  - [Pre-commit hooks](#pre-commit-hooks)
  - [Upgrading to a newer template version](#upgrading-to-a-newer-template-version)
- [AI development guardrails](#ai-development-guardrails)
- [Developing the template itself](#developing-the-template-itself)
- [Why not cookiecutter?](#why-not-cookiecutter)

## Quickstart

```bash
uvx copier copy gh:tboser/pythonproj my-new-project
cd my-new-project
just install
just all        # format + lint + test
```

You'll be asked 8 questions (variant, project name, author, license, etc.).
Defaults are sensible; `--defaults --trust` skips them.

## Variants

| Variant   | For                        | Extras over the shared core                                              |
|-----------|----------------------------|--------------------------------------------------------------------------|
| `library` | PyPI-publishable libraries | `mkdocs-material` + `mkdocstrings`, `.readthedocs.yaml`, `uv-dynamic-versioning`, PyPI OIDC release workflow, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` |
| `app`     | Services / applications    | `pydantic-settings` scaffold, `Dockerfile` (uv multi-stage), `compose.yaml`, `.env.example`, `python -m {{pkg}}` entry point |
| `cli`     | CLI tools                  | `cyclopts` scaffold, console-script entry point, `python -m {{pkg}}` entry point |

All three share: src-layout, `py.typed`, ruff + ty + pytest configs, `justfile`,
`AGENTS.md`/`CLAUDE.md` symlink, PR + issue templates, CODEOWNERS, SECURITY.md,
Dependabot (uv + actions + docker for app), `.editorconfig`, zizmor pre-commit
hook, CI workflows (lint + test, both with `concurrency: cancel-in-progress`).

## The stack

| Tool                                                                              | Role                                   |
|-----------------------------------------------------------------------------------|----------------------------------------|
| [`uv`](https://docs.astral.sh/uv/)                                                | env + package manager (never `pip`)    |
| [`hatchling`](https://hatch.pypa.io/)                                             | build backend                          |
| [`uv-dynamic-versioning`](https://github.com/ninoseki/uv-dynamic-versioning)      | version from git tag (library only)    |
| [`ruff`](https://docs.astral.sh/ruff/)                                            | lint + format                          |
| [`ty`](https://docs.astral.sh/ty/)                                                | type checker                           |
| [`pytest`](https://docs.pytest.org/)                                              | test runner                            |
| [`inline-snapshot`](https://15r10nk.github.io/inline-snapshot/)                   | assertion snapshotting                 |
| [`dirty-equals`](https://dirty-equals.helpmanual.io/)                             | flexible equality matchers             |
| [`pytest-recording`](https://github.com/kiwicom/pytest-recording)                 | HTTP recording for external-API tests (pytest wrapper over VCRpy) |
| [`just`](https://github.com/casey/just)                                           | task runner                            |
| [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | config loader (app variant)          |
| [`cyclopts`](https://cyclopts.readthedocs.io/)                                    | CLI framework (cli variant)            |
| [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/)                 | docs site (library variant)            |
| [`zizmor`](https://docs.zizmor.sh/)                                               | GitHub Actions security linter         |

## What you get

Generated projects ship with:

**Code quality**
- `ruff` (E/W/F/I/B/C4/UP/SIM rules, 100 char lines)
- `ty` type checking (strict on the whole project)
- `pytest` with `xfail_strict`, `filterwarnings=["error"]`, `asyncio_mode="auto"`
- Pre-commit hooks: `ruff check --fix`, `ruff format`, `zizmor`

**Supply chain & security**
- Dependabot weekly updates: `uv` deps, GitHub Actions, Docker (app variant),
  with cooldown windows (7d default, 30d semver-major)
- `zizmor.yml` policy allowing tag-pins for trusted publishers (`actions/*`, `astral-sh/*`, etc.), hash-pin required for everyone else
- Workflows: least-privilege `permissions: contents: read` at workflow level,
  job-scoped writes in release, `persist-credentials: false` on every checkout,
  `enable-cache: false` in release workflows to avoid cache-poisoning

**GitHub hygiene**
- `SECURITY.md`, `CODEOWNERS`, `CODE_OF_CONDUCT.md` (library only)
- Issue templates: bug report, feature request, disabled blank issues
- PR template with "AI-generated code reviewed line-by-line" checkbox
- `.editorconfig`

**AI assistance**
- `AGENTS.md` — the project constitution (stack, style, testing philosophy, AI contribution rules)
- `CLAUDE.md` — symlink to `AGENTS.md`, so there's one canonical source
- `.claude/settings.json` — Claude Code permission defaults (allow read, uv/just/ruff/ty/pytest/gh; deny `git push --force`, `git reset --hard`, `rm -rf`)

## Working in a generated project

### The `just` commands

Every generated project has a `justfile` with these recipes. Run `just` (no args) to see the list.

| Recipe                | What it does                                                   |
|-----------------------|----------------------------------------------------------------|
| `just install`        | `uv sync --all-extras` + `uv run pre-commit install`           |
| `just sync`           | `uv sync --all-extras` (no pre-commit)                         |
| `just lint`           | `ruff check` + `ruff format --check` + `ty check`              |
| `just lint-fix`       | `ruff check --fix` + `ruff format`                             |
| `just format`         | `ruff format` only                                             |
| `just test`           | `pytest`                                                       |
| `just test-v`         | `pytest -v`                                                    |
| `just test-cov`       | `pytest --cov --cov-report=term-missing`                       |
| `just test-cov-html`  | `pytest --cov --cov-report=html` (outputs `htmlcov/`)          |
| `just snapshot-create`| `pytest --inline-snapshot=create` (writes new snapshots)       |
| `just snapshot-fix`   | `pytest --inline-snapshot=fix` (updates snapshots after change)|
| `just docs`           | `mkdocs serve` (library only — local dev server on 127.0.0.1)  |
| `just docs-build`     | `mkdocs build --strict` (library only)                         |
| `just all`            | `format` + `lint` + `test`                                     |
| `just template-update`| `uvx copier update` — pull latest template changes             |

### Typical dev loop

```bash
# Change code
just lint-fix          # auto-format + auto-fix lint
just test              # run tests
git add -A
git commit -m "..."    # pre-commit runs ruff + zizmor on your changes
git push               # CI runs lint + test
```

Pre-commit is wired to block commits that fail ruff or zizmor. If you need to
bypass (please don't), `git commit --no-verify`.

### Writing tests

Tests live in `tests/` and **mirror `src/<package>/` 1:1** — every source
module gets a matching `test_<module>.py`. This is enforced by convention,
not by code, but it's the rule.

**Fast unit tests** — no I/O, no network, no sleeps. Use `pytest.mark.parametrize`
rather than duplicating test bodies.

**External APIs** — combine `pytest-recording` (pytest wrapper over VCRpy
that records real HTTP to YAML cassettes, auto-named after the test),
`inline-snapshot` (expected values auto-write into your test code), and
`dirty-equals` (flexible matchers for timestamps, IDs, ranges).

```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization", "x-api-key"],
        "record_mode": "once",
    }
```

```python
# tests/test_client.py
import pytest
from inline_snapshot import snapshot
from dirty_equals import IsPositiveInt, IsNow

@pytest.mark.vcr
def test_get_user():
    response = client.get_user(42)
    assert response.body == snapshot()        # inline-snapshot auto-fills this
    assert response.id == IsPositiveInt
    assert response.fetched_at == IsNow(delta=3)
```

Cassettes save to `tests/cassettes/<test_module>/<test_name>.yaml` automatically.

First run: `just snapshot-create` writes the `snapshot()` values into your test
file. After intentional API changes: `just snapshot-fix` updates snapshots.
Re-record a cassette: delete its file and rerun, or `pytest --record-mode=all`.
Never edit `snapshot(...)` values by hand.

### Library: cutting a release

Versions come from git tags via `uv-dynamic-versioning`. Flow:

```bash
git tag v0.2.0              # semver
git push origin v0.2.0
```

The `Release` workflow runs automatically:
1. `build` job — `uv build` produces wheel + sdist, uploads as artifact
2. `publish` job — publishes to PyPI via OIDC (no PyPI token needed; configure [trusted publishing](https://docs.pypi.org/trusted-publishers/) once for the project)
3. `github-release` job — creates a GitHub release with auto-generated notes from PRs since last tag

**First-time setup** for PyPI trusted publishing: on pypi.org, add a pending
trusted publisher for your package pointing at `{github_username}/{package}`,
workflow `release.yml`, environment `pypi`.

**Optional — Codecov coverage upload.** The generated `test.yml` workflow
uploads coverage to [Codecov](https://about.codecov.io/). As of 2025, Codecov
requires a token for **public** repositories (previously tokenless). The
upload is configured with `fail_ci_if_error: false`, so not setting this up
doesn't break CI — you just don't get coverage dashboards.

To enable:

1. Sign up at codecov.io with your GitHub account and install the app on your repo
2. Copy the upload token from the repo settings on Codecov
3. Add it to your GitHub repo as a secret named `CODECOV_TOKEN`:
   ```bash
   gh secret set CODECOV_TOKEN --repo {github_username}/{package}
   ```
4. Next CI run will publish coverage; add a Codecov badge to your README if you want

If you don't care about coverage dashboards, ignore this — the workflow will
no-op on the upload step.

### Library: docs

```bash
just docs          # live-reload server at http://127.0.0.1:8000
just docs-build    # one-shot strict build into site/
```

Docs source is in `docs/`. `docs/reference.md` uses `mkdocstrings` to
auto-render the public API from docstrings:

```markdown
# API Reference

::: {{ package_name }}
```

Add new pages by creating `docs/<page>.md` and listing them under `nav:` in
`mkdocs.yml`.

Hosting via [Read the Docs](https://readthedocs.org/): point RTD at your
repo — `.readthedocs.yaml` already configures it to install with `uv` and
build with `mkdocs`.

### App: Docker + settings

```bash
cp .env.example .env        # then edit .env
uv run python -m <package>  # run locally

docker build -t <package> . # multi-stage build: ~100MB slim image
docker run --rm --env-file .env <package>

# Or:
docker compose up           # reads .env automatically
```

Settings live in `src/<package>/settings.py` as a `pydantic-settings`
`BaseSettings` subclass. Add fields, document each with an attribute
docstring; they auto-bind to env vars:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    """Postgres connection string."""

    max_workers: int = 4
    """Worker pool size. Override with MAX_WORKERS=8."""
```

`.env` is gitignored. `.env.example` is committed — keep it in sync with
`Settings`.

### CLI: adding commands

The scaffolded CLI uses [`cyclopts`](https://cyclopts.readthedocs.io/) and
lives in `src/<package>/cli.py`:

```python
@app.command
def greet(name: str, *, excited: bool = False) -> None:
    """Say hi to NAME."""
    suffix = "!" if excited else "."
    print(f"Hello, {name}{suffix}")
```

Cyclopts derives the flag parser from your type annotations. `--help` is
generated from the docstring + type info.

Two entry points ship by default:
- `<package>` — console script (from `[project.scripts]` in `pyproject.toml`)
- `python -m <package>` — via `__main__.py`

When commands start doing real Python orchestration (multiple files, shared
types, complex flags), split `cli.py` into a `cli/` package with a module
per subcommand (the `rd` CLI pattern).

### Managing dependencies

```bash
uv add pydantic                       # runtime dep
uv add --dev pytest-mock              # dev dep (the `dev` group)
uv add --extra benchmark matplotlib   # optional extra
uv remove pydantic                    # remove
uv sync                               # sync after pyproject edits
uv tree                               # dependency tree
uv lock --upgrade                     # bump all deps to latest-allowed
uv lock --upgrade-package pydantic    # bump just one
```

`uv.lock` is committed. Dependabot opens weekly PRs to bump deps, GHA
versions, and (app variant) Docker base images — all with a 7-day cooldown
so compromised releases don't auto-land immediately.

### Pre-commit hooks

Installed by `just install`. Runs on every `git commit`:

| Hook             | Runs                                                |
|------------------|-----------------------------------------------------|
| `ruff-check-fix` | `ruff check --fix` on Python files                  |
| `ruff-format`    | `ruff format` on Python files                       |
| `zizmor`         | GitHub Actions security linter on workflow YAML     |

Run all hooks on every file (not just changed ones):
```bash
uv run pre-commit run --all-files
```

### Upgrading to a newer template version

When the template itself gets improvements:

```bash
cd my-project
just template-update       # or: uvx copier update
```

Copier does a 3-way merge: your changes are preserved, template changes
land where they don't conflict, conflicts drop into `.rej` files for you
to resolve.

`.copier-answers.yml` tracks your original answers — the update uses them,
so you don't answer questions again.

## AI development guardrails

This template is built assuming you're using an AI coding assistant. The
guardrails exist to keep the codebase consistent and high-quality regardless.

**`AGENTS.md`** — the single source of truth. Read by humans and agents
alike. Contains stack, conventions, testing philosophy, and rules like:
- Never add an AI as a git co-author
- Never use `getattr`/`hasattr` — break type safety
- Use dict-registry pattern over long if-elif chains
- Enums or Literal types for constrained values
- No inline comments (docstrings + attribute docstrings only)
- All imports at top of file (CLI entry points exempt)
- Confirm scope before starting non-trivial work
- Escalate public-API changes to a human

**`CLAUDE.md`** — symlink to `AGENTS.md`. One canonical file, many names.
Add more symlinks (`GEMINI.md`, `COPILOT_INSTRUCTIONS.md`, etc.) as you want.

**PR template** — explicit checkbox: *"Any AI-generated code has been
reviewed line-by-line by the human PR author, who stands by it."*

**`.claude/settings.json`** — default Claude Code permissions: allow read,
edit, uv/just/ruff/ty/pytest/gh; deny `git push --force`, `git reset --hard`,
`rm -rf`. Override locally in `.claude/settings.local.json` (gitignored).

## Developing the template itself

```bash
git clone https://github.com/tboser/pythonproj
cd pythonproj
uv sync
uv run pytest -v           # generation tests — generate each variant, run just lint + test inside each
```

The test suite (`tests/test_generation.py`) stages the template into a
non-git tmpdir and runs `copier copy` on the working tree. This means you
can iterate without committing every change — edit, save, `uv run pytest`.

### Adding a feature

1. Edit files under `template/` (or add new ones — remember: any file
   containing Jinja must end in `.jinja`).
2. If the file is variant-specific, add a line to `_exclude` in
   `copier.yml`.
3. If you add a required file, also add it to `must_exist` /
   `library_only` / `app_only` / `cli_only` in `tests/test_generation.py`.
4. `uv run pytest` — all six tests should pass.
5. Optional manual check: `uvx copier@9.10.2 copy --vcs-ref=HEAD --defaults --trust . /tmp/generated-test`

### Known Copier gotchas (hit them all while building this)

- **`.jinja` suffix is required on any file containing Jinja.** Without it,
  Copier copies the file verbatim — so a `justfile` with `{% if ... %}`
  ships unrendered and breaks `just`. Also applies to `.python-version.jinja`,
  workflow files using template vars, etc.
- **Symlinks in the template are resolved at read-time, before rendering.**
  `CLAUDE.md -> AGENTS.md` in the template dir would fail because `AGENTS.md`
  doesn't exist yet (only `AGENTS.md.jinja` does). Solution: create the
  symlink in a post-generation `_tasks` hook.
- **`.copier-answers.yml` is NOT auto-generated.** Needs an explicit
  `.copier-answers.yml.jinja` in the template with `{{ _copier_answers|to_nice_yaml -}}`.

## Why not cookiecutter?

Cookiecutter generates once and you're on your own. Copier supports
`copier update` — template improvements propagate to already-generated
projects with a 3-way merge. That's the deciding feature.

## License

MIT — see [LICENSE](./LICENSE).
