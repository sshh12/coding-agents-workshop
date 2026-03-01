# Agent Race: Narrator Notes

## The Prompt

Give both agents this exact prompt:

> Add a new feature: experiment tagging. Users should be able to add tags to experiments via a new endpoint `POST /api/experiments/{id}/tags` and see tags displayed on the experiment detail page in the dashboard. Follow the existing patterns in the codebase. Run the tests to verify your changes.

---

## Setup

### Terminal Layout

Two terminal windows side by side. Left = Version A (Before). Right = Version B (After).

### Before Starting

1. Make sure both apps run cleanly:

```bash
# Terminal 1 (Version A)
cd ~/coding-agents-workshop/A
pip install -r requirements.txt
python app.py
# Ctrl+C after confirming it starts

# Terminal 2 (Version B)
cd ~/coding-agents-workshop/B
pip install -r requirements.txt
python manage.py run
# Ctrl+C after confirming it starts
```

2. Verify B's tests pass:

```bash
cd ~/coding-agents-workshop/B
pytest
```

3. Reset both to a clean state (no uncommitted changes).

### Starting the Race

1. Open two terminal windows side by side
2. Navigate to `A/` in the left terminal, `B/` in the right
3. Paste the exact same prompt into both agents simultaneously
4. Narrate as they work

---

## What to Watch For

### Version A (The Struggle)

**Agent reads the CLAUDE.md** (0:00-0:30)
- The rules file is ~500 lines of rambling project history, meeting notes, and an outdated file map
- No runnable commands, no repo map that's useful
- Agent gets no useful signal from it — just burns tokens

**Agent searches for the right files** (0:30-2:00)
- Looks at `app.py` (600+ lines, everything in one file)
- Greps for "tags" and finds **9 files** with conflicting concepts:
  - `config.py` — `ENABLE_TAGS` flag + misleading comment pointing to `tags_v2.py`
  - `tags_v2.py` — abandoned CSV-based tag implementation using `/labels` endpoint
  - `TAGS_MIGRATION_PLAN.md` — dead-end migration doc (status: ON HOLD)
  - `utils/metrics.py` — `MetricTag` class (NOT experiment tags, but name collision)
  - `utils/metrics.py` — raw SQL `get_tags()` / `add_tag()` with wrong column names
  - `api_stuff/exp_helpers.py` — `validate_tag_data()` expecting different field names
  - `app.py` — misleading TODO comment pointing to `utils/metrics.py` for "tag helpers"
  - `app.py` — `do_thing()` call forcing trace through cryptic `h.py`
- Discovers templates are in `stuff/templates/`, not where you'd expect
- May read `h.py` and have no idea what `do_thing()` or `fmt()` do

**Agent attempts implementation** (2:00-4:00)
- Has to reconcile 8+ different "stories" about how tags work
- Has to figure out where to add the endpoint: `app.py`? `api_stuff/misc.py`? `tags_v2.py`?
- No schemas or models to follow as a pattern; everything is inline dicts and raw strings
- No type hints, no Pydantic schemas, status is raw strings, `h.py` accepts/returns `Any`, bare `except: pass` swallows errors
- Status is a raw string, no enum to reference for how tags should work
- May follow the misleading breadcrumbs to `tags_v2.py` or `TAGS_MIGRATION_PLAN.md`
- Pydantic 2.9.0 is in requirements.txt but never imported — no schema to follow, so the agent validates manually
- Agent sees sanitize() used in create_experiment and may copy the broken function for tag validation
- requirements.txt has alembic and redis installed but not configured — agent might try to import them

**Agent tries to test** (1:30-2:00)
- Finds `tests/test_app.py` which only tests `1+1==2`
- No useful test patterns to follow
- Writes its own tests that validate its own code — the self-grading trap
- Tests always pass because the agent wrote both the code and the tests
- Silent `except: pass` blocks mean errors are swallowed — bugs hide

