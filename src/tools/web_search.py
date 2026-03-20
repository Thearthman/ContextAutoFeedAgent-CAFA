from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool

def web_search(query: str) -> str:
    """Search the web for information using DuckDuckGo."""
    print(f"\n[Tool: web_search] Searching for: {query}...")
    search = DuckDuckGoSearchRun()
    return search.run(query)

def get_web_search_tool():
    """
    Returns a Web Search tool using DuckDuckGo.
    """
    return Tool(
        name="web_search",
        description="Search the web for information. Use this for current events or information not in your training data.",
        func=web_search
    )
