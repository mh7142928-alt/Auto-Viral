import os
import json
from datetime import datetime
from pathlib import Path

from .youtube_uploader import upload_to_youtube_shorts
from .instagram_uploader import upload_to_instagram_reels
from .tiktok_uploader import upload_to_tiktok
from config import OUTPUT_DIR

def publish_to_all_platforms(video_path: str, title: str, caption: str) -> dict:
    """
    Attempts to publish the final video to all 3 platforms:
    - YouTube Shorts
    - Instagram Reels
    - TikTok
    Logs results and continues even if one platform is not yet configured.
    """
    print("\n" + "=" * 65)
    print("🌐 Starting Automated Multi-Platform Publishing")
    print(f"📁 Video: {video_path}")
    print("=" * 65)

    results = {
        "timestamp": datetime.now().isoformat(),
        "video_path": str(video_path),
        "platforms": {}
    }

    # 1. YouTube Shorts
    print("\n[1/3] 🔴 Publishing to YouTube Shorts...")
    try:
        results["platforms"]["youtube"] = upload_to_youtube_shorts(
            video_path=video_path,
            title=title,
            description=caption
        )
    except Exception as e:
        print(f"YouTube exception: {e}")
        results["platforms"]["youtube"] = {"status": "error", "error": str(e)}

    # 2. Instagram Reels
    print("\n[2/3] 📸 Publishing to Instagram Reels...")
    try:
        results["platforms"]["instagram"] = upload_to_instagram_reels(
            video_path=video_path,
            caption=caption
        )
    except Exception as e:
        print(f"Instagram exception: {e}")
        results["platforms"]["instagram"] = {"status": "error", "error": str(e)}

    # 3. TikTok
    print("\n[3/3] 🎵 Publishing to TikTok...")
    try:
        results["platforms"]["tiktok"] = upload_to_tiktok(
            video_path=video_path,
            caption=caption
        )
    except Exception as e:
        print(f"TikTok exception: {e}")
        results["platforms"]["tiktok"] = {"status": "error", "error": str(e)}

    # Summary
    print("\n" + "=" * 65)
    print("📊 Multi-Platform Publishing Summary:")
    for platform, res in results["platforms"].items():
        status = res.get("status", "unknown")
        icon = "✅" if status == "success" else ("⚠️" if status == "skipped" else "❌")
        print(f"  {icon} {platform.upper()}: {status.upper()}")
    print("=" * 65)

    # Save to history log
    log_file = OUTPUT_DIR / "publishing_history.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(results, ensure_ascii=False) + "\n")

    return results

if __name__ == "__main__":
    print("Multi-Publisher module ready.")
