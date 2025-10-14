"""
Web page content extraction tool.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional


def read_webpage(url: str, max_length: int = 5000) -> str:
    """
    Fetch and extract main content from a webpage.
    
    Args:
        url: The URL of the webpage to read
        max_length: Maximum content length in characters (default: 5000)
    
    Returns:
        Cleaned text content from the webpage
    """
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Try to find main content
        main_content = None
        
        # Look for common main content containers
        for selector in ['main', 'article', '[role="main"]', '#content', '.content', '#main', '.main']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = soup.body
        
        if not main_content:
            return f"Error: Could not extract content from {url}"
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + f"\n\n[Content truncated at {max_length} characters]"
        
        # Add metadata
        title = soup.title.string if soup.title else "No title"
        result = f"Title: {title}\nURL: {url}\n\n{text}"
        
        return result
    
    except requests.RequestException as e:
        return f"Error fetching webpage: {str(e)}"
    except Exception as e:
        return f"Unexpected error reading webpage: {str(e)}"


# Tool definition for qwen-agent
TOOL_DEFINITION = {
    "name": "read_webpage",
    "description": "Read and extract the main text content from a webpage. Use this after getting URLs from search results to read the actual content of web pages.",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the webpage to read"
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum content length in characters (default: 5000)",
                "default": 5000
            }
        },
        "required": ["url"]
    }
}

