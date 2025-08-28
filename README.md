# newsapp
Automated News Publisher for WordPress . This is a fully automated Python application that fetches the latest news, uses an AI to rewrite the content in a journalistic style, and publishes it to a WordPress website with a featured image, category, and tag. 

## 🚀 Core Features

-   **Automated News Sourcing**: Fetches the 20 most recent news articles related to "Aceh" from Google News every two hours.
-   **Duplicate Prevention**: Keeps a log of recently posted articles and uses fuzzy logic to skip articles with similar titles, ensuring fresh content.
-   **Content Scraping**: Visits each article's URL to scrape the full text content for rewriting.
-   **AI-Powered Rewriting**: Uses the DeepSeek AI API to rewrite both the article title and content into a simple, objective journalistic style.
-   **WordPress Integration**:
    -   Uploads the article's thumbnail as a featured image.
    -   Creates a new post with the rewritten title and content.
    -   Assigns a predefined category ("Daerah") and tag.
-   **Error Handling**: Gracefully skips articles from websites that block scrapers or fail during processing.
-   **Scheduled Execution**: Designed to be run automatically by a cron job for hands-free operation.

## 🛠️ Technology Stack

-   **Backend**: Python
-   **APIs**:
    -   [SerpApi](https://serpapi.com/): For fetching Google News results.
    -   [DeepSeek AI](https://platform.deepseek.com/): For AI-powered content and title rewriting.
    -   WordPress REST API: For publishing posts, uploading media, and managing taxonomies.
-   **Key Libraries**:
    -   `requests`: For making HTTP requests to APIs and websites.
    -   `beautifulsoup4`: For parsing HTML and scraping article content.
    -   `openai`: The client library used to interact with the DeepSeek API.
    -   `thefuzz`: For fuzzy string matching to detect duplicate titles.
    -   `python-magic`: To identify file types for image uploads.
-   **Deployment**: Runs on a shared hosting environment (a2hosting) managed by a cPanel cron job.

## ⚙️ Setup and Configuration

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/your-username/automated-news-app.git](https://github.com/your-username/automated-news-app.git)
    cd automated-news-app
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `set_env.sh` file (this file is gitignored for security) and add your secret keys:
    ```bash
    #!/bin/bash
    cd /path/to/your/project/
    
    export SERPAPI_KEY="your_serpapi_key_here"
    export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
    export WORDPRESS_USERNAME="your_wp_username"
    export WORDPRESS_PASSWORD="your_wp_application_password"
    ```
    Make the script executable: `chmod +x set_env.sh`.

5.  **Run Manually**:
    ```bash
    . ./set_env.sh && python main.py
    ```

6.  **Set Up Cron Job**:
    To run the script every two hours, set up a cron job with the following command:
    ```cron
    0 */2 * * * /path/to/your/set_env.sh && /path/to/your/venv/bin/python /path/to/your/main.py >> /path/to/your/news_app.log 2>&1
    ```
