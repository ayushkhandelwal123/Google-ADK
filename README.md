# Google ADK Agents

A collection of small agents built with Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/). Most of them run on Groq's `openai/gpt-oss-120b` model through LiteLLM; two use Gemini with Google Search.

## Agents

| Agent | Model | Tools | What it does |
|---|---|---|---|
| `test_bot` | Groq `gpt-oss-120b` | none | General Q&A (temperature 0.4, max 1000 output tokens) |
| `google_agent` | Gemini `gemini-3.5-flash` | `google_search` | Answers questions using Google Search |
| `tavily_search_agent` | Groq `gpt-oss-120b` | `tavily_search` | Answers questions using Tavily web search, citing sources |
| `world_clock_agent` | Groq `gpt-oss-120b` | `get_current_time` | Tells the current time and date anywhere in the world |
| `combined_agent` | Groq `gpt-oss-120b` | `tavily_search`, `get_current_time` | Web search and world clock in one agent |
| `mcp_agent` | Gemini `gemini-3.5-flash` | filesystem MCP server, `google_search` | Reads, writes, edits and organises files in `mcp_agent/files/`, and can research topics with Google Search and save the results there |

All Groq agents share `common/retry_llm_client.py`, which retries rate-limit (HTTP 429) errors with exponential backoff and jitter, and they hide gpt-oss's reasoning text from replies.

`mcp_agent` connects to the official [filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem), which it starts with `npx`. The server can only access `mcp_agent/files/` (created automatically and not committed), and has no delete tool. The agent's instruction includes today's date, so searches for "this week's news" return current results instead of ones from the model's training period.

## Setup

Requires Python 3.13 (the version this was built and tested with). `mcp_agent` also needs [Node.js](https://nodejs.org/) so that `npx` is available; the first run downloads the filesystem server from npm.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
# source .venv/Scripts/activate     # Git Bash
# source .venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
```

Each agent reads its API keys from its own `.env` file. Copy the example in each agent folder you want to run and fill in your keys:

```bash
cp tavily_search_agent/.env.example tavily_search_agent/.env
```

| Key | Used by | Get one at |
|---|---|---|
| `GROQ_API_KEY` | all Groq agents | https://console.groq.com/keys |
| `TAVILY_API_KEY` | `tavily_search_agent`, `combined_agent` | https://app.tavily.com |
| `GOOGLE_API_KEY` | `google_agent`, `mcp_agent` | https://aistudio.google.com/apikey |

Google Search and Gemini calls are billed to your Google AI Studio account. If they fail with `402 RESOURCE_EXHAUSTED`, the account's prepaid credits have run out.

## Running

Run these from the repository root:

```bash
adk run combined_agent   # chat with one agent in the terminal
adk web                  # browser UI with every agent in a dropdown
```

On Windows, if piping input into `adk run` crashes with `UnicodeEncodeError`, set `PYTHONIOENCODING=utf-8` first.

## Adding an agent

```bash
adk create my_agent
```

Then switch the model to Groq the same way the other agents do:

```python
from google.adk.models.lite_llm import LiteLlm
from common.retry_llm_client import RetryingLiteLLMClient

model=LiteLlm(
    model="groq/openai/gpt-oss-120b",
    llm_client=RetryingLiteLLMClient(),
    include_reasoning=False,
)
```

Tools are plain Python functions passed in `tools=[...]`. ADK reads each function's type hints and docstring to tell the model how to call it.
