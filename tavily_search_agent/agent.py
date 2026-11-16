import os

import httpx
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from common.retry_llm_client import RetryingLiteLLMClient

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def tavily_search(query: str) -> dict:
    """Searches the web with Tavily and returns the top results.

    Args:
        query: The search query.

    Returns:
        A dict with a list of results, each with a title, url and content snippet,
        or an error message if the search failed.
    """
    try:
        response = httpx.post(
            TAVILY_SEARCH_URL,
            headers={"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}"},
            json={"query": query, "max_results": 5, "topic": "general"},
            timeout=30,
        )
        response.raise_for_status()
    except (KeyError, httpx.HTTPError) as e:
        return {"status": "error", "error_message": f"Tavily search failed: {e!r}"}

    results = [
        {"title": r.get("title"), "url": r.get("url"), "content": r.get("content")}
        for r in response.json().get("results", [])
    ]
    return {"status": "success", "results": results}


root_agent = Agent(
    model=LiteLlm(
        model="groq/openai/gpt-oss-120b",
        llm_client=RetryingLiteLLMClient(),
        include_reasoning=False,
    ),
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=
        ("Answer user questions accurately. "
         "Use the tavily_search tool to find information when necessary. "
         "If you use it, cite the source URLs in your answer."
        ),
    tools=[tavily_search],
)
