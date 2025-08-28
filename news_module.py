# news_module.py (Updated for recent articles)

import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_article_content(url):
    # ... (This function remains the same)
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs])
        return content if content else "Could not extract content."
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content: {e}")
        return "Could not fetch content due to an error."

def search_aceh_news(query="Berita Aceh", num_results=20):
    """Searches for news articles published in the last 3 hours."""
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_news", "q": query, "api_key": SERPAPI_KEY,
        "num": num_results, "hl": "id", "gl": "id",
        "tbs": "qdr:h3"  # ADDED: Time filter for the last 3 hours
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def select_best_articles(news_results, count=10):
    # ... (This function remains the same)
    articles = []
    if "news_results" in news_results:
        for result_block in news_results["news_results"]:
            if "stories" in result_block and isinstance(result_block["stories"], list):
                for article in result_block["stories"]:
                    articles.append({"title": article.get("title"), "link": article.get("link"), "thumbnail": article.get("thumbnail")})
                    if len(articles) >= count: return articles
            elif "title" in result_block:
                articles.append({"title": result_block.get("title"), "link": result_block.get("link"), "thumbnail": result_block.get("thumbnail")})
                if len(articles) >= count: return articles
    return articles