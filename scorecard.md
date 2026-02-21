# AI-Readiness Scorecard

Score your codebase 0-3 on each dimension. Max score: 9.

---

## Dimension 1: Rules File

| Score | Criteria |
|-------|----------|
| 0 | No CLAUDE.md, AGENTS.md, or equivalent rules file |
| 1 | Exists but bloated (>200 lines), vague, or missing runnable commands |
| 2 | Under 150 lines. Has: exact build/test/lint commands, repo map, definition of done |
| 3 | All of 2, plus: folder-level rule files, coding conventions with examples, "do not" list |

### Audit Questions

- Does your rules file exist?
- Can you copy-paste the test command from it and run it right now?
- Is it under 150 lines?
- Does it have a repo map showing where key things live?
- Does it define "done" (what must be true before the agent stops)?

---

## Dimension 2: File Organization

| Score | Criteria |
|-------|----------|
| 0 | God files >500 LOC, cryptic names, scattered structure, silent errors |
| 1 | Some modularization. Inconsistent naming. Errors exist but aren't actionable. |
| 2 | Max 300 LOC per file. Descriptive names. Co-located by feature. Error messages say what went wrong. CLI has --help. |
| 3 | All of 2, plus: header comments on every file. Errors include resolution steps. Tools mirror well-known interfaces. |

### Audit Questions

- What's your longest file? (Check: `find . -name "*.py" | xargs wc -l | sort -rn | head -5`)
- Can an agent find the right file by name alone?
- Do your error messages tell the agent what to do next?
- Is related code co-located (feature-grouped) or scattered by type?
- Do files have header comments explaining what they do and why?

---

## Dimension 3: Test & Verification

| Score | Criteria |
|-------|----------|
| 0 | No tests, or tests the agent can modify/delete |
| 1 | Tests exist but no clear "run tests" command, or agent can rewrite tests to make bugs pass |
| 2 | Fixed test suite agent runs but can't touch. Clear test commands. Lint as guardrail. |
| 3 | All of 2, plus: multi-layered verification (lint + type check + unit + integration). CI on agent PRs. |

### Audit Questions

- Can the agent run your tests in one command?
- Could the agent delete a test to make a bug pass? (Is your test suite protected?)
- How many verification layers does the agent hit? (lint, types, unit, integration, e2e)
- Do your tests cover requirements, not just lines of code?

---

## Quick Interpretation

| Score | What It Means | Next Step |
|-------|--------------|-----------|
| 0-3 | Codebase is fighting the agent. | Start with a rules file and splitting your largest files. |
| 4-6 | Basics are there. | Next unlock is test systems and codified verification. |
| 7-9 | Ahead of most teams. | Push on multi-layered verification and self-documenting tooling. |

---

## Your Score

| Dimension | Score (0-3) | Notes |
|-----------|-------------|-------|
| Rules File | | |
| File Organization | | |
| Test & Verification | | |
| **Total** | **/9** | |

**My #1 quick win to fix Monday:**

_____________________________________________
