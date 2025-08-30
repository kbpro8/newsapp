# wordpress_module.py (Final Cleaned Version)

import requests
import json
import os
import tempfile
import magic
import logging

# Set up a null handler for the logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

def upload_image_and_get_id(image_url, auth, wordpress_url, logger):
    if not image_url:
        return None
    logger.info(f"Uploading image from URL: {image_url}")
    tmp_path = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        image_response = requests.get(image_url, headers=headers, stream=True, timeout=15)
        image_response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image_response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp_path = tmp.name

        mime_type = magic.from_file(tmp_path, mime=True)
        if not mime_type.startswith('image/'):
            logger.warning(f"Downloaded file from {image_url} is not an image (MIME: {mime_type}). Skipping.")
            os.remove(tmp_path)
            return None

        filename = os.path.basename(image_url).split('?')[0] or "featured_image.jpg"

        with open(tmp_path, 'rb') as f:
            headers = {'Content-Disposition': f'attachment; filename={filename}', 'Content-Type': mime_type}
            upload_response = requests.post(f"{wordpress_url}/media", headers=headers, auth=auth, data=f)
            upload_response.raise_for_status()

        media_id = upload_response.json()['id']
        logger.info(f"Successfully uploaded image. Media ID: {media_id}")
        return media_id
    except requests.exceptions.RequestException as e:
        logger.error(f"Error handling image {image_url}: {e}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

def create_wordpress_post(title, content, category_id, tag_ids_list, featured_image_id, auth, wordpress_url, logger):
    logger.info(f"Creating WordPress post titled: '{title}'")
    headers = {"Content-Type": "application/json"}
    data = {
        "title": title, "content": content, "status": "publish",
        "categories": [category_id], "tags": tag_ids_list
    }
    if featured_image_id:
        data["featured_media"] = featured_image_id

    try:
        response = requests.post(f"{wordpress_url}/posts", headers=headers, auth=auth, data=json.dumps(data))
        response.raise_for_status()
        post_link = response.json().get('link')
        logger.info(f"Successfully created post: {post_link}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating WordPress post: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"WordPress Response (Status {e.response.status_code}): {e.response.text}")
        return None