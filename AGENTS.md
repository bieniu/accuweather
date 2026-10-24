<!-- CLAUDE.md is a symlink to this file — edit only AGENTS.md -->
# Instructions for AI Agents

## Repository context
- Python async wrapper for the AccuWeather API
- Published as `accuweather` on PyPI
- Public API surface is the `AccuWeather` class in `accuweather/__init__.py`

## Project layout
```
accuweather/
├── __init__.py     # Main client (AccuWeather)
├── const.py        # Endpoints, URL templates, language map
├── exceptions.py   # AccuweatherError, ApiError, InvalidApiKeyError, etc.
├── utils.py        # URL construction, response parsing helpers
└── py.typed        # PEP 561 marker
tests/
├── conftest.py     # Fixtures (loads JSON, syrupy snapshot config)
├── test_init.py    # 8 tests covering all public methods + error paths
├── fixtures/       # JSON response fixtures (4 files)
└── snapshots/      # Syrupy amber snapshots
```

## Python and environment
- Requires Python >=3.14, package manager is `uv`
- Setup: `./scripts/setup-local-env.sh` (creates `.venv`, runs `uv sync --all-groups` + `prek install`)
- All config in `pyproject.toml` (no `ruff.toml`, `setup.cfg`, etc.)

## Linting, formatting, type checking
- Lint: `ruff check .`
- Format: `ruff format .` (check-only: `ruff format --check .`)
- Types: `ty check accuweather`
- Pre-commit: `prek run` (runs ruff, ty, codespell, and builtin hooks)
- CI runs `lint -> test`; lint job runs `ruff check` + `ruff format --check` + `ty check` + `prek run`
- Ruff is configured with `select = ["ALL"]` and a curated ignore list — do not add new ignores without strong reason

## Testing
- Run tests: `pytest --timeout=30 --cov=accuweather --cov-report=xml --error-for-skips`
- HTTP mocking via `aiointercept` — never hit real API endpoints in tests
- Snapshot testing via `syrupy` — snapshots live in `tests/snapshots/` (amber format)
- When parsed output changes, update both fixtures and snapshots together
- Async test fixture scope: `asyncio_default_fixture_loop_scope = "session"` (set in `pyproject.toml`)
- Tests create `aiohttp.ClientSession()` directly (not injected)

## Implementation guidelines
- All I/O is async; caller provides `aiohttp.ClientSession`
- JSON parsing uses `orjson`; URL construction uses `yarl.URL`
- Endpoints and URL templates live in `accuweather/const.py` — do not scatter URLs
- API key is redacted from logs via `clean_url()` in utils
- Response structure cleanup (key removal, lowercasing, temperature splitting) lives in `utils.py` parse functions
- HTTP 401/403 → `InvalidApiKeyError`, 503 with specific message → `RequestsExceededError`, other errors → `ApiError`
- Lazy logging: `_LOGGER.debug("msg %s", value)`
- Preserve the public API and return shapes; breaking changes need explicit discussion
