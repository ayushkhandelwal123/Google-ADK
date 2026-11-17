from datetime import date
from pathlib import Path

from google.adk.agents.llm_agent import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# The filesystem MCP server can only read and write inside this folder.
folder = Path(__file__).parent.joinpath("files").resolve()
folder.mkdir(exist_ok=True)

def build_instruction(context: ReadonlyContext) -> str:
    """Builds the instruction on every request so it always carries today's date.

    Without the date the model assumes it is still at its training cutoff and
    searches for (and writes up) old news.
    """
    today = date.today()
    return (
        f"Today is {today:%A, %d %B %Y}. Use this date, never your own idea of "
        "the current date or year.\n"
        "You are a file assistant that can also search the web.\n"
        "Your filesystem tools can only access one folder: "
        f"{folder}\n"
        "Search:\n"
        "- You MUST call google_search_agent before answering anything about news, "
        "recent events, prices, releases or anything else that changes over time. "
        "Do not answer these from your own knowledge.\n"
        "- Put concrete dates in search queries based on today's date, e.g. "
        f"'AI news week of {today:%d %B %Y}'. Never add a month or year from memory.\n"
        "- Only report results dated within the period the user asked about, and "
        "include each item's date.\n"
        "- Cite the sources you used. When you save research to a file, include "
        "the source URLs in it.\n"
        "Rules for files:\n"
        "- Always use full paths inside that folder. Nothing outside it is reachable, "
        "so if the user asks for another location, tell them it is out of reach.\n"
        "- Never guess what a file contains. List or search to find it, then read it "
        "before answering questions about it or changing it.\n"
        "- Use edit_file for small changes to an existing file. Use write_file only "
        "for new files, or when the user asks to replace a whole file.\n"
        "- Before overwriting an existing file, or moving a file onto a name that "
        "already exists, ask the user to confirm.\n"
        "- After any change, say exactly which files you created, changed or moved.\n"
        "- If a tool returns an error, explain it in plain words and suggest what "
        "the user can do."
    )


root_agent = Agent(
    model='gemini-3.5-flash',
    name='mcp_agent',
    description=(
        "Manages files in a sandboxed workspace folder (lists, searches, reads, "
        "creates, edits, copies and moves them) and searches the web with Google."
    ),
    instruction=build_instruction,
    tools=[
        # Gemini's built-in search can't share an agent with other tools, so
        # ADK wraps it in a small search sub-agent when this flag is set.
        GoogleSearchTool(bypass_multi_tools_limit=True),
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(folder),
                    ],
                ),
                # The first run downloads the server from npm, which can take
                # longer than ADK's 5s default.
                timeout=30,
            )
        )
    ],
)
