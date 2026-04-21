# pythonproj — opinionated Python project template

A [Copier](https://copier.readthedocs.io/) template for bootstrapping Python
projects with the stack I actually use and the AI-development guardrails I
actually want.

**Stack** (default and only):

- [`uv`](https://docs.astral.sh/uv/) for env + packaging
- [`hatchling`](https://hatch.pypa.io/) as build backend (+ `uv-dynamic-versioning` for libraries)
- [`ruff`](https://docs.astral.sh/ruff/) for lint + format
- [`ty`](https://docs.astral.sh/ty/) for type checking
- [`pytest`](https://docs.pytest.org/) + `pytest-asyncio` + `inline-snapshot` + `dirty-equals` + `vcrpy`
- [`just`](https://github.com/casey/just) as task runner
- [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for config (app variant)
- [`cyclopts`](https://cyclopts.readthedocs.io/) for CLIs (cli variant)
- [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/) + `mkdocstrings` for docs (library variant)
- `AGENTS.md` as the canonical agent-guidance doc; `CLAUDE.md` is a symlink

**Variants:**

| Variant | For | Extras |
|---------|-----|--------|
| `library` | PyPI-publishable libraries | docs site, `uv-dynamic-versioning`, PyPI OIDC release workflow, CHANGELOG |
| `app` | Services / applications | `pydantic-settings` scaffold, `Dockerfile`, `compose.yaml`, `.env.example` |
| `cli` | CLI tools | `cyclopts` scaffold, entry point |

**AI guardrails** (applied to every variant):

- Distilled `AGENTS.md` with strong opinions (no `getattr`/`hasattr`, registry-over-if-chains, full type annotations, no inline comments, etc.)
- `.github/PULL_REQUEST_TEMPLATE.md` with the explicit "AI-generated code reviewed line-by-line" checkbox
- `.claude/settings.json` with a sensible Claude Code permission set
- Optional Claude auto-review workflow (enable with `include_claude_review: true`)

## Usage

```bash
# One-off: generate a new project
uvx copier copy gh:tboser/pythonproj my-new-project
cd my-new-project
just install
just all

# Later: pull updates from the template
cd my-new-project
uvx copier update
```

## Developing the template

```bash
uv sync --all-extras
uv run pytest          # runs generation tests: generates each variant into a tmpdir, runs just lint + just test inside
```

## Why not cookiecutter?

Cookiecutter generates once and you're on your own. Copier supports
`copier update` — template improvements propagate to already-generated
projects with a 3-way merge. That's the whole ballgame.

## License

MIT
