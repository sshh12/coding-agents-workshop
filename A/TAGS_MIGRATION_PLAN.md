# Tags Migration Plan: experiment_tags table -> tags_csv column

**Status: ON HOLD** (approved by tech lead, blocked on product sign-off)
**Last updated:** 2024-09-14
**Owner:** Maria (before she left), now unassigned

## Background

The current tagging implementation uses the `experiment_tags` join table (see
`Tag` model in `app.py`). This works but has performance concerns:
- Listing experiments filtered by tag requires a JOIN
- The `experiment_tags` table has no index on `name` column
- Each tag is a separate row, so experiments with many tags generate many rows

The proposed v2 approach stores tags as a comma-separated string directly on
the `experiments` table in a new `tags_csv` column. This is implemented in
`tags_v2.py` and uses `/labels` endpoints instead of `/tags`.

## Migration Steps

### Step 1: Add tags_csv column to experiments table
```sql
ALTER TABLE experiments ADD COLUMN tags_csv TEXT DEFAULT '';
```
- Run this migration manually (we don't have Alembic set up)
- The column should be nullable with empty string default

### Step 2: Backfill tags_csv from experiment_tags
```python
# Run this in a Python shell connected to the DB
from app import SessionLocal, Experiment, Tag

db = SessionLocal()
for exp in db.query(Experiment).all():
    tags = db.query(Tag).filter(Tag.experiment_id == exp.id).all()
    exp.tags_csv = ",".join(t.name for t in tags)
db.commit()
```

### Step 3: Enable v2 tag routes
- Set `ENABLE_TAGS=true` in environment (see `config.py`)
- Uncomment the router registration in `tags_v2.py`
- The v2 routes use `/labels` to avoid collision with v1 `/tags` routes
- Both v1 and v2 will run in parallel during migration

### Step 4: Update API consumers
- Update `api_stuff/exp_helpers.py` `validate_tag_data()` to work with CSV format
- Update the experiment detail template to read from `tags_csv`
- Update any code in `utils/metrics.py` that reads tags

### Step 5: Remove v1 tag infrastructure
- Remove `Tag` model from `app.py`
- Remove `experiment_tags` table
- Remove v1 `/tags` endpoints from `app.py`
- Rename v2 `/labels` endpoints to `/tags`
- Remove `tags` relationship from `Experiment` model

### Step 6: Cleanup
- Delete `tags_v2.py` (move code into `app.py` or `api_stuff/`)
- Update `config.py` to remove `ENABLE_TAGS` flag
- Update tests in `tests/test_app.py`

## Risks

- Data loss if backfill script (step 2) fails partway through
- CSV format doesn't support commas in tag names (need to document this)
- The `tags_csv` column has no length limit, could grow very large
- Two different tag formats in the API during migration (v1 returns objects, v2 returns strings)

## Files Affected

| File | Change |
|------|--------|
| `app.py` | Remove Tag model, remove /tags endpoints (step 5) |
| `tags_v2.py` | Uncomment routes, register router (step 3) |
| `config.py` | ENABLE_TAGS flag controls activation |
| `api_stuff/exp_helpers.py` | Update validate_tag_data() for CSV format |
| `utils/metrics.py` | Update get_tags() / add_tag() helpers |
| `stuff/templates/experiment.html` | Update tag display to use CSV data |
| `tests/test_app.py` | Update tag tests for new format |

## Decision Log

- 2024-07-12: Maria proposed CSV approach, Jake opposed (before he left)
- 2024-08-03: Team voted 3-2 in favor of CSV approach
- 2024-09-01: Maria started implementation in tags_v2.py
- 2024-09-14: Maria left company, migration put ON HOLD
- 2024-10-xx: Alex said he'd look at it "when he has time"
- No further updates
