# main.py (Final version with duplicate checking)

import os
import time
import configparser
import logging
from news_module import search_aceh_news, select_best_articles, get_article_content
from rewriter_module import rewrite_article
from wordpress_module import create_wordpress_post, upload_image_and_get_id, get_existing_wordpress_posts
from thefuzz import fuzz
import hashlib
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup

def setup_logger(log_file, log_level):
    """Sets up the application logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Setup logger
log_config = config['logging']
logger = setup_logger(log_config.get('log_file'), log_config.get('log_level'))

HISTORY_FILE = config.get('main', 'history_file')
SIMILARITY_THRESHOLD = config.getint('main', 'similarity_threshold')
CONTENT_SIMILARITY_THRESHOLD = config.getint('main', 'content_similarity_threshold', fallback=80)
WORD_OVERLAP_THRESHOLD = config.getfloat('main', 'word_overlap_threshold', fallback=0.7)
WORDPRESS_CHECK_DAYS = config.getint('main', 'wordpress_check_days', fallback=7)
URL_HISTORY_FILE = config.get('main', 'history_file').replace('.log', '_urls.json')

def load_posted_titles():
    """Loads the list of previously posted titles from the log file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_posted_title(title):
    """Saves a new title to the log file, keeping the list trimmed."""
    titles = [title] + load_posted_titles()
    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(titles[:50]))
    logger.info(f"Saved title to history: {title}")

def clean_text_for_comparison(text):
    """Cleans text for better comparison by removing HTML, extra spaces, and normalizing."""
    if not text:
        return ""
    
    # Remove HTML tags if present
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Normalize whitespace and remove extra characters
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    
    return text.lower()

def calculate_content_hash(content):
    """Generates a hash for content comparison."""
    cleaned_content = clean_text_for_comparison(content)
    return hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()

