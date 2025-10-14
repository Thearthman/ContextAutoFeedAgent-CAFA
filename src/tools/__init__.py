"""
Agent tools for web search, web reading, and local file access.
"""

from .web_search import google_search
from .web_reader import read_webpage
from .file_reader import read_local_file

__all__ = ['google_search', 'read_webpage', 'read_local_file']

