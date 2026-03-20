import os
import difflib
import re
from langchain_core.tools import tool
from pathlib import Path

# Configuration
WORKSPACE_ROOT = Path(r"C:\Users\17610\OneDrive\Lefun\5 - Utility\CAFA")

def _is_safe_path(path: Path) -> bool:
    """Ensure the path is within the Workspace root."""
    try:
        # Resolve resolves symlinks and absolute paths
        return WORKSPACE_ROOT.resolve() in path.resolve().parents or path.resolve() == WORKSPACE_ROOT.resolve()
    except Exception:
        return False

def _fuzzy_replace(file_content: str, search_block: str, replace_block: str, threshold: float = 0.85) -> str:
    """
    Finds the search_block in file_content using a waterfall matching algorithm:
    1. Exact match
    2. Normalized whitespace match
    3. Fuzzy similarity match
    """
    # Remove literal "\n" strings that some LLMs hallucinate at line ends
    search_block = search_block.replace('\\n', '')
    replace_block = replace_block.replace('\\n', '')

    # Tier 1: Exact Match
    if search_block in file_content:
        return file_content.replace(search_block, replace_block, 1)

    # Tier 2: Normalized Whitespace Match
    def normalize(text):
        # Remove all whitespace for a pure structural/content check
        return re.sub(r'\s+', '', text)

    norm_file = normalize(file_content)
    norm_search = normalize(search_block)
    
    if norm_search in norm_file:
        # If structural match exists, we use difflib to find the best range in the original
        matcher = difflib.SequenceMatcher(None, file_content, search_block)
        match = matcher.find_longest_match(0, len(file_content), 0, len(search_block))
        if match.size > 0:
            return file_content[:match.a] + replace_block + file_content[match.a + match.size:]

    # Tier 3: Fuzzy Similarity Match
    matcher = difflib.SequenceMatcher(None, file_content, search_block)
    match = matcher.find_longest_match(0, len(file_content), 0, len(search_block))
    
    found_text = file_content[match.a : match.a + match.size]
    if not found_text:
        raise ValueError("Could not find a matching block in the file.")
        
    similarity = difflib.SequenceMatcher(None, found_text, search_block).ratio()

    if similarity >= threshold:
        return file_content[:match.a] + replace_block + file_content[match.a + match.size:]
    else:
        raise ValueError(f"Match not found (best similarity: {similarity:.2f}). Please provide more context in your SEARCH block.")

@tool
def list_workspace_files():
    """
    Lists all files and folders within your private agent workspace recursively.
    Use this to see the complete structure of your work area.
    """
    try:
        if not WORKSPACE_ROOT.exists():
            return "Workspace root does not exist."
            
        formatted_list = []
        for root, dirs, files in os.walk(WORKSPACE_ROOT):
            # Calculate depth for indentation
            rel_path = os.path.relpath(root, WORKSPACE_ROOT)
            if rel_path == ".":
                depth = 0
                prefix = ""
            else:
                depth = rel_path.count(os.sep) + 1
                prefix = "  " * depth
                formatted_list.append(f"{prefix}[DIR] {os.path.basename(root)}")
            
            sub_prefix = "  " * (depth + 1)
            for f in files:
                formatted_list.append(f"{sub_prefix}[FILE] {f}")
                
        return "\n".join(formatted_list) if formatted_list else "Workspace is empty."
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def read_workspace_file(filepath: str):
    """
    Reads the content of a file from your private agent workspace.
    
    Args:
        filepath: The relative path to the file.
    """
    target_path = WORKSPACE_ROOT / filepath
    if not _is_safe_path(target_path):
        return "Error: Access denied."

    if not target_path.exists():
        return f"Error: File '{filepath}' not found."

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_workspace_file(filepath: str, content: str):
    """
    Writes or overwrites a file in your private agent workspace.
    Use this to save notes, logs, or data you want to persist.
    
    Args:
        filepath: The relative path to the file.
        content: The text content to write.
    """
    target_path = WORKSPACE_ROOT / filepath
    if not _is_safe_path(target_path):
        return "Error: Access denied."

    # Ensure parent directories exist
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{filepath}' written successfully."
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def edit_workspace_file(filepath: str, search_text: str, replace_text: str):
    """
    Edits a file in your private agent workspace using a SEARCH/REPLACE block strategy.
    The tool uses fuzzy matching, so you don't need to match whitespace perfectly, 
    but you should provide enough surrounding context to uniquely identify the block.
    
    Args:
        filepath: The relative path to the file.
        search_text: The original text/code block to find. 
        replace_text: The new text/code block to put in its place.
    """
    target_path = WORKSPACE_ROOT / filepath
    if not _is_safe_path(target_path):
        return "Error: Access denied."

    if not target_path.exists():
        return f"Error: File '{filepath}' not found."

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = _fuzzy_replace(content, search_text, replace_text)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"File '{filepath}' updated successfully."
    except ValueError as ve:
        return f"Error: {ve}"
    except Exception as e:
        return f"Error editing file: {e}"

@tool
def delete_workspace_file(filepath: str):
    """
    Deletes a file from your private agent workspace.
    
    Args:
        filepath: The relative path to the file.
    """
    target_path = WORKSPACE_ROOT / filepath
    if not _is_safe_path(target_path):
        return "Error: Access denied."

    if not target_path.exists():
        return f"Error: File '{filepath}' not found."

    try:
        if target_path.is_dir():
            import shutil
            shutil.rmtree(target_path)
        else:
            os.remove(target_path)
        return f"Successfully deleted '{filepath}'."
    except Exception as e:
        return f"Error deleting: {e}"

def get_workspace_tools():
    return [
        list_workspace_files,
        read_workspace_file,
        write_workspace_file,
        edit_workspace_file,
        delete_workspace_file
    ]
