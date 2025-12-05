# Contributing

This project follows a strict workflow suitable for PyPI packages. The goals are reproducibility, traceability, and low-entropy collaboration.

---

## Branching Strategy

Use short-lived branches created from `main`.

Choose the prefix based on intent:

- `feature/<scope>` — new feature or API surface
- `fix/<scope>` — bug correction
- `hotfix/<scope>` — urgent patch
- `release/<version>` — version bump + changelog prep
- `refactor/<scope>` — internal code restructuring
- `perf/<scope>` — targeted performance improvement
- `docs/<scope>` — documentation updates only
- `chore/<scope>` — formatting, lint setup, config updates
- `ci/<scope>` — CI/CD workflow changes
- `ops/<scope>` — operational or packaging scripts

Scopes should be short and specific:

`feature/cli-parser`, `fix/token-refresh`, `perf/vectorized-path`.

---

## Commit Message Format

Follow this pattern:

`<type>: <short summary>`

`<body explaining motivation and behavior>`

Valid `<type>` values mirror branch prefixes:

`feature`, `fix`, `hotfix`, `refactor`, `perf`, `docs`, `chore`, `ci`, `ops`.

### Examples:

**`feature: add token-based auth`**

Adds `TokenAuthenticator` class with pluggable backend.

**`fix: correct timezone handling`**

Ensures `datetime` fields are normalized to UTC on ingest.

---

## Code Style

- Keep modules small and composable.
- Follow DRY and avoid unnecessary abstraction.
- Prefer readability over clever constructs.
- Ensure every public function has a docstring describing:
  - purpose
  - parameters
  - return shape
  - error conditions

---

## Testing

All contributions must include tests matching the scope of change.

- **New features** → accompanying positive and negative tests.
- **Fixes** → a test that would fail before the fix and pass after.
- **Performance changes** → add benchmarks if applicable.

---

## Versioning & Releases

The project uses semantic versioning:

- **MAJOR** — breaking API change
- **MINOR** — new backward-compatible features
- **PATCH** — backward-compatible bug fixes

### Release flow:

1.  Create branch: `release/<version>`.
2.  Update `__version__` in the package root.
3.  Update `CHANGELOG.md`.
4.  Open PR to `master`.
5.  After merge, tag the commit: `git tag v<version>`.
6.  Publish to PyPI using the recommended build backend.

---

## Environment Setup

1.  **Create a virtual environment:**
    python -m venv .venv
2.  **Activate it:**
    source .venv/bin/activate
3.  **Install dependencies:**
    pip install -e .[dev]

### Run tests:
pytest

## Pull Requests

- Keep PRs focused.
- Explain the motivation of your change.
- Link issues if applicable.
- PR must be green on CI.

---

## Security

Report vulnerabilities privately. **Do not open a public issue for security defects.**