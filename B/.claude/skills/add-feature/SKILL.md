---
name: add-feature
description: "Add a new feature to the ML Experiment Tracker following existing patterns"
---

When adding a new feature to this project, follow these steps:

1. Create a new directory: `{feature_name}/`
2. Add these files following existing patterns in `experiments/` or `runs/`:
   - `models.py` - SQLAlchemy model with header comment
   - `schemas.py` - Pydantic schemas for request/response
   - `routes.py` - FastAPI APIRouter with endpoints
   - `templates/` - Jinja2 templates extending `shared/templates/base.html`
3. Register the router in `manage.py`
4. Add a migration in the `migrate` command if new tables are needed
5. Run `python manage.py check` to verify (ruff + pytest)

Every file must start with a 4-line header comment: path, purpose, why, relevant files.
Use enums for status fields, never raw strings.
