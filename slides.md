# Optimizing Codebases for Agents — Slide Deck

**Coding Agents: AI Driven Dev Conference**
March 3, 2026 | Computer History Museum, Mountain View, CA
Shrivu Shankar, VP AI, Abnormal Security

---

## Slide 1: Title (01/13)

# Optimizing Codebases for Agents

**Shrivu Shankar** / VP AI, Abnormal Security

*Your agent isn't broken. Your codebase is.*

> **Speaker Notes:** Start at 0:00. Open cold: "I use Claude Code. A lot. At home for personal projects, at work leading an AI team that ships production agents. And the single biggest unlock I've found for getting more out of coding agents has nothing to do with prompting. It has everything to do with how my codebase is organized." Pause. "Your agent isn't broken. Your codebase is. That's the thesis. In the next hour, you're going to audit your own repo and start fixing it." Transition: "Let me show you what I mean."

---

## Slide 2: The Glass Ceiling (02/13)

### Agents crush greenfield. They hit a wall on real codebases.

- You write more docs, bigger CLAUDE.mds, longer prompts
- The trap: bloated rules files and longer prompts that drown the agent in noise
- **The reframe: redesign the codebase for the agent**

> **Speaker Notes:** Start at ~0:30. Spend about 60 seconds here. "By now, nearly every one of you has seen an agent write a perfect unit test or churn out flawless boilerplate on a brand new project. But ask it to do something real on your actual codebase, and there's this frustrating glass ceiling. The agent gets lost, misses context, fails to navigate your code." Pause. "Our first instinct is always the same: write more documentation. Bigger CLAUDE.mds. Longer rules files. This is a trap. The unlock is the opposite: redesign your software with the agent as the primary user." Transition: "I'm going to show you exactly what this looks like. Live."

---

## Slide 3: The Agent Race (03/13)

### [LIVE DEMO]

Two terminals. Same prompt. Same model. Two repos. **Watch what happens.**

```
# The prompt (identical for both agents)
"Add experiment tagging. New endpoint
POST /api/experiments/{id}/tags and
show tags on the detail page.
Follow existing patterns. Run tests."
```

> **Speaker Notes:** Start at ~1:30. This is the centerpiece. Budget 3-4 minutes for the race itself. Two terminal windows side by side. Left: `cd A/` (messy). Right: `cd B/` (optimized). Same prompt in both. Narrate: "On the left, realistic codebase. God file, cryptic folders, no useful tests. On the right, same app, same functionality, organized for the agent." Point out: left agent reading 500-line god file, templates in `stuff/`, test that only tests 1+1=2. Right agent reads 50-line CLAUDE.md, navigates to `experiments/`, follows routes.py/models.py/schemas.py pattern. **Fallback:** If agent hangs: "Let me show you what this looked like when I ran it this morning" and switch to pre-recorded video. Let the difference land visually before narrating.

---

## Slide 4: What Just Happened? (04/13)

### Version A (the mess)

- Read a **240-line CLAUDE.md** full of meeting notes and project history; got zero signal
- Searched for "tags" and found **5 conflicting artifacts**: feature flag, broken helpers, abandoned template, duplicate validators
- Couldn't find templates (they're in `stuff/`)
- Only test was `assert 1 + 1 == 2`; no real verification

### Version B (optimized)

- Read **50-line CLAUDE.md**, got a repo map in 10 seconds
- Found `tags/` folder with model, schema, and a GET route already built
- Saw a `TODO` comment telling it exactly what POST endpoint to add
- Added the route (~20 lines), ran `pytest`, **tests passed on the first try**

> **Speaker Notes:** Start at ~5:00. Spend about 3 minutes here. Walk through what happened in each terminal, tying failures to specific structural problems. "On the left, the agent spent its first 30 seconds reading a 240-line CLAUDE.md full of meeting notes and changelog entries. Zero useful signal. Then it searched for 'tags' and found five different files with conflicting ideas about how tags should work: a feature flag set to false, broken helper functions using raw SQL against a table that doesn't exist, an abandoned HTML template, and a validation function expecting different field names than what app.py uses. The agent had to reconcile five different stories. And the only test was 'assert 1+1 equals 2', so even after it cobbled something together, nothing caught the bugs." Then flip: "On the right, the agent opened CLAUDE.md, got a repo map, saw a tags/ directory in the map, went straight there. Found a model, a schema, and a GET route already built. Found a TODO comment telling it exactly what POST endpoint to add and which file to reference for the pattern. It added 20 lines of code, ran pytest, and got green." Pause. "Same model. Same prompt. Different codebase. That's the whole talk." Transition: "So what are the actual levers? There are three."

---

## Slide 5: Three Dimensions of Agent-Readiness (05/13)

1. **Rules File & Agent Config** — Does the agent know the rules?
2. **File Organization** — Can the agent find things?
3. **Test & Verification** — Can the agent verify its work?

Score: **0-3 per dimension. Max 9.**

