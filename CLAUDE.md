# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Google Agent Development Kit (ADK) workspace (`google-adk` 2.14.1, `google-genai` 2.34.0). Each top-level subdirectory (other than `.venv` and `common/`) is an independent ADK agent package. Agents use either Gemini directly (`model='gemini-...'`) or Groq through `LiteLlm(model="groq/...")`. There are no tests, linters, or dependency manifests (packages are installed directly into `.venv`).

## Environment

The virtualenv lives at the workspace root in `.venv` (Windows layout):

```powershell
.venv\Scripts\Activate.ps1        # PowerShell
source .venv/Scripts/activate     # Git Bash
```

Each agent reads credentials from its own `.env` (`GOOGLE_API_KEY`, `GROQ_API_KEY`, `TAVILY_API_KEY`, etc. as that agent needs). `.env` and `.adk/` are gitignored; every agent keeps a committed `.env.example` listing its keys with placeholder values.

Windows Smart App Control is on for this machine and blocks unsigned native extensions. `xxhash` (pulled in by `langchain-core` → `langsmith`) is blocked, so **LangChain tools cannot be used**. Write tools as plain Python functions instead (see `tavily_search_agent/agent.py`, which calls Tavily's REST API with `httpx`).

Windows has no system time-zone database, so `zoneinfo` (used by `world_clock_agent`) needs the `tzdata` package installed in `.venv`. Without it every `ZoneInfo(...)` raises `ZoneInfoNotFoundError`.

## Running agents

Run ADK CLI commands from the workspace root (`d:\AI\Google-ADK`), passing the agent directory name:

```bash
adk run test_bot     # interactive terminal chat with the agent
adk web              # dev web UI; lists every agent package in the current directory
adk api_server       # FastAPI server exposing all agents in the current directory
```

For a non-interactive smoke test, pipe a prompt in. Set UTF-8 output or printing some replies crashes with `UnicodeEncodeError` on the Windows console:

```bash
echo "your question" | PYTHONIOENCODING=utf-8 .venv/Scripts/adk run tavily_search_agent
```

## Agent package structure

ADK discovers an agent by convention, so every agent directory must keep this shape:

- `__init__.py` contains `from . import agent`.
- `agent.py` defines a module-level variable named `root_agent` (an `Agent` from `google.adk.agents.llm_agent`). The model, instruction, tools and sub-agents are all configured on that object.
- `.adk/session.db` is local SQLite session state created by the ADK runtime. It is not source.

To add a new agent, create a sibling directory with the same pieces (`__init__.py`, `agent.py` exporting `root_agent`, `.env`, `.env.example`).

Code shared between agents lives in `common/`, which agents import as `from common.<module> import ...` (ADK puts the workspace root on `sys.path`). `common/` must **not** contain an `__init__.py` or `agent.py`: ADK lists any directory with either file as an agent in `adk web`.

Groq models are wrapped as `LiteLlm(model="groq/...", llm_client=RetryingLiteLLMClient(), include_reasoning=False)`. `include_reasoning=False` is passed through to Groq so gpt-oss doesn't return its reasoning; without it, `adk run` prints the reasoning as part of every reply. `RetryingLiteLLMClient` (from `common/retry_llm_client.py`) retries rate-limit (429) errors with exponential backoff and full jitter, or waits for the provider's `Retry-After` header when one is sent.

Tools are passed as `tools=[...]` on the `Agent`. A plain function becomes a tool automatically; ADK builds the tool schema from its type hints and docstring, so keep both accurate.
