NewsApp
This application automates the process of fetching, rewriting, and publishing news articles to a WordPress website. It is designed to be a "set it and forget it" script that periodically finds relevant news, rewrites it to be unique, and posts it to your site.

Core Features
Configurable: All major settings are managed in the config.ini file for easy tweaking.
Structured Logging: All actions are logged to app.log for easy monitoring and debugging.
High-Quality Content Scraping: Uses the trafilatura library to accurately extract the main article content, avoiding ads and boilerplate.
Smart Article Selection: Prioritizes news from a preferred list of sources that you define.
Duplicate Prevention: Keeps a log of recently posted articles to avoid publishing similar content.
Installation Guide
Follow these steps to get the application running on your local machine or server.

1. Prerequisites
Python 3.8 or higher
Access to a WordPress site with administrator privileges
2. Clone the Repository
First, clone the repository to your local machine.

git clone <your-repository-url>
cd <repository-directory>
3. Set Up a Virtual Environment
It is highly recommended to use a Python virtual environment to manage dependencies and avoid conflicts.

# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
4. Install Dependencies
Install all the required Python libraries using the requirements.txt file.

pip install -r requirements.txt
Configuration
The application requires you to set up API keys (via environment variables) and configure the application's behavior (via config.ini).

1. Set Environment Variables
The application needs the following secret keys to run. The most secure way to manage them is by setting them as environment variables in your system.

SERPAPI_KEY: Your API key for SerpApi (for Google News searches).
DEEPSEEK_API_KEY: Your API key for DeepSeek AI (for rewriting content).
WORDPRESS_USERNAME: Your WordPress username.
WORDPRESS_PASSWORD: An Application Password for your WordPress user.
Important: Do not use your main password. WordPress allows you to generate secure, revocable "Application Passwords" for this purpose. You can create one in your WordPress admin panel under Users > Profile > Application Passwords.
2. Configure config.ini
This file controls the main behavior of the application. You can edit it directly.

[main]: Controls core logic like the duplicate checking threshold.
[wordpress]: Set your WordPress site URL and the default category/tag IDs for new posts.
[news_api]: Define the news search query, how many results to fetch, and your list of preferred_sources.
[ai_rewriter]: Tweak the AI model parameters.
[logging]: Controls the log file name and log level.
Running the Application
Once you have completed the installation and configuration, you can run the script with a single command:

python main.py
The script will start the automation process. You can view its progress in your console and review the detailed output in the app.log file.


