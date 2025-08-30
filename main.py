# main.py (Final version with duplicate checking)

import os
import time
import configparser
import logging
from news_module import search_aceh_news, select_best_articles, get_article_content
from rewriter_module import rewrite_article
from wordpress_module import create_wordpress_post, upload_image_and_get_id
from thefuzz import fuzz

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

def is_duplicate(new_title, posted_titles):
    """Checks if a new title is too similar to any previously posted titles."""
    for posted_title in posted_titles:
        similarity_score = fuzz.ratio(new_title.lower(), posted_title.lower())
        if similarity_score > SIMILARITY_THRESHOLD:
            logger.warning(f"Duplicate found. Title '{new_title}' is {similarity_score}% similar to '{posted_title}'.")
            return True
    return False

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

        # Check for duplicates before doing any processing
        if is_duplicate(original_title, posted_titles):
            continue

        logger.info(f"Processing new article: {original_title}")
        
        # All processing happens only after the duplicate check passes
        featured_image_id = upload_image_and_get_id(thumbnail_url, auth, wordpress_url, logger)
        full_content = get_article_content(link, logger)
        if "Could not fetch content" in full_content or not full_content:
            logger.warning(f"Could not fetch content for article: {original_title}")
            continue
        
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
            
            # Final duplicate check on the rewritten title
            if is_duplicate(new_title, posted_titles):
                continue

            logger.info("Posting to WordPress...")
            post_response = create_wordpress_post(
                new_title, new_content, daerah_category_id,
                [existing_tag_id], featured_image_id, auth, wordpress_url, logger
            )
            
            if post_response:
                # If post is successful, save the new title to our history
                save_posted_title(new_title)
                save_posted_title(original_title) # Also save original to be safe

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