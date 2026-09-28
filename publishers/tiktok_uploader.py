import os
import requests
from pathlib import Path

def upload_to_tiktok(video_path: str, caption: str) -> dict:
    """
    Publishes a video to TikTok via official TikTok Content Posting API v2.
    """
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    if not access_token:
        print("⚠️ TikTok credentials (TIKTOK_ACCESS_TOKEN) not configured. Skipping TikTok upload.")
        return {"status": "skipped", "reason": "Missing credentials"}

    file_size = os.path.getsize(video_path)
    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }

    # TikTok caption length limit is usually 2200 chars
    clean_caption = caption[:2000]

    payload = {
        "post_info": {
            "title": clean_caption,
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_stitch": False,
            "disable_comment": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1
        }
    }

    print("🚀 Initializing TikTok video upload session...")
    try:
        init_res = requests.post(init_url, headers=headers, json=payload, timeout=30)
        init_data = init_res.json()

        if init_data.get("error", {}).get("code") != "ok":
            print(f"TikTok init error: {init_data}")
            return {"status": "error", "platform": "tiktok", "error": init_data}

        upload_url = init_data["data"]["upload_url"]
        publish_id = init_data["data"]["publish_id"]

        print("📤 Uploading video bytes to TikTok servers...")
        upload_headers = {
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
            "Content-Type": "video/mp4"
        }

        with open(video_path, "rb") as f:
            video_bytes = f.read()

        put_res = requests.put(upload_url, headers=upload_headers, data=video_bytes, timeout=120)
        put_res.raise_for_status()

        print(f"✅ Published to TikTok successfully! Publish ID: {publish_id}")
        return {
            "status": "success",
            "platform": "tiktok",
            "publish_id": publish_id
        }

    except Exception as e:
        print(f"TikTok upload failed with exception: {e}")
        return {"status": "error", "platform": "tiktok", "error": str(e)}

if __name__ == "__main__":
    print("TikTok Uploader module ready.")