def load_url_history():
    """Loads the URL history from JSON file."""
    if not os.path.exists(URL_HISTORY_FILE):
        return {}
    try:
        with open(URL_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_url_history(url_history):
    """Saves URL history to JSON file."""
    try:
        with open(URL_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(url_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving URL history: {e}")

def is_url_processed(url, url_history):
    """Checks if a URL has already been processed."""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return url_hash in url_history

def save_processed_url(url, title, url_history):
    """Saves a processed URL with metadata."""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    url_history[url_hash] = {
        'url': url,
        'title': title,
        'processed_date': datetime.now().isoformat()
    }
    save_url_history(url_history)

def advanced_similarity_check(new_title, new_content, comparison_data):
    """
    Advanced similarity checking using multiple methods.
    comparison_data should be a list of dicts with 'title' and 'content' keys.
    """
    new_title_clean = clean_text_for_comparison(new_title)
    new_content_clean = clean_text_for_comparison(new_content)
    new_content_hash = calculate_content_hash(new_content)
    
    for item in comparison_data:
        existing_title = item.get('title', '')
        existing_content = item.get('content', '')
        
        if not existing_title and not existing_content:
            continue
        
        existing_title_clean = clean_text_for_comparison(existing_title)
        existing_content_clean = clean_text_for_comparison(existing_content)
        
        # Method 1: Title similarity using multiple algorithms
        title_ratio = fuzz.ratio(new_title_clean, existing_title_clean)
        title_partial_ratio = fuzz.partial_ratio(new_title_clean, existing_title_clean)
        title_token_sort_ratio = fuzz.token_sort_ratio(new_title_clean, existing_title_clean)
        
        # Use the highest similarity score
        max_title_similarity = max(title_ratio, title_partial_ratio, title_token_sort_ratio)
        
        if max_title_similarity > SIMILARITY_THRESHOLD:
            logger.warning(f"Title similarity detected: '{new_title}' vs '{existing_title}' (Score: {max_title_similarity}%)")
            return True, f"Title similarity: {max_title_similarity}%"
        
        # Method 2: Content hash comparison (exact content match)
        existing_content_hash = calculate_content_hash(existing_content)
        if new_content_hash == existing_content_hash and new_content_hash != hashlib.md5(''.encode()).hexdigest():
            logger.warning(f"Exact content match found with existing post: '{existing_title}'")
            return True, "Exact content match"
        
        # Method 3: Content similarity for substantial overlap
        if len(new_content_clean) > 100 and len(existing_content_clean) > 100:  # Only for substantial content
            content_similarity = fuzz.ratio(new_content_clean[:500], existing_content_clean[:500])  # First 500 chars
            if content_similarity > CONTENT_SIMILARITY_THRESHOLD:
                logger.warning(f"High content similarity: {content_similarity}% with '{existing_title}'")
                return True, f"Content similarity: {content_similarity}%"
        
        # Method 4: Key phrase extraction and comparison
        new_words = set(new_title_clean.split())
        existing_words = set(existing_title_clean.split())
        
        if len(new_words) > 0 and len(existing_words) > 0:
            word_overlap = len(new_words.intersection(existing_words)) / len(new_words.union(existing_words))
            if word_overlap > WORD_OVERLAP_THRESHOLD:
                logger.warning(f"High word overlap: {word_overlap:.2%} with '{existing_title}'")
                return True, f"Word overlap: {word_overlap:.2%}"
    
    return False, "No duplicates found"

def is_duplicate(new_title, posted_titles):
    """Legacy function maintained for backward compatibility."""
    comparison_data = [{'title': title, 'content': ''} for title in posted_titles]
    is_dup, reason = advanced_similarity_check(new_title, '', comparison_data)
    return is_dup

def run_news_automation():
    logger.info("Starting news automation process...")
    # WordPress settings from config
    wp_config = config['wordpress']
    daerah_category_id = wp_config.getint('daerah_category_id')
    existing_tag_id = wp_config.getint('existing_tag_id')
    wordpress_url = wp_config.get('url')

    # News API settings from config
    news_api_config = config['news_api']
    news_query = news_api_config.get('query')
    num_results = news_api_config.getint('num_results')
    select_count = news_api_config.getint('select_count')
    preferred_sources_str = news_api_config.get('preferred_sources', '')
    preferred_sources = [source.strip() for source in preferred_sources_str.split(',') if source.strip()]

    # AI Rewriter settings from config
    rewriter_config = config['ai_rewriter']

    auth = (os.getenv("WORDPRESS_USERNAME"), os.getenv("WORDPRESS_PASSWORD"))
    
    # Load the history of posted articles
    posted_titles = load_posted_titles()
    logger.info(f"Loaded {len(posted_titles)} previously posted titles for checking.")
    
    # Load URL history
    url_history = load_url_history()
    logger.info(f"Loaded {len(url_history)} processed URLs for checking.")
    
    # Fetch recent WordPress posts for comprehensive duplicate checking
    existing_wp_posts = get_existing_wordpress_posts(auth, wordpress_url, logger, days_back=WORDPRESS_CHECK_DAYS)
    logger.info(f"Retrieved {len(existing_wp_posts)} recent WordPress posts for duplicate checking.")

    logger.info(f"Searching for recent news about '{news_query}'...")
    try:
        news_results = search_aceh_news(news_query, num_results, logger)
        selected_articles = select_best_articles(news_results, select_count, preferred_sources)
        if not selected_articles:
            logger.info("No new articles found. Exiting.")
            return
        logger.info(f"Found {len(selected_articles)} potential articles.")
    except Exception as e:
        logger.error(f"Error during news search: {e}", exc_info=True)
        return

    for i, article in enumerate(selected_articles):
        original_title = article.get("title")
        link = article.get("link")
        thumbnail_url = article.get("thumbnail")

        if not original_title or not link:
            continue

        # Step 1: Check if URL has already been processed
        if is_url_processed(link, url_history):
            logger.info(f"URL already processed, skipping: {link}")
            continue

        # Step 2: Check for duplicates against local history
        if is_duplicate(original_title, posted_titles):
            logger.info(f"Local duplicate detected, skipping: {original_title}")
            continue

        logger.info(f"Processing new article: {original_title}")
        
        # Get full content early for comprehensive duplicate checking
        full_content = get_article_content(link, logger)
        if "Could not fetch content" in full_content or not full_content:
            logger.warning(f"Could not fetch content for article: {original_title}")
            continue

        # Step 3: Advanced duplicate checking against WordPress posts
        all_comparison_data = existing_wp_posts + [{'title': title, 'content': ''} for title in posted_titles]
        is_dup, reason = advanced_similarity_check(original_title, full_content, all_comparison_data)
        
        if is_dup:
            logger.info(f"Advanced duplicate detected ({reason}), skipping: {original_title}")
            # Still save URL to prevent reprocessing
            save_processed_url(link, original_title, url_history)
            continue

        # All processing happens only after all duplicate checks pass
        featured_image_id = upload_image_and_get_id(thumbnail_url, auth, wordpress_url, logger)
        
        try:
            rewritten_data = rewrite_article(
                original_title,
                full_content,
                model=rewriter_config.get('model'),
                temperature=rewriter_config.getfloat('temperature'),
                max_tokens=rewriter_config.getint('max_tokens'),
                logger=logger
            )
            new_title = rewritten_data['title']
            new_content = rewritten_data['content']
            
            # Step 4: Final duplicate check on the rewritten content
            is_dup_rewritten, reason_rewritten = advanced_similarity_check(new_title, new_content, all_comparison_data)
            if is_dup_rewritten:
                logger.info(f"Rewritten content duplicate detected ({reason_rewritten}), skipping: {new_title}")
                save_processed_url(link, original_title, url_history)
                continue

            logger.info("Posting to WordPress...")
            post_response = create_wordpress_post(
                new_title, new_content, daerah_category_id,
                [existing_tag_id], featured_image_id, auth, wordpress_url, logger
            )
            
            if post_response:
                # If post is successful, save to all tracking systems
                save_posted_title(new_title)
                save_posted_title(original_title)
                save_processed_url(link, original_title, url_history)
                logger.info(f"Successfully posted and tracked: {new_title}")

        except Exception as e:
            logger.error(f"Error during processing or posting for article '{original_title}': {e}", exc_info=True)
        
        time.sleep(5)

    logger.info("News automation process completed.")

if __name__ == "__main__":
    if not all([os.getenv("SERPAPI_KEY"), os.getenv("DEEPSEEK_API_KEY"),
                os.getenv("WORDPRESS_USERNAME"), os.getenv("WORDPRESS_PASSWORD")]):
        # Logger might not be initialized, so use print for this critical startup error
        print("CRITICAL: Missing one or more required environment variables (SERPAPI_KEY, DEEPSEEK_API_KEY, WORDPRESS_USERNAME, WORDPRESS_PASSWORD).")
    else:
        run_news_automation()
