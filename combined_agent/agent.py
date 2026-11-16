from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from common.retry_llm_client import RetryingLiteLLMClient

from .tools import get_current_time, tavily_search

root_agent = Agent(
    model=LiteLlm(
        model="groq/openai/gpt-oss-120b",
        llm_client=RetryingLiteLLMClient(),
        include_reasoning=False,
    ),
    name='combined_agent',
    description="A helpful assistant that can search the web and tell the time anywhere.",
    instruction=(
        "Answer user questions accurately. You have two tools:\n"
        "- tavily_search: search the web for current or factual information you "
        "are unsure about. When you use it, cite the source URLs in your answer.\n"
        "- get_current_time: get the current date and time in a time zone. "
        "Translate place names into IANA time zones yourself "
        "(e.g. Mumbai -> Asia/Kolkata).\n"
        "If a tool returns status 'error', explain the problem and ask the user "
        "to clarify. Use both tools in one answer when a question needs both."
    ),
    tools=[tavily_search, get_current_time],
)
