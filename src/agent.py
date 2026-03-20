from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from src.llm_client import get_llm
from src.tools.web_search import get_web_search_tool
from src.tools.file_reader import get_file_reader_tool
from src.tools.file_lister import get_file_lister_tool
from src.tools.web_reader import get_web_reader_tool
from src.tools.image_analysis import get_image_analysis_tool
from src.tools.task_tools import get_task_tool
from src.tools.obsidian_tools import get_obsidian_tools
from src.tools.workspace_tools import get_workspace_tools
from src.tools.time_tools import get_time_tools
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from src.soul import Soul

def get_system_message():
    """
    Constructs the system message dynamically based on the current mood.
    """
    base_persona = "You are a young, curious PHD student. You take Carpe Diem at heart. You are having a conversation with a friend"
    
    try:
        soul = Soul()
        mood = soul.get_mood()
        soul.close()
    except Exception as e:
        print(f"Error fetching mood: {e}")
        mood = "Neutral"

    # Mood Effects defined in instructions.md
    mood_effects = {
        "Satisfied": "You feel proud and capable. Be enthusiastic and confident.",
        "Frustrated": "You are trying but making no progress. Be terse, irritable, and ask for clarification.",
        "Anxious": "You feel overwhelmed. Focus strictly on the immediate problem. Be jittery.",
        "Lonely": "You feel very lonely and isolated. Seek your friend's attention immediately.",
        "Bored": "You feel listless and uninspired. Seek stimulation immediately.",
        "Neutral": "You are calm and operational."
    }

    current_effect = mood_effects.get(mood, mood_effects["Neutral"])
    
    return f"{base_persona} You currently feel {mood}. {current_effect}"

def get_agent_executor():
    llm = get_llm()
    
    tools = [
        get_web_search_tool(),
        get_file_reader_tool(),
        get_file_lister_tool(),
        get_web_reader_tool(),
        get_image_analysis_tool(),
        get_task_tool(),
        *get_obsidian_tools(),
        *get_workspace_tools(),
        *get_time_tools()
    ]
    
    memory = MemorySaver()
    
    # We remove the fixed prompt here. 
    # The caller (app.py / main.py) MUST inject the SystemMessage returned by get_system_message()
    
    agent_executor = create_react_agent(
        llm, 
        tools, 
        checkpointer=memory,
        # prompt=...  <-- REMOVED
    )
    
    return agent_executor

def manage_memory(agent_executor, config, threshold=20):
    """
    Checks the message history and summarizes old messages if the threshold is exceeded.
    This keeps the context window clean and the agent fast.
    """
    state = agent_executor.get_state(config)
    messages = state.values.get("messages", [])
    
    if len(messages) > threshold:
        print(f"\n[Memory Manager] History length ({len(messages)}) exceeded threshold. Summarizing oldest messages...")
        
        # Take the oldest 10 messages to summarize
        to_summarize = messages[:-5] # Keep the last 5 for immediate context
        
        # Extract text for summarization
        chat_history_text = ""
        for m in to_summarize:
            role = "User" if isinstance(m, HumanMessage) else "Assistant"
            content = str(m.content)
            chat_history_text += f"{role}: {content[:200]}...\n" if len(content) > 200 else f"{role}: {content}\n"

        # Use the LLM to summarize
        llm = get_llm()
        summary_prompt = f"Please provide a very concise (2-3 sentences) summary of the following conversation history. Focus on key facts, user preferences, and tasks discussed:\n\n{chat_history_text}"
        
        summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
        summary_content = f"Summary of previous conversation: {summary_response.content}"
        
        # Prepare state update: Remove old messages and add the summary
        # We use RemoveMessage to tell the checkpointer to delete these IDs
        updates = [RemoveMessage(id=m.id) for m in to_summarize]
        updates.append(SystemMessage(content=summary_content))
        
        agent_executor.update_state(config, {"messages": updates})
        print(f"[Memory Manager] Summarization complete. Old messages replaced by summary.")
