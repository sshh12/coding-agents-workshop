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
- The trap: 500-line rules files that drown the agent in noise
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

- Agent read a **500-line god file** trying to understand the app
- Couldn't find templates (they're in `stuff/`)
- Only test was `assert 1 + 1 == 2`; no real verification
- Wrote string-typed code with no guardrails

### Version B (optimized)

- Agent read **50-line CLAUDE.md**, got a repo map in 10 seconds
- Found `experiments/` folder, followed existing pattern
- Added tag model + endpoint + template, matching the structure
- Ran `pytest`, **tests passed on the first try**

> **Speaker Notes:** Start at ~5:00. Spend about 3 minutes here. Walk through what happened in each terminal, tying failures to specific structural problems. "On the left, the agent spent its first 30 seconds reading a 500-line file called app.py. That's not a prompt problem, that's a file organization problem. It couldn't find the templates because they were in a folder called 'stuff'. That's a naming problem. The only test was assert 1+1 equals 2, so even after it wrote broken code, nothing caught it. That's a verification problem." Then flip: "On the right, the agent opened CLAUDE.md, got a repo map, knew exactly where to go. It found experiments/, saw the pattern of routes.py, models.py, schemas.py, and followed it. It ran pytest, got green, and stopped." Pause. "Same model. Same prompt. Different codebase. That's the whole talk." Transition: "So what are the actual levers? There are three."

---

## Slide 5: Three Dimensions of Agent-Readiness

```
                    +-----------------+
                    |  RULES FILE     |  Does the agent know the rules?
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

## Slide 6: Dimension 1 — Rules File

### The 150-line rule

**What to include:**
- Exact commands: `pytest`, `npm run lint`, `python manage.py run`
- Repo map: where entrypoints, configs, and tests live
- Definition of done: what must be true before the agent stops
- 1-2 code examples: a good pattern and a bad pattern
- Hard boundaries: "do not touch generated files," "ask before adding deps"

**What NOT to include:**
- Your entire architecture doc
- General coding philosophy
- Anything over 150 lines

> **Speaker Notes:** Start at ~9:00. About 90 seconds. "The rules file is the single highest-leverage thing you can add to any repo. And the most common mistake is making it too long. Past 150 lines, the agent starts losing signal in the noise. Think of it as a cheat sheet for a new hire on their first day, not the employee handbook." Reference the demo: "In Version B, the CLAUDE.md was 50 lines. It had the test command, a repo map, and a definition of done. That's it. And that was enough for the agent to navigate the entire codebase." Mention progressive disclosure: "For monorepos, put global rules at the root and folder-level rules in each package. The agent picks up the relevant context as it navigates." Transition: "But even the best rules file can't save you if the agent can't find anything."

---

## Slide 7: Dimension 2 — File Organization

### Five patterns that make codebases agent-readable

1. **Every output is a prompt** — errors and CLI output guide the agent's next step
2. **Self-documenting code** — `--help` flags and header comments, not external wikis
3. **Right interface** — CLI for agents that script; MCP for structured tool calls
4. **Metaphorical interface** — model your tools after pytest, pandas, kubectl
5. **Workflows, not concepts** — co-locate by feature (`/experiments/`), not by layer (`/models/`)

### The practical rules

- Max **300 lines** per file
- **Descriptive names**: `experiment_routes.py`, not `er.py`
- **Feature-grouped folders**: everything for one feature in one place

> **Speaker Notes:** Start at ~10:30. About 2 minutes. This is the densest slide, so don't read every bullet. Instead, ground each pattern in the demo: "You saw the difference between 'stuff/templates' and 'experiments/templates'. That's pattern 5: co-locate by feature, not by concept. You saw the agent on the left get a silent 'Success!' from the CLI and not know what to do next. Pattern 1 says every output should be a prompt for the next action." Hit the practical rules quickly: "300 lines per file, descriptive names, feature-grouped folders. These are the mechanical changes. You can audit for them in 5 minutes." If anyone brought up Simon Willison's post or Francois Chollet's tweet during Q&A or hallway chats earlier, reference them: "Simon Willison wrote about this last year: make your codebase productive for AI tools. Surprisingly none of his recommendations involved CLAUDE.md files. It's all structure." Transition: "Structure gets the agent to the right place. But how does it know if it did the right thing?"

---

## Slide 8: Dimension 3 — Test & Verification

### The confidence spectrum

```
Linters → Types → Unit Tests → Integration → E2E → Visual
   ←  fast, cheap, narrow  |  slow, expensive, comprehensive  →
```

### The critical rule: fixed test suites

- The agent runs tests. The agent does **not** write tests.
- If the agent can delete a test to make a bug pass, your suite is broken.
- Protect test files from agent modification.

### Anti-pattern: the agent's own tests

```
# Agent writes this to "verify" its broken code
def test_tags():
    assert add_tags(1, ["ml"]) is not None  # passes, proves nothing
```

> **Speaker Notes:** Start at ~12:30. About 90 seconds. "This is the dimension most teams score lowest on. Not because they don't have tests, but because the agent can rewrite the tests." Tell the story from the demo: "In Version A, the only test was 'assert 1+1 equals 2'. The agent could have written any code it wanted, run the test, gotten green, and declared victory. That's not verification, that's theater." Then lay out the confidence spectrum: "Linters catch formatting. Types catch wrong shapes. Unit tests catch wrong logic. Integration tests catch wrong wiring. E2E tests catch wrong behavior. The more layers the agent hits on every change, the more you can trust it." The key insight: "Your test suite is a guardrail, not a scorecard. Protect it like you protect your production database." Transition: "Before we move on, let me hit a few patterns you should actively avoid."

---

## Slide 9: The Anti-Patterns

| Anti-Pattern | What Happens | The Fix |
|---|---|---|
| **Rule-gaming** | Agent modifies lint rules instead of fixing code | Lock config files from agent writes |
| **Self-written tests** | Agent writes tests that make its own bugs pass | Fixed test suite the agent can't touch |
| **Infinite retries** | Agent retries failing commands, burns tokens | "Fail twice, stop and explain" rule |
| **Error swallowing** | Agent wraps everything in try/catch, hides failures | "Let errors surface clearly" in rules file |
| **Bloated context** | 500-line CLAUDE.md drowns signal in noise | 150-line limit, progressive disclosure |

> **Speaker Notes:** Start at ~14:00. About 60 seconds. Go through the table quickly. "Five things I see teams get burned by. Rule-gaming: the agent changes your ESLint config instead of fixing the code. Self-written tests: looks great in CI, breaks on review. Infinite retries: the agent fails, tries again, fails, tries again, burns through your token budget. Error swallowing: the agent wraps everything in try/catch so nothing ever fails. And bloated context: you wrote a 500-line rules file thinking more is better, and the agent can't find anything in it." These should feel like quick hits, not deep dives. The audience can reference the scorecard later for details. Transition: "Alright. That's the framework. Now it's your turn."

---

## Slide 10: Your Turn — The Audit Sprint

### Score your codebase. 15 minutes. Go.

**Instructions:**

1. Open `scorecard.md` in the workshop repo (QR code below)
2. Score your repo **0-3** on each dimension: Rules File, File Organization, Test & Verification
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
