"""
Google search tool using web scraping.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time


def google_search(query: str, num_results: int = 10) -> str:
    """
    Search Google and return top results.
    
    Args:
        query: The search query string
        num_results: Number of results to return (default: 10)
    
    Returns:
        Formatted string with search results including titles, snippets, and URLs
    """
    try:
        # Add delay to avoid rate limiting
        time.sleep(1)
        
        # Construct Google search URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        params = {
            'q': query,
            'num': num_results,
            'hl': 'en'
        }
        
        url = 'https://www.google.com/search'
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search results
        results = []
        
        # Find all search result divs
        search_divs = soup.find_all('div', class_='g')
        
        for div in search_divs[:num_results]:
            try:
                # Extract title
                title_elem = div.find('h3')
                title = title_elem.text if title_elem else 'No title'
                
                # Extract URL
                link_elem = div.find('a')
                url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'No URL'
                
                # Extract snippet
                snippet_elem = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                if not snippet_elem:
                    snippet_elem = div.find('span', class_='aCOpRe')
                snippet = snippet_elem.text if snippet_elem else 'No description available'
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
            except Exception as e:
                continue
        
        # Format results as string
        if not results:
            return f"No search results found for query: '{query}'"
        
        formatted_results = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result['title']}\n"
            formatted_results += f"   URL: {result['url']}\n"
            formatted_results += f"   {result['snippet']}\n\n"
        
        return formatted_results.strip()
    
    except requests.RequestException as e:
        return f"Error performing search: {str(e)}"
    except Exception as e:
        return f"Unexpected error during search: {str(e)}"


# Tool definition for qwen-agent
TOOL_DEFINITION = {
    "name": "google_search",
    "description": "Search Google for information. Use this when you need to find current information, news, articles, or any web content. Returns titles, URLs, and snippets of top search results.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on Google"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of search results to return (default: 10, max: 20)",
                "default": 10
            }
        },
        "required": ["query"]
    }
}