**Narration points:**
- "Notice the agent modified the test file — it's grading its own homework"
- "It grepped 'tags' and got hits in 9 files with 8 different meanings — that's the trap"
- "It found `tags_v2.py` and `TAGS_MIGRATION_PLAN.md` — dead ends that waste time"
- "The starting tests were `1+1==2`. The agent rewrote them to test its own code. That's theater, not verification."
- "No types, no schemas, no enums. The agent is guessing at every interface shape."
- "Bare `except: pass` blocks — errors are invisible. The agent can't self-correct."
- "Pydantic is installed but nobody wrote a single schema. The agent is doing by hand what one BaseModel would handle."
- "Look at the import — sanitize() from h.py. The agent is copying a broken security function into new code."
- "Both codebases have Pydantic installed. Only B uses it. Same library, different outcomes."

### Version B (The Flow)

**Agent reads the CLAUDE.md** (0:00-0:15)
- ~50 lines, crisp
- Sees exact commands: `python manage.py run`, `pytest`, `ruff check .`
- Sees repo map: `experiments/` for experiment code, `runs/` for run code, `tags/` for tags
- Knows the definition of done: tests pass, ruff clean, no new deps
- Sees explicit rules: "do not modify tests", "if pytest fails, read the error and fix it"

**Agent finds the right files immediately** (0:15-0:45)
- Goes to `tags/` folder (obvious from name and CLAUDE.md repo map)
- Reads `tags/routes.py` — sees GET endpoint + detailed TODO comment for POST
- TODO says: follow pattern in `runs/routes.py`, accept `TagCreate`, return `TagResponse` with 201
- Reads `runs/routes.py` to see the pattern
- Model and schema already exist — just needs the route

**Agent implements the feature** (0:45-2:00)
- Implements `POST /api/experiments/{id}/tags` following the runs pattern
- Handles 404 (experiment not found) and 409 (duplicate tag)
- Full type hints everywhere, Pydantic schemas define exact shapes, enums for status, ruff configured, explicit HTTPException with descriptive messages
- ~20-30 lines of code, all in `tags/routes.py`
- Everything is signposted: TODO told it what to do, pattern file told it how

**Agent runs verification** (2:00-3:00)
- Runs `pytest` — all 28 tests pass (including the 4 tag tests that were failing)
- Runs `ruff check .` — no lint errors
- Done. Clean exit.

**Narration points:**
- "The agent went straight to `tags/` — the CLAUDE.md told it exactly where to look"
- "It found a TODO comment that was basically a spec: endpoint, schema, status codes, test file"
- "It followed the pattern from `runs/routes.py`. Copy, adapt, done."
- "Pydantic schemas are doing the heavy lifting. The agent knows exactly what fields to pass."
- "All 28 tests pass. The agent didn't write tests — it made the existing ones pass."
- "Both codebases have Pydantic installed. Only B uses it. Same library, wildly different outcomes."

---

## Timestamped Highlights (from recorded race)

Timestamps based on screen recordings (`A.mov` = 43s, `B.mov` = 76s). Side-by-side video: `race-side-by-side.mp4`.

### Version A — Frame-by-Frame

| Time | What's on screen | Narrator cue |
|------|-----------------|--------------|
| 0:03 | Reads `config.py`, starts thinking | "It skipped straight past the 500-line CLAUDE.md — no useful signal there anyway" |
| 0:04 | Reads `tests/test_app.py` | "It found the tests — `1+1==2`. That's all it has to work with." |
| 0:05 | Reads `requirements.txt` | "It sees Pydantic in the requirements but there are no schemas anywhere to follow" |
| 0:07 | Declares "I have a clear picture" | "Seven seconds in and it thinks it understands the codebase. It never searched for 'tags'. Never read `h.py`. Never found `tags_v2.py`." |
| 0:09 | Writes `ExperimentTag` model in `app.py` | "Everything goes into the god file. Model, routes, all in `app.py`." |
| 0:14 | POST and GET tag endpoints written | "It built the endpoints — but look: it never called `sanitize()` on the tag name. The existing code has `sanitize(name)` with a security comment. The agent missed the pattern." |
| 0:17 | Updates experiment detail route + template | "It's wiring up the template — finding the `stuff/` folder. Adding CSS inline." |
| 0:21 | Template done with tag pill badges | "Tags render as badges. But the template is getting more inline CSS dumped in." |
| 0:26 | Rewrites entire test file — 11 new tests | "Here it is — it deleted the 3 placeholder tests and wrote 11 of its own. The self-grading trap. These tests validate *its* code." |
| 0:28 | `python -m pytest` → command not found | "First test attempt fails — `python` not on PATH. Minor, but B won't have this problem." |
| 0:29 | `.venv/bin/python -m pytest` → no module | "Second attempt — pytest isn't installed in the venv." |
| 0:30 | `pip install pytest httpx` | "Third attempt: installing its own test dependencies. B had this from the start." |
| 0:36 | Tests finally running | "On the third try, tests are running." |
| 0:38 | All 11 tests pass. Done. | "11 tests pass. But they're the agent's own tests. It wrote the code *and* the grade. That's the fundamental problem." |

