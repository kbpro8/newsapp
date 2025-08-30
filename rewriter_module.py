# rewriter_module.py (Simplified)

import os
from openai import OpenAI
import logging

# Set up a null handler for the logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

def rewrite_article(title, content, model, temperature, max_tokens, logger):
    """
    Rewrites the article and title using the DeepSeek AI model.
    Returns a dictionary with the new title and content.
    """
    logger.info(f"Rewriting article: '{title}' with model {model}")
    system_prompt = (
        "You are an expert Indonesian journalist. Your task is to rewrite a news article. "
        "You must follow these rules strictly:\n"
        "1. Rewrite the provided title and article content into standard, simple Indonesian journalistic style. Make sure to follow 5W1H formula in news writing, and make it 6-12 paragraphs at least. Include qoutes and narrations from sourcepersons. Follow the standard article writing like Harian Kompas standard.\n"
        "2. Do not add any information that is not in the original text. Your output must be 100% factual based on the source.\n"
        "3. Please mention the source of the article at the end of the article.\n"
        "4. Your final output must be in a specific format: a rewritten title on the first line, followed by '|||', and then the rewritten article content which must start with 'Acehjurnal.com - '."
    )
    user_prompt = f"Original Title: {title}\n\nOriginal Content:\n{content}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        full_response = response.choices[0].message.content

        parts = full_response.split('|||', 1)
        if len(parts) == 2:
            new_title = parts[0].strip()
            new_content = parts[1].strip()
            logger.info("Successfully rewritten article.")
            return {"title": new_title, "content": new_content}
        else:
            logger.warning("AI response did not follow the expected 'title|||content' format. Using fallback.")
            # Fallback if the model doesn't follow the format
            return {"title": title, "content": full_response}
    except Exception as e:
        logger.error(f"Error during AI rewriting: {e}", exc_info=True)
        # In case of an API error, return the original content to avoid crashing
        return {"title": title, "content": content}