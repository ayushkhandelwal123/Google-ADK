# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Google Agent Development Kit (ADK) workspace (`google-adk` 2.14.1, `google-genai` 2.34.0). Each subdirectory is one ADK agent package; currently only `test_bot/`. There are no tests, linters, or dependency manifests (packages are installed directly into `.venv`).

## Environment

The virtualenv lives at the workspace root in `.venv` (Windows layout):

```powershell
.venv\Scripts\Activate.ps1        # PowerShell
source .venv/Scripts/activate     # Git Bash
```

Each agent reads credentials from its own `.env` (e.g. `test_bot/.env`, which sets `GOOGLE_API_KEY` and `GOOGLE_GENAI_USE_ENTERPRISE`). `.env` and `.adk/` are gitignored.

## Running agents

Run ADK CLI commands from the workspace root (`d:\AI\Google-ADK`), passing the agent directory name:

```bash
adk run test_bot     # interactive terminal chat with the agent
adk web              # dev web UI; lists every agent package in the current directory
adk api_server       # FastAPI server exposing all agents in the current directory
```

## Agent package structure

ADK discovers an agent by convention, so every agent directory must keep this shape:

- `__init__.py` contains `from . import agent`.
- `agent.py` defines a module-level variable named `root_agent` (an `Agent` from `google.adk.agents.llm_agent`). The model, instruction, tools and sub-agents are all configured on that object.
- `.adk/session.db` is local SQLite session state created by the ADK runtime. It is not source.

To add a new agent, create a sibling directory with the same three pieces (`__init__.py`, `agent.py` exporting `root_agent`, `.env`).
