import datetime
from langchain_core.tools import tool

@tool
def get_current_time():
    """
    Returns the current date and time. 
    Use this when the user asks for the time, date, or when you need to 
    reference the current timestamp for logs or tasks.
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_time_tools():
    return [get_current_time]
