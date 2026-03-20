from langchain_core.tools import tool
from src.soul import Soul

@tool
def add_task_to_queue(task_description: str):
    """
    Adds a task to the agent's subconscious queue to be performed later.
    Use this when the user asks you to do something "later", "in the background", or "remind me to...".
    
    Args:
        task_description: The detailed description of what needs to be done.
    """
    try:
        soul = Soul()
        soul.add_task(task_description, source="user")
        soul.close()
        return "Task added to queue successfully. The Inner Agent will pick it up shortly."
    except Exception as e:
        return f"Error adding task: {e}"

def get_task_tool():
    return add_task_to_queue
