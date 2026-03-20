import os
from langchain_core.tools import Tool

def read_file(file_path: str) -> str:
    """Reads a file from the local filesystem."""
    print(f"\n[Tool: read_file] Reading: {file_path}...")
    try:
        # Basic security check to prevent reading outside the workspace (simplistic)
        # In a real scenario, more robust checks are needed.
        # Assuming workspace root is current working directory
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return f"Error: File {file_path} does not exist."
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_file_reader_tool():
    return Tool(
        name="read_file",
        description="Read the contents of a file. Input should be the relative or absolute path to the file.",
        func=read_file
    )
