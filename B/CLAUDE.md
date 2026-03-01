# ML Experiment Tracker

## Commands

```bash
python manage.py run          # Start dev server on :8000
python manage.py seed         # Load sample data
python manage.py migrate      # Create/update database tables
python manage.py check        # Run all checks (ruff + pytest)
pytest                        # Run test suite
ruff check .                  # Lint — runs automatically after every edit via PostToolUse hook
```

## Repo Map

```
manage.py                  # CLI entrypoint
experiments/               # Experiment CRUD: routes, models, schemas, templates
runs/                      # Run logging & comparison: routes, models, schemas, templates
tags/                      # Experiment tagging: routes, models, schemas
exports/                   # Data export (JSON/CSV): routes, models, schemas
shared/                    # DB engine, config, base model, base templates
tests/                     # Fixed test suite (DO NOT MODIFY)
.claude/                   # Agent config: hooks, skills, commands
pyproject.toml             # Ruff config
```

## Definition of Done

Before submitting, all of these must pass:
1. `pytest` exits 0 (all tests pass)
2. `ruff check .` exits 0 (no lint errors)
3. No new dependencies added to requirements.txt without asking
4. Existing tests are not modified or deleted
5. If pytest fails, read the error, fix it, run again. Do not modify the test to make it pass.
6. Existing tests in tests/ are the source of truth -- they are never modified or deleted.

## Coding Conventions

- Models: SQLAlchemy declarative, one model per file in `{feature}/models.py`
- Schemas: Pydantic BaseModel in `{feature}/schemas.py`
- Routes: FastAPI APIRouter in `{feature}/routes.py`, mounted in `manage.py`
- Templates: Jinja2 in `{feature}/templates/`, extend `shared/templates/base.html`
- Types: all function signatures have type hints. Use Pydantic schemas for all API request/response bodies.
- Status fields: use the `ExperimentStatus` / `RunStatus` enums, never raw strings
- Every file starts with a 4-line header comment (path, purpose, why, relevant files)

## Do Not

- Do not modify anything in `tests/`
- Do not delete or rename existing endpoints
- Do not add dependencies without asking
- Do not put business logic in templates
- Do not use raw strings for status values (use the enums)
