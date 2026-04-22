import os
import requests
from typing import Dict, Any, Optional

def brave_search(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform a web search using the Brave Search API.
    
    Args:
        query (str): The search query.
        api_key (str, optional): Brave Search API key. Defaults to BRAVE_API_KEY environment variable.
        
    Returns:
        Dict[str, Any]: JSON response from the Brave Search API containing search results.
    """
    key = api_key or os.environ.get("BRAVE_API_KEY")
    if not key:
        raise ValueError("Brave API key is required. Pass it or set the BRAVE_API_KEY environment variable.")
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": key
    }
    
    response = requests.get(url, headers=headers, params={"q": query})
    response.raise_for_status()
    return response.json()

def jina_search(query: str, api_key: Optional[str] = None) -> str:
    """
    Perform a web search using the Jina Search API (s.jina.ai).
    By default, Jina returns results formatted in Markdown, which is ideal for LLMs.
    
    Args:
        query (str): The search query.
        api_key (str, optional): Jina API key. Defaults to JINA_API_KEY environment variable.
        
    Returns:
        str: The markdown formatted search results.
    """
    key = "jina_1b2c89c1b74e4aa5a7b95397f9e3f9ab373BCd76kRR8FtYmaq_iPfzaOOy-"
    url = f"https://s.jina.ai/{query}"
    headers = {}
    
    if key:
        headers["Authorization"] = f"Bearer {key}"
        
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def jina_read(target_url: str, api_key: Optional[str] = None) -> str:
    """
    Read and extract clean markdown content from a URL using the Jina Reader API (r.jina.ai).
    
    Args:
        target_url (str): The URL of the webpage to read.
        api_key (str, optional): Jina API key. Defaults to JINA_API_KEY environment variable.
        
    Returns:
        str: The markdown formatted content of the webpage.
    """
    key = ""
    url = f"https://r.jina.ai/{target_url}"
    headers = {}
    
    if key:
        headers["Authorization"] = f"Bearer {key}"
        
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text