### Version B — Frame-by-Frame

| Time | What's on screen | Narrator cue |
|------|-----------------|--------------|
| 0:01 | CLAUDE.md auto-loaded | "CLAUDE.md is loaded before any tool calls. 50 lines — repo map, commands, definition of done." |
| 0:05 | Spawns exploration sub-agent | "It spawns a focused sub-agent to scan the codebase. Structured approach." |
| 0:10 | Reads `runs/routes.py` | "Ten seconds in — already reading the pattern file. It knows where to look." |
| 0:12 | Runs `find` on `tags/` directory | "Twelve seconds in — found the `tags/` directory. The CLAUDE.md told it exactly where to look." |
| 0:14 | Reads `tags/models.py` | "It found the pre-built tag model. The scaffolding is already in place." |
| 0:19 | Reads experiment detail template | "Reading the template where tags will be displayed. Also checks `pyproject.toml` for lint config." |
| 0:47 | Exploration sub-agent finishes (33 tool calls, 45k tokens) | "48 seconds of exploration — 33 parallel reads. It has full context on the entire codebase." |
| 0:58 | "The TODO comment spells out exactly what's needed" | "This is the money quote. The agent explicitly says: the TODO told it what to build. The scaffolding worked." |
| 1:01 | Implementation: `create_tag` endpoint in `tags/routes.py` | "One file. Pydantic schemas for validation. `HTTPException` with descriptive messages. 404, 409, 201 — all handled." |
| 1:04 | Cleans up `# noqa: F401` comment on import | "A nice detail — it removed the lint suppression comment because `TagCreate` is now actually used." |
| 1:05 | `pytest tests/test_tags.py` → `python` not found | "Same PATH issue as A — but watch what happens next." |
| 1:07 | 6 tag tests pass | "Six tag tests pass on the first real run. Including the 4 pre-written ones that were failing before." |
| 1:09 | All 28 tests pass + `ruff check .` clean | "28 tests pass. Ruff clean. One file changed. Done." |
| 1:13 | Summary: lists what it built vs what was already there | "Look at the summary — it acknowledges what was already in place: model, schema, template, router. It only had to write the endpoint." |

### Key Contrasts to Call Out

| Moment | Version A | Version B |
|--------|-----------|-----------|
| First useful action | 0:03 — reads `config.py` | 0:05 — spawns structured exploration |
| Finds tag-related code | 0:07 — claims "clear picture" without searching | 0:12 — finds `tags/` directory, reads model |
| Implementation starts | 0:09 — dumps model + routes into god file | 1:01 — adds 1 endpoint to `tags/routes.py` |
| Files changed | 3 (app.py, template, tests) | 1 (tags/routes.py) |
| Test approach | 0:26 — rewrites test file (self-grading) | 1:07 — makes pre-written tests pass |
| Test env issues | 3 attempts (no python, no pytest, pip install) | 2 attempts (no python, then works) |
| sanitize() pattern | Copies `sanitize()` into tag endpoint | Uses Pydantic schemas — nothing broken to copy |
| Total time | 38s (fast, but unverified) | 1m 12s (thorough, verified) |

---

## Timing

| Phase | Expected Time |
|-------|--------------|
| Agent reads rules + explores | 0:00-0:15 (B) / 0:00-1:00 (A) |
| Agent implements feature | 0:15-1:30 (B) / 1:00-2:00 (A) |
| Agent verifies | 1:30-2:30 (B) / 2:00-2:30 (A) |
| **Total** | **~2-4 min each** |

