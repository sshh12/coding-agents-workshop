# Optimizing Codebases for Agents

**Conference:** Coding Agents: AI Driven Dev Conference
**Date:** March 3, 2026
**Location:** Computer History Museum, Mountain View, CA
**Speaker:** Shrivu Shankar (VP AI, Abnormal Security)

> Your agent isn't broken. Your codebase is.

## What This Is

This repo contains the materials for the "Optimizing Codebases for Agents" workshop. It includes a demo app in two versions (before and after optimization), an AI-readiness scorecard, and agent race narrator notes.

## Prerequisites

- A laptop with a development environment
- An AI coding tool installed and authenticated (Claude Code, Gemini CLI, Codex CLI, or Cursor)
- Python 3.10+
- A repository you want to audit (open source or personal). If you don't bring one, you can audit the `A/` demo app.

## Quick Start

```bash
git clone https://github.com/sshh12/coding-agents-workshop.git
cd coding-agents-workshop
```

### Run the "Before" app (Version A)

```bash
cd A
pip install -r requirements.txt
python app.py
# Open http://localhost:8000
```

### Run the "After" app (Version B)

```bash
cd B
pip install -r requirements.txt
python manage.py run
# Open http://localhost:8000
```

### Run tests (Version B only)

```bash
cd B
pytest
```

## Repo Structure

```
coding-agents-workshop/
  README.md           # You are here
  scorecard.md        # AI-Readiness Audit (use during the workshop)
  race.md             # Agent Race narrator notes
  slides.html         # Workshop slides (speaker notes embedded as HTML comments)
  A/                  # "Before" -- messy demo app (deliberate anti-patterns)
  B/                  # "After"  -- agent-optimized (same functionality)
```

## Workshop Materials

- **[Slides](https://html-preview.github.io/?url=https://github.com/sshh12/coding-agents-workshop/blob/main/slides.html)** -- Full slide deck (press N for speaker notes, arrow keys to navigate)
- **[scorecard.md](scorecard.md)** -- Score your codebase 0-9 across three dimensions. Bring this up during the audit sprint.
- **[race.md](race.md)** -- Narrator notes for the live agent race demo. Two terminals, same prompt, different codebases.

## Run the Scorecard on Your Repo

You can have Claude Code audit any repo against the scorecard automatically:

> Use web fetch to read https://raw.githubusercontent.com/sshh12/coding-agents-workshop/refs/heads/main/scorecard.md and then spawn tasks in parallel to perform and report an audit of the current repo

Paste this as a prompt to Claude Code inside the repo you want to audit.

## The Demo App

Both `A/` and `B/` implement the same ML Experiment Tracker with dashboard:

- Track experiments (name, description, status)
- Log runs with hyperparameters and metrics (accuracy, loss, latency)
- Compare runs side-by-side with charts
- Dashboard with status badges, metric charts, and activity feed

The difference is how the code is organized. Version A is a realistic mess. Version B is optimized for coding agents.

## License

MIT
