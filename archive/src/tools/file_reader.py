"""
Local file reading tool for markdown and text files.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def read_local_file(file_path: str, max_length: int = 10000) -> str:
    """
    Read content from local .md or .txt files.
    
    Args:
        file_path: Path to the file (absolute or relative)
        max_length: Maximum content length in characters (default: 10000)
    
    Returns:
        File content with metadata
    """
    try:
        # Convert to Path object for security checks
        path = Path(file_path).resolve()
        
        # Security: Check if file exists and is a file (not directory)
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"
        
        # Security: Only allow .md and .txt files
        allowed_extensions = {'.md', '.txt'}
        if path.suffix.lower() not in allowed_extensions:
            return f"Error: Only .md and .txt files are supported. File has extension: {path.suffix}"
        
        # Get file metadata
        stat = path.stat()
        size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Truncate if too long
        truncated = False
        if len(content) > max_length:
            content = content[:max_length]
            truncated = True
        
        # Format result with metadata
        result = f"File: {path.name}\n"
        result += f"Path: {path}\n"
        result += f"Size: {size} bytes\n"
        result += f"Modified: {modified_time}\n"
        result += f"{'─' * 60}\n\n"
        result += content
        
        if truncated:
            result += f"\n\n[Content truncated at {max_length} characters]"
        
        return result
    
    except PermissionError:
        return f"Error: Permission denied reading file: {file_path}"
    except Exception as e:
        return f"Unexpected error reading file: {str(e)}"


# Tool definition for qwen-agent
TOOL_DEFINITION = {
    "name": "read_local_file",
    "description": "Read content from local markdown (.md) or text (.txt) files. Use this to access your local notes, documentation, or text files.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file (can be absolute or relative path)"
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum content length in characters (default: 10000)",
                "default": 10000
            }
        },
        "required": ["file_path"]
    }
}

