# wordpress_module.py (Final Cleaned Version)

import requests
import json
import os
import tempfile
import magic

WORDPRESS_URL = "https://acehjurnal.com/wp-json/wp/v2"
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")

def upload_image_and_get_id(image_url, auth):
    if not image_url: return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        image_response = requests.get(image_url, headers=headers, stream=True, timeout=15)
        image_response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image_response.iter_content(chunk_size=8192): tmp.write(chunk)
            tmp_path = tmp.name
        mime_type = magic.from_file(tmp_path, mime=True)
        if not mime_type.startswith('image/'):
            os.remove(tmp_path)
            return None
        filename = os.path.basename(image_url).split('?')[0] or "featured_image.jpg"
        with open(tmp_path, 'rb') as f:
            headers = {'Content-Disposition': f'attachment; filename={filename}', 'Content-Type': mime_type}
            upload_response = requests.post(f"{WORDPRESS_URL}/media", headers=headers, auth=auth, data=f)
            upload_response.raise_for_status()
        os.remove(tmp_path)
        return upload_response.json()['id']
    except requests.exceptions.RequestException as e:
        print(f"Error handling image {image_url}: {e}")
        if 'tmp_path' in locals() and os.path.exists(tmp_path): os.remove(tmp_path)
        return None

def create_wordpress_post(title, content, category_id, tag_ids_list, featured_image_id=None):
    auth = (WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
    headers = {"Content-Type": "application/json"}
    data = {
        "title": title, "content": content, "status": "publish",
        "categories": [category_id], "tags": tag_ids_list
    }
    if featured_image_id:
        data["featured_media"] = featured_image_id
    try:
        response = requests.post(f"{WORDPRESS_URL}/posts", headers=headers, auth=auth, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully created post: {response.json().get('link')}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating WordPress post: {e}")
        if e.response.status_code == 400:
            print(f"WordPress Response: {e.response.json()}")
        return None