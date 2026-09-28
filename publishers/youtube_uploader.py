import os
import sys
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    """Authenticates and returns the YouTube API service object."""
    token_json_env = os.getenv("YOUTUBE_TOKEN_JSON")
    token_file = Path(__file__).resolve().parent.parent / "youtube_token.json"
    client_secrets_file = Path(__file__).resolve().parent.parent / "client_secrets.json"

    creds = None

    # 1. Load from environment variable (Best for GitHub Actions)
    if token_json_env:
        try:
            token_data = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Warning: Could not parse YOUTUBE_TOKEN_JSON env var: {e}")

    # 2. Load from local file if env var was not provided
    if not creds and token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except Exception as e:
            print(f"Warning: Could not load {token_file}: {e}")

    # 3. Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save back updated token
            with open(token_file, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception as e:
            print(f"Warning: Failed to refresh YouTube token: {e}")
            creds = None

    # 4. If still no valid credentials, run local browser flow (first-time local setup)
    if not creds:
        if not client_secrets_file.exists():
            return None
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_file), SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"✅ YouTube authorization successful! Saved to {token_file}")

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube_shorts(video_path: str, title: str, description: str, tags: list = None, privacy_status: str = "public") -> dict:
    """Uploads a vertical short video to YouTube Shorts."""
    youtube = get_youtube_service()
    if not youtube:
        print("⚠️ YouTube credentials not configured. Skipping YouTube upload.")
        return {"status": "skipped", "reason": "Missing credentials"}

    # Ensure title contains #Shorts for YouTube algorithm categorization
    final_title = title if "#Shorts" in title or "#shorts" in title else f"{title} #Shorts"
    if len(final_title) > 100:
        final_title = final_title[:90] + " #Shorts"

    final_tags = tags or ["Shorts", "Viral", "Arabic"]

    body = {
        "snippet": {
            "title": final_title,
            "description": f"{description}\n\n#Shorts #Viral",
            "tags": final_tags,
            "categoryId": "22"  # People & Blogs / Entertainment
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024 * 4,
        resumable=True,
        mimetype="video/mp4"
    )

    print(f"🚀 Uploading to YouTube Shorts: '{final_title}'...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f" Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"
    print(f"✅ Video published to YouTube Shorts! URL: {video_url}")

    return {
        "status": "success",
        "platform": "youtube",
        "video_id": video_id,
        "video_url": video_url
    }

if __name__ == "__main__":
    print("Testing YouTube uploader setup...")
    svc = get_youtube_service()
    if svc:
        print("✅ YouTube Service initialized successfully!")
    else:
        print("ℹ️ YouTube credentials not set yet. Place client_secrets.json in root to authenticate.")