> **Speaker Notes:** Start at ~8:00. About 60 seconds here. Keep it quick. "Three dimensions. Three questions. Does the agent know the rules? Can it find things? Can it verify its own work? Each scored 0-3, max 9. Most teams are around 2-4. We'll go through each one, then you score your own repo." Transition: "Let's start with the rules file."

---

## Slide 6: Dimension 1 — Rules File & Agent Config (06/13)

### The 200-line rule

**Include:**
- Exact commands: `pytest`, `npm run lint`, `python manage.py check`
- Repo map: where entrypoints, configs, tests live
- Definition of done: what must be true before agent stops
- Hard boundaries: "do not touch tests", "ask before adding deps"

**Exclude:**
- Meeting notes, changelogs, or architecture docs
- General coding philosophy
- Anything that belongs in a linter config or hook

### Beyond CLAUDE.md: the `.claude/` directory

- **`settings.json`**: Tool permissions (allow, deny), environment config
- **Hooks**: Auto-lint after edits (PostToolUse), block dangerous commands (PreToolUse)
- **`rules/`** or folder-level CLAUDE.md: Progressive disclosure for monorepos
- **`skills/`**: Repeatable workflows the agent can auto-discover

**CLAUDE.md is advisory. Hooks are enforcement. Use both.**

> **Speaker Notes:** Start at ~9:00. About 90 seconds. "The rules file is the single highest-leverage thing you can add. Most common mistake: making it too long. Past 150 lines, agent loses signal. Think of it as a cheat sheet for a new hire on day one, not the employee handbook." Reference demo: "Version B had 50 lines: test command, repo map, definition of done. That was enough." Then the level-up: "But CLAUDE.md is just the starting point. Modern Claude Code has a whole .claude directory. Settings.json for permissions. Hooks for automation: auto-run the linter after every edit, block dangerous commands. Skills for repeatable workflows. Folder-level rules for progressive disclosure. The key insight: CLAUDE.md is advisory; the agent can choose to ignore it. Hooks are enforcement; the agent can't bypass them." Transition: "But even the best rules file can't save you if the agent can't find anything."

---

## Slide 7: Dimension 2 — File Organization (07/13)

### Five patterns that make codebases agent-readable

1. **Every output is a prompt** — errors and CLI output guide the agent's next step
2. **Self-documenting code** — header comments with purpose + related files, `--help` flags, not external wikis
3. **Predictable interfaces** — typed configs, enums over strings, conventions the agent already knows
4. **Greppable names** — descriptive file and function names are the agent's search index
5. **Workflows, not concepts** — co-locate by feature, not by layer

**Single-concern files** (split when concerns mix, not at an arbitrary line count). **Descriptive names.** Feature-grouped folders.

> **Speaker Notes:** Start at ~10:30. About 2 minutes. Densest slide, don't read every bullet. Ground in demo: "stuff/templates vs experiments/templates = pattern 5: co-locate by feature. Agent got silent Success! and didn't know what to do next = pattern 1: every output should prompt the next action." Quick hits: "Single-concern files. The question isn't 'is this file over 300 lines?' The question is 'does this file mix concerns?' A 600-line test file for one module is fine. A 300-line file that does routing, database queries, and HTML rendering is a problem." Transition: "Structure gets the agent to the right place. But how does it know if it did the right thing?"

---

## Slide 8: Dimension 3 — Test & Verification (08/13)

### The confidence spectrum

```
Linters → Types → Unit Tests → Integration → E2E → Visual
   ←  fast, cheap, narrow  |  slow, expensive, comprehensive  →
```

### Three principles

1. **Baseline tests are immutable.** Protect existing tests from agent modification.
2. **Agents write new tests, test-first.** TDD for agents: write the failing test, then implement.
3. **Hooks close the feedback loop.** PostToolUse hooks auto-run lint, types, and tests after every edit.

```
Agent edits file → PostToolUse fires → lint + type-check + pytest →
    errors fed back → agent self-corrects → repeat
```

> **Speaker Notes:** Start at ~12:30. About 90 seconds. "This is the dimension most teams score lowest on. Not because they don't have tests, but because the agent can rewrite them." Demo story: "Version A's test was 1+1=2. Agent could write anything, get green, declare victory. That's theater, not verification." New framing: "Your existing test suite, the one that validates known-good behavior, that's immutable. The agent must not touch it. But the agent absolutely should write NEW tests for new features. Ideally test-first. Tests are deterministic acceptance criteria for a non-deterministic worker." Then hooks: "The real level-up is hooks. PostToolUse hook that auto-runs lint and pytest after every file edit. Immediate feedback, not a pile-up of failures at the end." Transition: "Before we move on, let me hit a few patterns to actively avoid."

---

## Slide 9: The Anti-Patterns (09/13)

| Anti-Pattern | What Happens | The Fix |
|---|---|---|
| **Test-gaming** | Agent modifies/deletes existing tests to make broken code pass | Protect baseline tests with hooks |
| **Implementation-mirroring tests** | Agent writes tests that verify its own code line-by-line | Require behavior-based tests |
| **Rule-gaming** | Agent modifies lint rules instead of fixing code | Lock config files |
| **No feedback loop** | Agent codes for extended sessions without running tests | PostToolUse hooks auto-run verification |
| **Bloated context** | 500-line CLAUDE.md drowns signal | 200-line limit, use `.claude/rules/` for progressive disclosure |
| **Advisory-only rules** | Agent ignores "do not modify tests" in CLAUDE.md | Enforce with hooks and `settings.json` deny rules |

