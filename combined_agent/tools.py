"""Tools available to combined_agent."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

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


def get_current_time(timezone: str) -> dict:
    """Get the current date and time in a given time zone.

    Use this whenever the user asks what time or date it is somewhere.

    Args:
        timezone: An IANA time zone name, e.g. "Asia/Kolkata",
            "America/New_York" or "Europe/London".

    Returns:
        A dict with "status" ("success" or "error"). On success it also has
        "timezone", "date", "time" and "weekday". On error it has "error_message".
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except (ZoneInfoNotFoundError, ValueError):
        # ValueError covers malformed names such as "" or "../etc".
        return {
            "status": "error",
            "error_message": f"Unknown time zone '{timezone}'. Use an IANA name like 'Asia/Kolkata'.",
        }
    return {
        "status": "success",
        "timezone": timezone,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
    }
