import os
from langchain_core.tools import tool
from pathlib import Path

# Configuration
OBSIDIAN_ROOT = Path(r"C:\Users\17610\OneDrive\Lefun")

def _is_safe_path(path: Path) -> bool:
    """Ensure the path is within the Obsidian root."""
    try:
        # Resolve resolves symlinks and absolute paths
        return OBSIDIAN_ROOT.resolve() in path.resolve().parents or path.resolve() == OBSIDIAN_ROOT.resolve()
    except Exception:
        return False

@tool
def list_obsidian_files(subfolder: str = ""):
    """
    Lists files and folders within the user's Obsidian Vault (personal knowledge base).
    Use this to explore the directory structure or find specific notes.
    
    Args:
        subfolder: The relative path inside the vault to list. Leave empty for root.
                   Example: "Daily Notes" or "Projects/ProjectA"
    """
    target_path = OBSIDIAN_ROOT / subfolder
    
    # Security check
    if not _is_safe_path(target_path):
        return "Error: Access denied. You can only access files inside the Obsidian Vault."
    
    if not target_path.exists():
        return f"Error: Path '{subfolder}' does not exist in Obsidian Vault."
    
    try:
        items = os.listdir(target_path)
        # Filter hidden files
        items = [i for i in items if not i.startswith('.')]
        
        # Format output
        formatted_list = []
        for item in items:
            full_path = target_path / item
            kind = "DIR" if full_path.is_dir() else "FILE"
            formatted_list.append(f"[{kind}] {item}")
            
        return "\n".join(formatted_list)
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def read_obsidian_file(filepath: str):
    """
    Reads the content of a markdown note or text file from the Obsidian Vault.
    
    Args:
        filepath: The relative path to the file.
                  Example: "Ideas.md" or "Daily Notes/2023-10-27.md"
    """
    target_path = OBSIDIAN_ROOT / filepath
    
    # Security check
    if not _is_safe_path(target_path):
        return "Error: Access denied. You can only access files inside the Obsidian Vault."

    if not target_path.exists():
        # Try adding .md extension if missing
        if not str(target_path).endswith('.md'):
             target_path = target_path.with_suffix('.md')
             if not target_path.exists():
                 return f"Error: File '{filepath}' not found."
        else:
            return f"Error: File '{filepath}' not found."

    try:
        with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            return content
    except Exception as e:
        return f"Error reading file: {e}"

def get_obsidian_tools():
    return [list_obsidian_files, read_obsidian_file]
