# Contributing to FastVK

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
git clone https://github.com/ndugram/fastvk.git
cd fastvk

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

## Development Workflow

### 1. Create a branch

```bash
git checkout -b feature/your-feature
# or
git checkout -b fix/your-bug-fix
```

### 2. Make changes

- Write clean, typed code
- Add tests for new features
- Update docstrings and examples if needed

### 3. Test

```bash
pytest
pytest --cov=fastvk
pytest -m "not slow"
```

### 4. Code quality

```bash
ruff format .
ruff check .
mypy fastvk/
```

### 5. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add RedisStorage backend"
git commit -m "fix: handle failed=3 in long poll correctly"
git commit -m "docs: add webhook example"
```

Prefixes: `feat` · `fix` · `docs` · `refactor` · `test` · `chore`

### 6. Open a PR

Push your branch and open a pull request on GitHub. Keep PRs focused — one feature or fix per PR.

## Pull Request Checklist

- [ ] Code is typed and passes `mypy`
- [ ] `ruff check` passes with no errors
- [ ] Tests added or updated
- [ ] Examples updated if the public API changed
- [ ] Commit messages follow Conventional Commits

## Reporting Issues

**Bugs** — include Python version, fastvk version, minimal reproduction script, and the full traceback.

**Feature requests** — describe the problem you're solving and how the API would look.

Open issues at: <https://github.com/ndugram/fastvk/issues>

## Release Process

1. Bump `version` in `pyproject.toml`
2. Push to `master` — CI builds and publishes to PyPI automatically, then creates a GitHub release
