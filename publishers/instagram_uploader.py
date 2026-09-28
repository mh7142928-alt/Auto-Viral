import os
import time
import requests
from pathlib import Path

def upload_to_instagram_reels(video_path: str, caption: str) -> dict:
    """
    Publishes a video to Instagram Reels via official Meta Graph API
    using direct resumable byte upload (no third-party hosting required).
    """
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not access_token or not account_id:
        print("⚠️ Instagram credentials (INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID) not configured. Skipping.")
        return {"status": "skipped", "reason": "Missing credentials"}

    file_size = os.path.getsize(video_path)
    base_url = f"https://graph.facebook.com/v20.0/{account_id}"

    # Step 1: Initialize Resumable Upload Session
    print("🚀 Initializing Instagram Reels container...")
    init_url = f"{base_url}/media"
    init_params = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "caption": caption,
        "access_token": access_token
    }

    init_res = requests.post(init_url, params=init_params, timeout=30)
    init_data = init_res.json()

    if "id" not in init_data or "uri" not in init_data:
        print(f"Instagram init failed: {init_data}")
        return {"status": "error", "platform": "instagram", "error": init_data}

    container_id = init_data["id"]
    upload_uri = init_data["uri"]

    # Step 2: Upload Video Bytes
    print("📤 Uploading video bytes directly to Meta servers...")
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": str(file_size)
    }

    upload_res = requests.post(upload_uri, headers=upload_headers, data=video_bytes, timeout=120)
    upload_res.raise_for_status()

    # Step 3: Wait for Meta to process the video container
    print("⏳ Waiting for Instagram video processing...")
    status_url = f"https://graph.facebook.com/v20.0/{container_id}"
    for _ in range(15):
        time.sleep(4)
        status_res = requests.get(status_url, params={"fields": "status_code", "access_token": access_token}, timeout=20)
        status_data = status_res.json()
        code = status_data.get("status_code")
        if code == "FINISHED":
            break
        elif code in ["ERROR", "EXPIRED"]:
            print(f"Instagram processing error: {status_data}")
            return {"status": "error", "platform": "instagram", "error": status_data}

    # Step 4: Publish Container
    print("📢 Publishing Reel to Instagram...")
    publish_url = f"{base_url}/media_publish"
    pub_res = requests.post(publish_url, params={"creation_id": container_id, "access_token": access_token}, timeout=30)
    pub_data = pub_res.json()

    if "id" in pub_data:
        print(f"✅ Published to Instagram Reels successfully! Media ID: {pub_data['id']}")
        return {"status": "success", "platform": "instagram", "post_id": pub_data["id"]}
    else:
        print(f"Publish failed: {pub_data}")
        return {"status": "error", "platform": "instagram", "error": pub_data}

if __name__ == "__main__":
    print("Instagram Reels Uploader module ready.")
