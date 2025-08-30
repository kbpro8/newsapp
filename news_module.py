# news_module.py (Updated for recent articles)

import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

# Set up a null handler for the logger to avoid "No handler found" warnings
# if the module is used in a context where logging is not configured.
logging.getLogger(__name__).addHandler(logging.NullHandler())

import trafilatura

def get_article_content(url, logger):
    logger.info(f"Extracting main content from {url} using trafilatura.")
    try:
        # Download the page content using trafilatura's fetcher
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            logger.warning(f"Trafilatura could not fetch content from {url}.")
            return "Could not fetch content due to download error."

        # Extract the main content, ignoring comments and tables
        content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)

        if not content:
            logger.warning(f"Trafilatura could not extract main content from {url}.")
            return "Could not extract content."

        logger.info(f"Successfully extracted content from {url}.")
        return content
    except Exception as e:
        logger.error(f"An unexpected error occurred during content extraction from {url}: {e}", exc_info=True)
        return "Could not fetch content due to an unexpected error."

def search_aceh_news(query, num_results, logger):
    """Searches for news articles published in the last 3 hours."""
    logger.info(f"Executing news search with query: '{query}'")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_news", "q": query, "api_key": SERPAPI_KEY,
        "num": num_results, "hl": "id", "gl": "id",
        "tbs": "qdr:h3"  # Time filter for the last 3 hours
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    logger.info("News search successful.")
    return response.json()

def select_best_articles(news_results, count=10, preferred_sources=None):
    """
    Selects the best articles from the news results, prioritizing preferred sources.
    """
    if preferred_sources is None:
        preferred_sources = []

    all_articles = []
    if "news_results" in news_results:
        for result_block in news_results["news_results"]:
            stories = result_block.get("stories", [])
            # Handle cases where the result block itself is a story
            if "title" in result_block and not stories:
                stories = [result_block]

            if isinstance(stories, list):
                for article in stories:
                    all_articles.append({
                        "title": article.get("title"),
                        "link": article.get("link"),
                        "thumbnail": article.get("thumbnail"),
                        "source": article.get("source", {}).get("name")
                    })

    # Separate articles into preferred and others
    preferred_articles = []
    other_articles = []

    # Normalize preferred sources for comparison
    preferred_sources_lower = [src.lower() for src in preferred_sources]

    for article in all_articles:
        source_name = (article.get("source") or "").lower()
        is_preferred = any(preferred in source_name for preferred in preferred_sources_lower)

        if is_preferred:
            preferred_articles.append(article)
        else:
            other_articles.append(article)

    # Combine the lists with preferred ones first
    sorted_articles = preferred_articles + other_articles

    # Return the top 'count' articles
    return sorted_articles[:count]