Both agents often finish at roughly the same time — sometimes A is faster. **Don't narrate this as a speed race.** The story is about *what they produced*: B made 4 pre-written tests pass in 1 file. A modified 3 files including the test file — writing tests that validate its own code (self-grading). A also copied the broken `sanitize()` function into its tag endpoint — pattern pollution in real time.

---

## Fallback Plan

If the live demo fails (network issues, agent misbehaves, etc.):

1. **First option:** Say "Let me show you what this looked like when I ran it earlier" and play `race-side-by-side.mp4` (A and B stitched side by side with headers). Use the timestamped highlights above to narrate.

2. **Second option:** Walk through the two codebases side by side manually:
   - Show `A/app.py` (600+ lines) vs `B/tags/routes.py` (~40 lines with TODO)
   - Show `A/CLAUDE.md` (~500 lines of noise) vs `B/CLAUDE.md` (50 lines of signal)
   - Show `A/` grep for "tag" → 9 files vs `B/tags/` → everything in one place
   - Show `A/tests/test_app.py` (`assert 1+1==2`) vs `B/tests/test_tags.py` (4 real failing tests as spec)
   - Ask: "If you were an agent, which codebase would you rather work in?"

3. **Key point either way:** The difference isn't the agent. It's the codebase. Same model, same prompt, wildly different outcomes.

---

## Pre-Race Checklist

- [ ] Both apps start without errors
- [ ] B's tests pass (`pytest` in `B/`)
- [ ] Both terminals visible on projector
- [ ] Font size large enough for back of room
- [ ] Pre-recorded backup video ready (`race-side-by-side.mp4`)
- [ ] Git state clean in both directories
- [ ] Prompt copied to clipboard, ready to paste

---

## Programmatic Race (Headless)

For running the race without manual narration:

### Quick Start

```bash
# 1. Reset both repos to clean state
./race-reset.sh

# 2. Run the race (both agents in parallel)
./race.sh

# 3. Analyze results
./race-analyze.sh
```

### Custom Prompt

```bash
./race.sh --prompt "Add a CSV export endpoint at POST /api/experiments/{id}/export that returns experiment data with all runs as a downloadable CSV. Follow existing patterns."
```

### What the Scripts Do

- **`race.sh`**: Launches `claude -p` in both A/ and B/ simultaneously with `--output-format stream-json`. Captures timing, tool calls, and full output to `race-results/<timestamp>/`.
- **`race-reset.sh`**: Runs `git checkout -- .` and `git clean -fd` in both repos. Deletes any SQLite DB files.
- **`race-analyze.sh`**: Parses the stream-json output to show timing, tool usage breakdown (Read/Write/Edit/Glob/Grep/Bash counts), token usage, files modified, and test results.

### Expected Results

| Metric | Version A (Before) | Version B (After) |
|--------|-------------------|-------------------|
| Time to complete | 1-3 min | 2-4 min |
| Tool calls | 15-30 | 30-65 |
| Files modified | 3 (god file, template, tests) | 1 (`tags/routes.py`) |
| Test outcome | Agent writes its own tests (self-grading) | All 28 tests pass (including 4 pre-written tag tests) |
| Test integrity | Agent modifies test file freely | Tests are protected; agent cannot change the spec |
| Pattern pollution | Agent copies broken `sanitize()` into new tag code | Agent uses Pydantic schemas — no broken patterns to copy |
| Correct implementation | Usually works, but unverified | Verified by immutable test suite |

**Key insight:** Version A may finish just as fast — but speed isn't the point. The point is *verification* and *pattern quality*. A writes its own tests, which always pass its own code (the classic self-grading trap). A also copies the broken `sanitize()` function into new code — pattern pollution. B's tests were written in advance and protected; the agent had to make *them* pass, not write its own. B uses Pydantic schemas and proper HTTPException — clean patterns in, clean patterns out.

### Alternative Race Prompts

1. **Tagging** (default): "Add experiment tagging with POST /api/experiments/{id}/tags..."
2. **Bug fix**: "Users report that creating an experiment with status 'completed' doesn't work correctly. Find and fix the bug. Run tests to verify."
3. **New metric**: "Add a new metric field 'f1_score' (float, 0-1) to runs. Update the model, API, and detail page to support it."