> **Speaker Notes:** Start at ~14:00. About 60 seconds. Quick hits: "Six things teams get burned by. Test-gaming: agent modifies existing tests to make broken code pass. One developer caught their agent hardcoding golden test pairs. Implementation-mirroring: test is a line-by-line copy of the implementation; if the code is wrong, the test is wrong too. Rule-gaming: changes your ESLint config instead of fixing the code. No feedback loop: codes for 5 minutes without running anything. Bloated context: 500-line rules file. Advisory-only rules: you wrote 'do not modify tests' in CLAUDE.md, but the agent ignored it because CLAUDE.md is advisory. Hooks are enforcement." Transition: "Alright. That's the framework. Now it's your turn."

---

## Slide 10: The Audit Sprint (10/13)

### Score your codebase. 20 minutes. Go.

**Instructions:**

1. Open `scorecard.md` in the workshop repo
2. Score your repo **0-3** on each dimension: Rules File & Agent Config, File Organization, Test & Verification
3. Write down your **#1 quick win**

*No repo? Clone Version A and audit that.*

`github.com/sshh12/coding-agents-workshop`

`[QR CODE]` `[20:00 COUNTDOWN TIMER]`

> **Speaker Notes:** Start at ~15:00. About 60 seconds for instructions, then 20 minutes of work. "Open the scorecard. Auditing your own code if you brought a repo, Version A if you didn't. Score 0-3 on each dimension. Be honest, this is for you. Write down the one thing you'd fix first." Logistics: "20 minutes. I'm walking the room. Flag me if stuck." Walk immediately. Note which dimensions score lowest. Help anyone without a repo clone Version A. Check first 2-3 min that people understand rubric. Questions while walking: "What did you score on rules file?" "What's your longest file?" "Does your repo have a test command?" At 2-min warning: "Two minutes left. Finish scores and write down your #1 quick win."

---

## Slide 11: Pair and Fix (11/13)

### Turn to the person next to you.

1. **Compare scores** — Where did you agree? Diverge?
2. **Pick one quick win** — The single highest-impact fix
3. **Start implementing** — Actually change the code

*If you audited Version A, pair with someone who brought their own repo.*

`[07:00 COUNTDOWN TIMER]`

> **Speaker Notes:** Start at ~35:00. About 60 seconds for instructions, then 7 minutes of pair work. "Turn to the person next to you. If you're on the end, turn around. If you audited Version A and your neighbor brought their own repo, great, you're fresh eyes on unfamiliar code." "Compare scores. Find where you agree and disagree. Pick one quick win and start fixing it. Write the CLAUDE.md. Split the god file. Add the lint rule. Whatever your #1 was, start now." "7 minutes. I'm walking again." Rotate between pairs. Questions: "What did you pick?" "What are you stuck on?" "Did your partner spot something you missed?" Ready for micro-demos at laptops. Common: "How to write CLAUDE.md?" (show B's). "How to split this file?" (feature-grouped pattern). At 1-min mark: "One minute. Wrap up. I'm pulling up patterns I saw."

---

## Slide 12: Pattern Debrief (12/13)

### What I saw walking the room

*[Filled in live from the audit and pair sprints]*

1. _(most common pattern observed)_
2. _(second most common)_
3. _(third most common)_

*[Live-demo the fix on Version A]*

> **Speaker Notes:** Start at ~42:00. Budget 10 minutes through ~52:00. Second live coding moment. "I talked to about 30 of you. Here's what I saw." Name 2-3 most common issues. Live-demo the fix on Version A. If top issue is "no rules file," write a CLAUDE.md live: test command, repo map, definition of done, 20-30 lines. If god files, open 500-line app.py and show how to split into experiments/routes.py, models.py, etc. 2-3 min per fix. **Fallback:** Narrate verbally and show Version B code as the "after" state.

---

## Slide 13: Takeaway (13/13)

### Volunteers. 2 minutes each.

**What's the one thing you're fixing next week?**

---

### Resources

- **Workshop repo:** `github.com/sshh12/coding-agents-workshop`
- **Scorecard:** `scorecard.md` in the repo
- **Blog:** `blog.sshh.io`

> **Speaker Notes:** Start at ~52:00. Budget 6-8 minutes for lightning shares plus close. "Volunteers. 2 minutes each. What did you score, what did you find, what's the one thing you're fixing next week?" Point to people from your walk. If nobody volunteers: "I talked to someone in the back who found a 1,200-line god file. Want to tell us about that?" After shares, close fast: "Here's the repo. Scorecard is in there. Both demo app versions. My blog goes deeper on all of this." One-sentence close: "Your agent isn't broken. Your codebase is. Go fix it." Don't linger. Thank audience, leave QR up, step away.
