# Optimizing Codebases for Agents — Slide Deck

**Coding Agents: AI Driven Dev Conference**
March 3, 2026 | Computer History Museum, Mountain View, CA
Shrivu Shankar, VP AI, Abnormal Security

---

## Slide 1: Title

# Optimizing Codebases for Agents

**Shrivu Shankar**
VP AI, Abnormal Security

*Your agent isn't broken. Your codebase is.*

> **Speaker Notes:** Start at 0:00. You're on after the break, so the room is resettled but energized. Don't open with pleasantries or bio. Walk up, title slide is already on screen, and open cold: "I use Claude Code. A lot. At home for personal projects, at work leading an AI team that ships production agents. And the single biggest unlock I've found for getting more out of coding agents has nothing to do with prompting. It has everything to do with how my codebase is organized." Pause. "Your agent isn't broken. Your codebase is. That's the thesis. And in the next hour, you're going to audit your own repo and start fixing it." Transition: "Let me show you what I mean." Click to next slide. (~30 seconds)

---

## Slide 2: The Glass Ceiling

### Agents crush greenfield. They hit a wall on real codebases.

- The instinct: write more docs, bigger CLAUDE.mds, longer prompts
- The trap: bloated rules files and longer prompts that drown the agent in noise
- **The reframe: redesign the codebase for the agent**

> **Speaker Notes:** Start at ~0:30. Spend about 60 seconds here. "By now, nearly every one of you has seen an agent write a perfect unit test or churn out flawless boilerplate on a brand new project. But ask it to do something real on your actual codebase, and there's this frustrating glass ceiling. The agent gets lost, misses context, fails to navigate your code." Pause. "Our first instinct is always the same: write more documentation. Bigger CLAUDE.mds. Longer rules files. This is a trap. It expects the AI to learn our messy, human-centric systems. The unlock is the opposite: redesign your software with the agent as the primary user." This sets up the demo. Transition: "I'm going to show you exactly what this looks like. Live." Click to next slide.

---

## Slide 3: The Agent Race

### [LIVE DEMO]

Two terminals. Same prompt. Same model. Two repos.

**Watch what happens.**

```
Prompt: "Add a new feature: experiment tagging. Users should be
able to add tags to experiments via a new POST /api/experiments/{id}/tags
endpoint and see tags displayed on the experiment detail page.
Follow the existing patterns. Run the tests to verify."
```

> **Speaker Notes:** Start at ~1:30. This is the centerpiece. Budget 3-4 minutes for the race itself. Have two terminal windows open side by side before you start. Left terminal: `cd A/` (the messy repo). Right terminal: `cd B/` (the optimized repo). Both running Claude Code (or your agent of choice). Copy the exact same prompt into both terminals at the same time. Narrate as you go: "On the left, this is a realistic codebase. One god file, cryptic folder names, no useful tests. On the right, same exact app, same functionality, but organized for the agent." While the agents run, point out key moments: the left agent reading the 500-line god file, trying to find templates in a folder called `stuff/`, finding a test file that only tests 1+1==2. The right agent reading a 50-line CLAUDE.md, navigating straight to `experiments/`, following the existing pattern of routes.py / models.py / schemas.py. **Fallback:** If either agent hangs or does something unexpected, say: "Let me show you what this looked like when I ran it this morning" and switch to the pre-recorded video. Keep the video under 3 minutes. Either way, let the audience see the contrast play out before you narrate it on the next slide. Do NOT skip to the explanation too early; let the difference land visually first.

---

## Slide 4: What Just Happened?

### Version A (the mess)

- Agent read a **240-line CLAUDE.md** full of meeting notes and project history; got zero signal
- Searched for "tags" and found **5 conflicting artifacts**: a feature flag set to `False`, broken helper functions, an abandoned template, duplicate validators with different field names
- Couldn't find templates (they're in `stuff/`)
- Only test was `assert 1 + 1 == 2`; no real verification

### Version B (optimized)

