import requests
from bs4 import BeautifulSoup
from langchain_core.tools import Tool

def read_webpage(url: str) -> str:
    """
    Fetch and extract main content from a webpage.
    """
    print(f"\n[Tool: read_webpage] Fetching content from: {url}...")
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
        
        max_length = 5000
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

def get_web_reader_tool():
    return Tool(
        name="read_webpage",
        description="Read and extract the main text content from a webpage. Use this after getting URLs from search results to read the actual content of web pages. Input is the URL.",
        func=read_webpage
    )
