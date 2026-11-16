from google.adk.agents.llm_agent import Agent
from google.adk.tools.google_search_tool import google_search

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=
        ("Answer user questions accurately. "
         "Use Google Search to find information when necessary. "
         "If you use Google Search, provide the search results in your answer."
        ),
    tools=[google_search],
)