- Agent read **50-line CLAUDE.md**, got a repo map in 10 seconds
- Found `tags/` folder with model, schema, and a GET route already built
- Saw a `TODO` comment telling it exactly what POST endpoint to add
- Added the route (~20 lines), ran `pytest`, **tests passed on the first try**

> **Speaker Notes:** Start at ~5:00. Spend about 3 minutes here. Walk through what happened in each terminal, tying failures to specific structural problems. "On the left, the agent spent its first 30 seconds reading a 240-line CLAUDE.md full of meeting notes and changelog entries. Zero useful signal. Then it searched for 'tags' and found five different files with conflicting ideas about how tags should work: a feature flag set to false, broken helper functions using raw SQL against a table that doesn't exist, an abandoned HTML template, and a validation function expecting different field names than what app.py uses. The agent had to reconcile five different stories. And the only test was 'assert 1+1 equals 2', so even after it cobbled something together, nothing caught the bugs." Then flip: "On the right, the agent opened CLAUDE.md, got a repo map, saw a tags/ directory in the map, went straight there. Found a model, a schema, and a GET route already built. Found a TODO comment telling it exactly what POST endpoint to add and which file to reference for the pattern. It added 20 lines of code, ran pytest, and got green." Pause. "Same model. Same prompt. Different codebase. That's the whole talk." Transition: "So what are the actual levers? There are three."

---

## Slide 5: Three Dimensions of Agent-Readiness

```
                    +-----------------+
                    |  RULES FILE &   |  Does the agent know the rules?
                    |  AGENT CONFIG   |
                    +-----------------+
                            |
                    +-----------------+
                    |  FILE           |  Can the agent find things?
                    |  ORGANIZATION   |
                    +-----------------+
                            |
                    +-----------------+
                    |  TEST &         |  Can the agent verify its work?
                    |  VERIFICATION   |
                    +-----------------+
```

Score: **0-3 per dimension. Max 9.**

> **Speaker Notes:** Start at ~8:00. About 60 seconds here. This is the overview slide; keep it quick. "Three dimensions. Three questions. Does the agent know the rules? Can it find things? And can it verify its own work? Each one is scored 0-3. A 9 means your codebase is ready. Most teams I talk to are somewhere around 2-4. We're going to go through each one, then you're going to score your own repo." Transition: "Let's start with the rules file."

---

## Slide 6: Dimension 1 — Rules File & Agent Config

### The 200-line rule (for your root CLAUDE.md)

**What to include:**
- Exact commands: `pytest`, `npm run lint`, `python manage.py check`
- Repo map: where entrypoints, configs, and tests live
- Definition of done: what must be true before the agent stops
- 1-2 code examples: a good pattern and a bad pattern
- Hard boundaries: "do not touch tests/," "ask before adding deps"

**What NOT to include:**
- Your entire architecture doc, meeting notes, or changelog
- General coding philosophy ("write clean code")
- Anything that belongs in a linter config or hook

### Beyond CLAUDE.md: the `.claude/` directory

- **`settings.json`**: Tool permissions (allow/deny), environment config
- **Hooks**: Auto-lint after edits (PostToolUse), block dangerous commands (PreToolUse)
- **`rules/`** or folder-level CLAUDE.md: Progressive disclosure for monorepos
- **`skills/`**: Repeatable workflows the agent can auto-discover

**The key insight:** CLAUDE.md is advisory. Hooks are enforcement. Use both.

> **Speaker Notes:** Start at ~9:00. About 90 seconds. "The rules file is the single highest-leverage thing you can add to any repo. And the most common mistake is making it too long. Boris Cherny, who created Claude Code at Anthropic, has his team's CLAUDE.md at about 2,500 tokens, maybe 60-80 lines. Past 200 lines, you're losing signal in the noise." Reference the demo: "In Version B, the CLAUDE.md was 50 lines. It had the test command, a repo map, and a definition of done. That's it. And that was enough for the agent to navigate the entire codebase." Then the level-up: "But CLAUDE.md is just the starting point. Modern Claude Code has a whole .claude directory. Settings.json for permissions: what tools the agent can and can't use. Hooks for automation: auto-run the linter after every file edit, block dangerous commands before they execute. Skills for repeatable workflows. And folder-level rules for progressive disclosure in monorepos. The key insight: CLAUDE.md is advisory; the agent can choose to ignore it. Hooks are enforcement; the agent can't bypass them." Transition: "But even the best rules file can't save you if the agent can't find anything."

