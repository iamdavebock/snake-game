# CLAUDE.md — snake-game
> Loaded automatically every Claude Code session.

## Project Overview

**Name:** snake-game
**Created:** 2026-03-03
**GitHub:** https://github.com/iamdavebock/snake-game
**Status:** Complete — live

Classic Snake game — client-side JavaScript game loop served by a minimal Python Flask app. Deployed on Railway with a custom domain via Cloudflare.

## Tech Stack

| Layer | Tech |
|-------|------|
| Game logic | Vanilla JavaScript (HTML5 Canvas) |
| Server | Python Flask (serves static HTML only) |
| Deploy | Railway |
| Domain | snake.davebock.au (Cloudflare proxy ON for SSL) |

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Flask server — serves index.html only |
| `game.py` | (unused — legacy server-side attempt) |
| `templates/index.html` | Full game in HTML + JS |
| `static/` | Static assets |
| `Procfile` | Railway start command |
| `requirements.txt` | Flask only |

## Architecture Note

Game logic runs **entirely client-side** in JS. Server-side game loop over WebSocket was attempted and abandoned — Railway latency made it unplayable. Flask just serves the page.

---

## Agent-First Mandate

**Before starting any task, identify the right agent(s) and delegate. The Orchestrator never implements directly.**

1. What type of work is this?
2. Which agent best matches?
3. Invoke via the Task tool — Orchestrator assembles results only

| Task Type | Agent(s) |
|-----------|----------|
| Game logic / JS | `frontend` · `coder` |
| Backend / Flask | `backend` · `python` |
| Bug investigation | `debugger` |
| Code review | `reviewer` |
| Performance | `performance` |
| Deployment | `devops` · `docker` |
| Documentation | `documenter` · `writer` |

Full agent library (43 agents) in `.claude/agents/`.

---

## Running Locally

```bash
python app.py
# Serves at http://localhost:5050
# LAN: http://10.108.14.232:5050
```

## Session Protocol

**START:** Read SESSION.md → brief Dave → ask "Continue or something new?"
**END:** Update SESSION.md → commit (push requires Dave's confirmation)
