# AI-Readiness Scorecard

Score your codebase 0-3 on each dimension. Max score: 9.

---

## Dimension 1: Rules File & Agent Config

| Score | Criteria |
|-------|----------|
| 0 | No CLAUDE.md or equivalent rules file. No `.claude/` directory. |
| 1 | Rules file exists but bloated (>300 lines without modular splits), vague ("write clean code"), or missing runnable commands. No `.claude/` configuration. |
| 2 | CLAUDE.md under 200 lines with: exact build/test/lint commands, repo map, definition of done. Basic `.claude/settings.json` with tool permissions. |
| 3 | All of 2, plus at least two of: folder-level CLAUDE.md or `.claude/rules/` for progressive disclosure; hooks for automated guardrails (auto-lint, safety gates); custom skills or commands for repeatable workflows. "Do not" list with enforced boundaries (hooks, not just instructions). |

### Audit Questions

- Does your rules file exist? Can you copy-paste the test command and run it right now?
- Is your root CLAUDE.md under 200 lines? (Or does it use `.claude/rules/` to stay modular?)
- Does it have a repo map showing where key things live?
- Does it define "done" (what must be true before the agent stops)?
- Do you have `.claude/settings.json` with tool permissions?
- Do you have any hooks? (auto-lint on edit, safety gates on dangerous commands)
- Are there folder-level rules for different parts of the codebase?

---

## Dimension 2: File Organization

| Score | Criteria |
|-------|----------|
| 0 | **Agent gets lost.** Mixed-concern god files (routing + DB + logic + rendering in one file). Cryptic or abbreviated names (`er.py`, `utils2.py`, `stuff/`). No consistent structure. Errors are silent or swallowed. |
| 1 | **Agent finds things eventually.** Some modularization but inconsistent. Naming is mostly descriptive but has outliers. Code organized by layer (`models/`, `views/`, `utils/`) rather than feature. Errors exist but don't guide next steps. |
| 2 | **Agent navigates confidently.** Files are single-concern (one module, one feature slice). Names are descriptive and greppable (`experiment_routes.py`). Co-located by feature. Error messages say what went wrong and suggest what to do. |
| 3 | **Agent reasons about structure.** All of 2, plus: files have header comments with purpose and related files. Typed interfaces (enums, schemas) encode valid states. Error messages include resolution steps. Folder structure mirrors the domain. |

### Audit Questions

- What's your longest file? Is it long because it does one thing deeply, or because it mixes concerns?
- Pick a random feature. How many directories do you need to touch to modify it end-to-end?
- Can an agent find the right file by name alone, without reading any code?
- Do your error messages tell the agent what to do next, or just what went wrong?
- Do your files have header comments that explain purpose and link to related files?

---

## Dimension 3: Test & Verification

| Score | Criteria |
|-------|----------|
| 0 | No tests, or tests the agent can freely modify/delete. No lint or type checking configured. |
| 1 | Tests exist and agent can run them, but no protection against test modification. Test commands may not be documented. No distinction between baseline and new tests. |
| 2 | **Baseline test suite is protected** (agent cannot modify existing tests). Agent can write NEW test files for new features. Clear test commands in rules file. Lint/type-check configured as guardrails. |
| 3 | All of 2, plus: PostToolUse hooks auto-run verification after every edit (lint + types + targeted tests). Multi-layer pipeline: format, lint, type-check, unit, integration. CI on agent PRs with stricter gates. |

### Audit Questions

- Can the agent run your tests in one command?
- Is your baseline test suite protected? Could the agent delete a test to make a bug pass?
- Can the agent write NEW tests for new features? (It should.)
- How many verification layers does the agent hit? (lint, types, unit, integration, e2e)
- Do you have hooks that auto-run verification after every file edit?

---

## Quick Interpretation

| Score | What It Means | Next Step |
|-------|--------------|-----------|
| 0-3 | Codebase is fighting the agent. | Start with a rules file and splitting your largest files. |
| 4-6 | Basics are there. | Next unlock is test protection, hooks, and codified verification. |
| 7-9 | Ahead of most teams. | Push on multi-layered verification with hooks and self-documenting tooling. |

---

## Your Score

| Dimension | Score (0-3) | Notes |
|-----------|-------------|-------|
| Rules File & Agent Config | | |
| File Organization | | |
| Test & Verification | | |
| **Total** | **/9** | |

**My #1 quick win to fix Monday:**

_____________________________________________
