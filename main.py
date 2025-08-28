# main.py (Final version with duplicate checking)

import os
import time
from news_module import search_aceh_news, select_best_articles, get_article_content
from rewriter_module import rewrite_article
from wordpress_module import create_wordpress_post, upload_image_and_get_id
from thefuzz import fuzz

HISTORY_FILE = "posted_articles.log"
SIMILARITY_THRESHOLD = 85 # Adjust this score (0-100) as needed

def load_posted_titles():
    """Loads the list of previously posted titles from the log file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        # Read lines and strip any whitespace
        return [line.strip() for line in f.readlines()]

def save_posted_title(title):
    """Saves a new title to the log file, keeping the list trimmed."""
    # Prepend the new title and keep only the last 50 entries
    titles = [title] + load_posted_titles()
    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(titles[:50]))

def is_duplicate(new_title, posted_titles):
    """Checks if a new title is too similar to any previously posted titles."""
    for posted_title in posted_titles:
        similarity_score = fuzz.ratio(new_title.lower(), posted_title.lower())
        if similarity_score > SIMILARITY_THRESHOLD:
            print(f"Duplicate found. Title '{new_title}' is {similarity_score}% similar to '{posted_title}'.")
            return True
    return False

def run_news_automation():
    print("Starting news automation process...")
    daerah_category_id = 3
    existing_tag_id = 3953
    auth = (os.getenv("WORDPRESS_USERNAME"), os.getenv("WORDPRESS_PASSWORD"))
    
    # Load the history of posted articles
    posted_titles = load_posted_titles()
    print(f"Loaded {len(posted_titles)} previously posted titles for checking.")

    print("Searching for recent news about Aceh...")
    try:
        news_results = search_aceh_news()
        selected_articles = select_best_articles(news_results)
        if not selected_articles:
            print("No new articles found in the last 3 hours. Exiting.")
            return
        print(f"Found {len(selected_articles)} potential articles.")
    except Exception as e:
        print(f"Error during news search: {e}")
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

        print(f"\nProcessing new article: {original_title}")
        
        # All processing happens only after the duplicate check passes
        featured_image_id = upload_image_and_get_id(thumbnail_url, auth)
        full_content = get_article_content(link)
        if "Could not fetch content" in full_content or not full_content:
            continue
        
        try:
            rewritten_data = rewrite_article(original_title, full_content)
            new_title = rewritten_data['title']
            new_content = rewritten_data['content']
            
            # Final duplicate check on the rewritten title
            if is_duplicate(new_title, posted_titles):
                continue

            print("Posting to WordPress...")
            post_response = create_wordpress_post(new_title, new_content, daerah_category_id, [existing_tag_id], featured_image_id)
            
            if post_response:
                # If post is successful, save the new title to our history
                save_posted_title(new_title)
                save_posted_title(original_title) # Also save original to be safe

        except Exception as e:
            print(f"Error during processing or posting: {e}")
        
        time.sleep(5)

    print("News automation process completed.")

if __name__ == "__main__":
    if not all([os.getenv("SERPAPI_KEY"), os.getenv("DEEPSEEK_API_KEY"),
                os.getenv("WORDPRESS_USERNAME"), os.getenv("WORDPRESS_PASSWORD")]):
        print("Error: Missing one or more required environment variables.")
    else:
        run_news_automation()