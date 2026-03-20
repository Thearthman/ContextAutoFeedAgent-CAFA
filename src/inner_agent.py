from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from src.llm_client import get_llm
from src.tools.web_search import get_web_search_tool
from src.tools.file_reader import get_file_reader_tool
from src.tools.file_lister import get_file_lister_tool
from src.tools.web_reader import get_web_reader_tool
from src.tools.obsidian_tools import get_obsidian_tools
from src.tools.workspace_tools import get_workspace_tools
from src.tools.time_tools import get_time_tools

def get_inner_agent_executor():
    """
    Creates the 'Subconscious' agent with restricted tools and specific persona.
    """
    llm = get_llm()
    
    # SAFE TOOLSET (No Write/Delete/Image Analysis)
    tools = [
        get_web_search_tool(),
        get_file_reader_tool(),  # Already read-only
        get_file_lister_tool(),
        get_web_reader_tool(),
        *get_obsidian_tools(),
        *get_workspace_tools(),
        *get_time_tools()
    ]
    
    memory = MemorySaver()
    
    system_msg = """You are the Subconscious Inner Monologue of an autonomous AI. 
    You DO NOT talk to the user directly. 
    Your job is to execute the tasks given to you efficiently and silently.
    
    If the task asks you to "Draft a message", you should output the message content clearly.
    If the task asks you to research, you should read the material and summarize it.
    
    RESTRICTIONS:
    - You cannot modify files.
    - You cannot delete files.
    - You generally do not need to ask clarifying questions (there is no one to answer). Do your best with what you have.
    """

    agent_executor = create_react_agent(
        llm, 
        tools, 
        checkpointer=memory,
        prompt=system_msg
    )
    
    return agent_executor
