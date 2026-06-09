"""
Custom CrewAI Tools for Web Scraping
Uses Jina.ai Reader API (no API key required for basic use)
"""

import requests
from crewai.tools import tool


@tool("Website Content Scraper")
def scrape_website(url: str) -> str:
    """
    Scrapes and extracts clean, readable content from any website URL using the Jina.ai Reader API.
    This tool fetches the main text content of a webpage, stripping away ads and navigation clutter.
    Use this tool to get detailed information from a company's website, news articles, or any web page.
    Input should be a valid URL starting with http:// or https://
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            "Accept": "text/plain",
            "X-Return-Format": "text",
            "X-Timeout": "25",
        }
        response = requests.get(jina_url, headers=headers, timeout=30)

        if response.status_code == 200:
            content = response.text.strip()
            if not content:
                return f"No readable content found at {url}"
            # Cap at 6000 chars to avoid token limits
            if len(content) > 6000:
                content = content[:6000] + "\n\n[Content truncated for brevity...]"
            return f"Content from {url}:\n\n{content}"
        else:
            return f"Failed to scrape {url}. HTTP Status: {response.status_code}"

    except requests.exceptions.Timeout:
        return f"Request timed out while scraping {url}. The website may be slow or unavailable."
    except requests.exceptions.ConnectionError:
        return f"Could not connect to {url}. Please check the URL."
    except Exception as e:
        return f"Unexpected error scraping {url}: {str(e)}"


@tool("News Article Extractor")
def extract_news_article(url: str) -> str:
    """
    Extracts the full text content of a news article or blog post from a given URL.
    Ideal for reading news articles, press releases, and blog posts about a company.
    Input should be a direct URL to the article.
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            "Accept": "text/plain",
            "X-Return-Format": "text",
            "X-Timeout": "20",
        }
        response = requests.get(jina_url, headers=headers, timeout=25)

        if response.status_code == 200:
            content = response.text.strip()
            if len(content) > 5000:
                content = content[:5000] + "\n\n[Article truncated...]"
            return f"Article from {url}:\n\n{content}"
        else:
            return f"Could not fetch article from {url}. Status: {response.status_code}"
    except Exception as e:
        return f"Error extracting article: {str(e)}"