---

## Slide 7: Dimension 2 — File Organization

### Five patterns that make codebases agent-readable

1. **Every output is a prompt** — errors and CLI output guide the agent's next step
2. **Self-documenting code** — header comments with purpose + related files, `--help` flags, not external wikis
3. **Predictable interfaces** — typed configs, enums over strings, conventions the agent already knows (REST, pytest, pandas)
4. **Greppable names** — descriptive file and function names are the agent's search index
5. **Workflows, not concepts** — co-locate by feature (`/experiments/`), not by layer (`/models/`)

### The practical rules

- **Single-concern files** (split when concerns mix, not at an arbitrary line count)
- **Descriptive names**: `experiment_routes.py`, not `er.py`
- **Feature-grouped folders**: everything for one feature in one place

> **Speaker Notes:** Start at ~10:30. About 2 minutes. This is the densest slide, so don't read every bullet. Ground each pattern in the demo: "You saw the difference between 'stuff/templates' and 'experiments/templates'. That's pattern 5: co-locate by feature, not by concept. You saw the agent on the left get a silent 'Success!' from the CLI and not know what to do next. Pattern 1 says every output should be a prompt for the next action. And pattern 4, greppable names: when the agent searched for 'tags' in Version A, it found five files with conflicting ideas. In Version B, it found a folder literally called tags/. The agent uses grep and find to navigate; your file names are its search index." Hit the practical rules: "Single-concern files. The question isn't 'is this file over 300 lines?' The question is 'does this file mix concerns?' A 600-line test file for one module is fine. A 300-line file that does routing, database queries, and HTML rendering is a problem." Transition: "Structure gets the agent to the right place. But how does it know if it did the right thing?"

---

## Slide 8: Dimension 3 — Test & Verification

### The confidence spectrum

```
Linters → Types → Unit Tests → Integration → E2E → Visual
   ←  fast, cheap, narrow  |  slow, expensive, comprehensive  →
```

### Three principles

1. **Baseline tests are immutable.** Protect existing tests from agent modification. These are your golden suite that validates known-good behavior.
2. **Agents write new tests, test-first.** The agent writes a failing test that crystallizes "what correct means" before implementing. TDD for agents.
3. **Hooks close the feedback loop.** Don't rely on the agent to "remember" to test. PostToolUse hooks auto-run lint, types, and tests after every edit.

### The hook feedback loop

```
Agent edits file → PostToolUse fires → lint + type-check + pytest →
    errors fed back → agent self-corrects → repeat
```

> **Speaker Notes:** Start at ~12:30. About 90 seconds. "This is the dimension most teams score lowest on. And the advice I used to give was wrong. I used to say: 'the agent runs tests, the agent does NOT write tests.' That's too simplistic." New framing: "Here's the nuanced version. Your existing test suite, the one that validates known-good behavior, that's immutable. The agent must not touch it. If the agent can delete a test to make a bug pass, your verification is broken. But the agent absolutely should write NEW tests for new features. Ideally test-first: write the failing test, then implement. Tests are deterministic acceptance criteria for a non-deterministic worker." Tell the demo story: "In Version B, the test suite already had tests for the tagging endpoint. The agent's job was to make them pass. It couldn't modify them. That's the pattern." Then hooks: "The real level-up is hooks. Instead of relying on the agent to remember to run tests, set up a PostToolUse hook that auto-runs lint and pytest after every file edit. The agent gets immediate feedback, not a pile-up of failures at the end." Transition: "Before we move on, let me hit a few patterns you should actively avoid."

---

## Slide 9: The Anti-Patterns

