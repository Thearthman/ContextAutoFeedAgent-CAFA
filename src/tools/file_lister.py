import os
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional

class ListFilesInput(BaseModel):
    directory_path: str = Field(description="The local directory path to list.")
    level: int = Field(default=1, description="How many levels of subdirectories to list. Default is 1.")

def list_files(directory_path: str, level: int = 1) -> str:
    """Lists files and directories in a given path, restricted to the P: drive."""
    print(f"\n[Tool: list_files] Listing directory: {directory_path} (level: {level})...")
    try:
        # Handle "P" or "P:" to ensure it points to the root P:\ 
        # instead of the current working directory on P:
        clean_path = directory_path.strip()
        if clean_path.lower() in ["p", "p:"]:
            clean_path = "P:\\"
        elif clean_path.lower().startswith("p:") and len(clean_path) == 2:
            clean_path = "P:\\"
            
        # Normalize path and check if it starts with P:
        abs_root = os.path.abspath(clean_path)
        
        # Security check: Ensure it's on the P: drive
        if not abs_root.lower().startswith('p:'):
            return "Error: Access denied. This tool is restricted to the P: drive."
            
        if not os.path.exists(abs_root):
            return f"Error: Directory '{directory_path}' does not exist."
            
        if not os.path.isdir(abs_root):
            return f"Error: '{directory_path}' is not a directory."

        output = [f"Contents of {abs_root} (depth level: {level}):"]
        items_count = 0
        limit = 100

        def walk_dir(current_path, current_level):
            nonlocal items_count
            if current_level > level or items_count >= limit:
                return

            try:
                items = os.listdir(current_path)
                items.sort()
            except Exception as e:
                output.append(f"{'  ' * current_level}[Error reading {current_path}: {e}]")
                return

            for item in items:
                if items_count >= limit:
                    break
                
                item_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(item_path)
                type_str = "[DIR]" if is_dir else "[FILE]"
                
                indent = "  " * (current_level)
                output.append(f"{indent}{type_str} {item}")
                items_count += 1
                
                if is_dir and current_level < level:
                    walk_dir(item_path, current_level + 1)

        walk_dir(abs_root, 1)
            
        if items_count >= limit:
            output.append(f"\n... (truncated to {limit} items).")
            
        return "\n".join(output)
        
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def get_file_lister_tool():
    return StructuredTool.from_function(
        func=list_files,
        name="list_files",
        description="List files and folders in a local directory with a specified depth level. Restricted to the P: drive.",
        args_schema=ListFilesInput
    )
