import requests
from pathlib import Path
from config import PEXELS_API_KEY, TEMP_DIR

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"

def search_and_download_video(query: str, output_path: str, min_duration: int = 4) -> str:
    """
    Searches Pexels for portrait video clips matching the query and downloads the best HD vertical video.
    """
    if not PEXELS_API_KEY:
        raise ValueError("PEXELS_API_KEY is missing! Please set it in your .env file.")

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": "portrait",
        "per_page": 6
    }

    response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    videos = data.get("videos", [])
    if not videos:
        # Fallback to general search if portrait yields nothing
        params.pop("orientation", None)
        response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30)
        data = response.json()
        videos = data.get("videos", [])

    if not videos:
        # Ultimate fallback
        params["query"] = "cinematic mystery dark background"
        response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30)
        data = response.json()
        videos = data.get("videos", [])

    if not videos:
        raise RuntimeError(f"No videos found on Pexels for query: {query}")

    # Pick the best vertical video file
    selected_download_url = None
    for vid in videos:
        # Check files
        files = vid.get("video_files", [])
        # Prefer HD vertical 1080x1920
        hd_portrait = [f for f in files if f.get("quality") == "hd" and f.get("width", 0) <= f.get("height", 0)]
        if hd_portrait:
            selected_download_url = hd_portrait[0]["link"]
            break
        # Fallback to any HD
        hd_files = [f for f in files if f.get("quality") == "hd"]
        if hd_files:
            selected_download_url = hd_files[0]["link"]
            break
        # Fallback to first available mp4
        if files:
            selected_download_url = files[0]["link"]
            break

    if not selected_download_url:
        raise RuntimeError("No suitable video stream link found in Pexels results.")

    # Download video file
    with requests.get(selected_download_url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return output_path

def fetch_scene_videos(scenes: list) -> list:
    """Downloads one video for each scene in the scenes list."""
    downloaded_paths = []
    for idx, scene in enumerate(scenes):
        query = scene.get("search_query", "cinematic nature")
        out_path = str(TEMP_DIR / f"scene_{idx + 1}.mp4")
        print(f"Downloading video for scene {idx + 1}: '{query}'...")
        try:
            download_file = search_and_download_video(query, out_path)
            downloaded_paths.append(download_file)
        except Exception as e:
            print(f"Warning: Failed to fetch for query '{query}': {e}. Using fallback...")
            fallback_file = search_and_download_video("cinematic abstract", out_path)
            downloaded_paths.append(fallback_file)

    return downloaded_paths

if __name__ == "__main__":
    print("Testing Pexels fetcher...")
    try:
        path = search_and_download_video("deep space galaxy", str(TEMP_DIR / "test_space.mp4"))
        print(f"Successfully downloaded test video to: {path}")
    except Exception as e:
        print(f"Pexels Test Error: {e}")