| Anti-Pattern | What Happens | The Fix |
|---|---|---|
| **Test-gaming** | Agent modifies or deletes existing tests to make broken code pass | Protect baseline tests with hooks (PreToolUse blocks edits to `tests/`) |
| **Implementation-mirroring tests** | Agent writes tests that verify its own code line-by-line, not the actual requirement | Require behavior-based tests; tests describe WHAT, not HOW |
| **Rule-gaming** | Agent modifies lint rules instead of fixing code | Lock config files from agent writes |
| **No feedback loop** | Agent codes for an extended session without running tests; failures compound | PostToolUse hooks auto-run verification after every edit |
| **Bloated context** | 500-line CLAUDE.md drowns signal in noise | 200-line limit; use `.claude/rules/` for progressive disclosure |
| **Advisory-only rules** | Agent ignores "do not modify tests" in CLAUDE.md | Enforce with hooks (PreToolUse blocks) and `settings.json` deny rules |

> **Speaker Notes:** Start at ~14:00. About 60 seconds. Go through the table quickly. "Six things I see teams get burned by. Test-gaming: the agent modifies your existing tests to make broken code pass. One developer caught their agent hardcoding golden test pairs into the algorithm. Implementation-mirroring: the agent writes a test that's a line-by-line copy of the implementation; if the code is wrong, the test is wrong too. Rule-gaming: the agent changes your ESLint config instead of fixing the code. No feedback loop: the agent codes for 5 minutes without running anything, and by the time it tests, the failures are too deep to untangle. Bloated context: a 500-line rules file where the agent can't find the test command. And advisory-only rules: you wrote 'do not modify tests' in CLAUDE.md, but the agent ignored it because CLAUDE.md is advisory. Hooks are enforcement." Transition: "Alright. That's the framework. Now it's your turn."

---

## Slide 10: Your Turn — The Audit Sprint

### Score your codebase. 15 minutes. Go.

**Instructions:**

1. Open `scorecard.md` in the workshop repo (QR code below)
2. Score your repo **0-3** on each dimension: Rules File & Agent Config, File Organization, Test & Verification
3. Write down your **#1 quick win** at the bottom

**No repo? Clone Version A and audit that.**

```bash
git clone https://github.com/sshh12/coding-agents-workshop.git
cd coding-agents-workshop/A
```

`[QR CODE]`

> **Speaker Notes:** Start at ~15:00. About 60 seconds for instructions, then 15 minutes of silent work. Put the QR code up and leave it. "Here's what I need from you. Open the scorecard. If you brought a repo, you're auditing your own code. If you didn't, clone Version A and audit that. Score yourself 0-3 on each dimension. Be honest; this is for you, not for me. Write down the single thing you'd fix first, the #1 quick win." Logistics: "You've got 15 minutes. I'm going to walk the room. If you're stuck, flag me down." Click to the timer slide. Walk the room immediately. Note which dimensions people score lowest on and what patterns come up repeatedly; you'll need this for Slide 14. Help anyone who didn't bring a repo get Version A cloned. For the first 2-3 minutes, check that people actually have the scorecard open and understand the rubric; course-correct early.

---

## Slide 11: Audit Sprint

# 15:00

*[On-screen countdown timer]*

> **Speaker Notes:** Timer runs from 15:00 to 30:00. Walk the room the entire time. Don't sit at the front. Make yourself available but don't hover. Good questions to ask people as you walk: "What did you score on rules file?" "What's your longest file?" "Does your repo have a test command?" "What's your biggest surprise so far?" Mental checklist while walking: (1) How many people scored 0 on rules file? (2) What's the most common file organization issue? (3) Are people finding the rubric clear? (4) Who's auditing Version A vs their own repo? Take mental or physical notes; you'll use the most common patterns on Slide 14. At the 2-minute warning, announce: "Two minutes left. Finish your scores and write down your #1 quick win."

---

## Slide 12: Pair and Fix

### Turn to the person next to you.

1. **Compare scores** — Where did you agree? Where did you diverge?
2. **Pick one quick win** — The single highest-impact fix
3. **Start implementing** — Actually change the code. 12 minutes.

