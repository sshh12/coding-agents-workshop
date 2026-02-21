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
- The rules file is ~240 lines of rambling project history
- No runnable commands, no repo map
- Agent gets no useful signal from it

**Agent searches for the right files** (0:30-2:00)
- Looks at `app.py` (500+ lines, everything in one file)
- Finds `api_stuff/misc.py` with some routes randomly placed there
- Discovers templates are in `stuff/templates/`, not where you'd expect
- May read `h.py` and have no idea what `do_thing()` or `fmt()` do

**Agent attempts implementation** (2:00-4:00)
- Has to figure out where to add the endpoint: `app.py`? `api_stuff/misc.py`?
- No schemas or models to follow as a pattern; everything is inline dicts and raw strings
- Status is a raw string, no enum to reference for how tags should work
- May break the god file by editing in the wrong place

**Agent tries to test** (4:00-5:00)
- Finds `tests/test_app.py` which only tests `1+1==2`
- No useful test patterns to follow
- May write its own test that makes its own code pass (the classic trap)
- Silent `except: pass` blocks mean errors are swallowed

**Narration points:**
- "Notice how much time the agent spends just figuring out WHERE things are"
- "It found the templates in `stuff/templates/` -- not exactly discoverable"
- "The only test is `1+1==2`. The agent has no verification to run."
- "It's guessing at patterns because there are no schemas or enums to follow"

### Version B (The Flow)

**Agent reads the CLAUDE.md** (0:00-0:15)
- 50 lines, crisp
- Sees exact commands: `python manage.py run`, `pytest`, `ruff check .`
- Sees repo map: `experiments/` for experiment code, `runs/` for run code
- Knows the definition of done: tests pass, ruff clean, no new deps

**Agent finds the right files immediately** (0:15-0:45)
- Goes to `experiments/` folder (obvious from name)
- Reads `experiments/models.py` -- sees SQLAlchemy model with header comment
- Reads `experiments/schemas.py` -- sees Pydantic schemas with typed enums
- Reads `experiments/routes.py` -- sees the pattern for endpoints

**Agent implements the feature** (0:45-2:30)
- Adds a `Tag` model following the existing model pattern
- Adds a Pydantic schema for tags
- Adds `POST /api/experiments/{id}/tags` following the route pattern
- Updates `experiments/templates/detail.html` to display tags
- Everything is co-located: model, schema, route, template all in `experiments/`

**Agent runs verification** (2:30-3:30)
- Runs `pytest` -- existing tests still pass
- Runs `ruff check .` -- no lint errors
- May add new tests following the pattern in `test_experiments.py`

**Narration points:**
- "The agent went straight to `experiments/` -- the folder name told it exactly where to look"
- "It's following the existing schema pattern. Typed enums, Pydantic validation."
- "Notice it found the template right next to the route. Co-location."
- "Tests pass. Lint passes. The agent verified its own work."

---

## Timing

| Phase | Expected Time |
|-------|--------------|
| Agent reads rules + explores | 0:00-0:30 (B) / 0:00-2:00 (A) |
| Agent implements feature | 0:30-2:30 (B) / 2:00-4:00 (A) |
| Agent verifies | 2:30-3:30 (B) / 4:00-5:00 (A) |
| **Total** | **~3 min (B) / ~5 min (A)** |

Expect Version B to finish while Version A is still figuring out the file structure.

---

## Fallback Plan

If the live demo fails (network issues, agent misbehaves, etc.):

1. **First option:** Say "Let me show you what this looked like when I ran it earlier" and switch to a pre-recorded screencast of the race.

2. **Second option:** Walk through the two codebases side by side manually:
   - Show `A/app.py` (500+ lines) vs `B/experiments/routes.py` (~80 lines)
   - Show `A/CLAUDE.md` (300+ lines of noise) vs `B/CLAUDE.md` (50 lines of signal)
   - Show `A/tests/test_app.py` (`assert 1+1==2`) vs `B/tests/test_experiments.py` (real tests)
   - Ask: "If you were an agent, which codebase would you rather work in?"

3. **Key point either way:** The difference isn't the agent. It's the codebase. Same model, same prompt, wildly different outcomes.

---

## Pre-Race Checklist

- [ ] Both apps start without errors
- [ ] B's tests pass (`pytest` in `B/`)
- [ ] Both terminals visible on projector
- [ ] Font size large enough for back of room
- [ ] Pre-recorded backup video ready
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
| Time to complete | 3-5 min | 1.5-3 min |
| Tool calls | 30-50 | 15-25 |
| Files read before first edit | 5-8 | 2-4 |
| Test outcome | No meaningful tests | All tests pass |
| Correct implementation | Maybe | Very likely |

### Alternative Race Prompts

1. **Tagging** (default): "Add experiment tagging with POST /api/experiments/{id}/tags..."
2. **Bug fix**: "Users report that creating an experiment with status 'completed' doesn't work correctly. Find and fix the bug. Run tests to verify."
3. **New metric**: "Add a new metric field 'f1_score' (float, 0-1) to runs. Update the model, API, and detail page to support it."