*If you audited Version A, pair with someone who brought their own repo.*

> **Speaker Notes:** Start at ~30:00. About 60 seconds for instructions, then 12 minutes of pair work. "Alright, turn to the person next to you. If you're on the end of a row, turn around. If you audited Version A and the person next to you brought their own repo, great, you're a fresh set of eyes on unfamiliar code." "Compare your scores. Find where you agree and where you disagree. Then pick one quick win between the two of you and start actually fixing it. Write the CLAUDE.md. Split the god file. Add the lint rule. Whatever your #1 was, start it now." For people who audited Version A, they can implement fixes on the demo repo. That's fine; they'll learn by doing. "You've got 12 minutes. I'm walking around again."

---

## Slide 13: Pair Sprint

# 12:00

*[On-screen countdown timer]*

> **Speaker Notes:** Timer runs from 30:00 to 42:00. Rotate between pairs. Good questions: "What did you pick as your quick win?" "What are you stuck on?" "Did your partner spot something you missed?" Be ready to do quick micro-demos at people's laptops. Common requests: "How do I write a good CLAUDE.md?" (pull up Version B's as an example), "How do I split this file?" (show the feature-grouped pattern). At 2-minute mark: "Two minutes. Wrap up what you're doing. I'm going to pull up a few patterns I saw while walking the room."

---

## Slide 14: Pattern Debrief

### What I saw walking the room

*[This slide gets filled in live based on the 2-3 most common issues observed during the audit and pair sprints]*

**Likely patterns:**

- Most common: no rules file at all (Dimension 1, Score 0)
- Second most common: god files / scattered structure (Dimension 2)
- Third: agent can modify test suite (Dimension 3)

*[Live-demo the fix on Version A]*

> **Speaker Notes:** Start at ~42:00. Budget 10 minutes through ~52:00. This is the second live coding moment. Pull up the patterns you observed while walking around. "I talked to about 30 of you in the last 27 minutes. Here's what I saw." Name the 2-3 most common issues. Then live-demo the fix for the top one on Version A. For example, if the most common issue was "no rules file," open Version A in your editor and write a CLAUDE.md live: "Here's what I'd write for this repo. Test command: pytest. Repo map: api_stuff has the routes, stuff/templates has the HTML, tests/ has the tests. Definition of done: tests pass, no new dependencies." Show how the file is 20-30 lines. If the most common issue was god files, open the 500-line app.py and show how you'd split it into experiments/routes.py, experiments/models.py, etc. Keep each demo to 2-3 minutes. Don't try to fix everything; show one clean fix per pattern. **Fallback:** If the live demo is too slow or breaks, narrate the fix verbally and show the Version B code as the "after" state. "Here's what this looks like when it's done" and display the corresponding file from B/.

---

## Slide 15: Lightning Shares + Takeaway

### 3 volunteers. 2 minutes each.

**What's the one thing you're fixing Monday?**

---

### Resources

`[QR CODE to repo]`

- **Workshop repo:** github.com/sshh12/coding-agents-workshop
- **Scorecard:** `scorecard.md` in the repo
- **"AI Can't Read Your Docs":** shrivushankar.substack.com

> **Speaker Notes:** Start at ~52:00. Budget 6-8 minutes for lightning shares plus close. "Three volunteers. Two minutes each. Tell us: what did you score, what did you find, and what's the one thing you're fixing Monday?" Don't ask for hands; point to people you talked to during the walk who had interesting findings. You should have 2-3 candidates in mind from the pair sprint. If nobody volunteers, seed it: "I talked to someone in the back who found a 1,200-line god file. Want to tell us about that?" After the three shares, close fast: "Here's the repo. The scorecard is in there. Both versions of the demo app are in there. My Substack post 'AI Can't Read Your Docs' goes deeper on the file organization patterns." Then the one-sentence close: "Your agent isn't broken. Your codebase is. Go fix it." Don't linger. Thank the audience, leave the QR code up, and step away from the mic. Total time: 60 minutes.
