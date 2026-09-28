import sys
import json
from datetime import datetime
from pathlib import Path

from brain import generate_script
from tts import generate_scene_audios
from subtitles import build_scene_subtitles
from pexels import fetch_scene_videos
from video_assembler import assemble_scenes
from config import OUTPUT_DIR, TEMP_DIR

def run_pipeline(custom_topic: str = None) -> dict:
    """Executes the complete video creation pipeline."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 60)
    print(f"🎬 Starting Automated Video Generation Pipeline [{timestamp}]")
    print("=" * 60)

    # 1. Brain & Script Generation
    print("\n🧠 Step 1: Generating Script with Gemini Flash...")
    script_data = generate_script(topic=custom_topic)
    print(f"📌 Title: {script_data['title']}")
    print(f"📝 Topic: {script_data.get('topic', 'General')}")
    print(f"📜 Scenes to produce: {len(script_data['scenes'])}")

    # 2. Voiceover per Scene
    print("\n🎙️ Step 2: Generating Natural Voiceover per scene...")
    scene_audios = generate_scene_audios(script_data["scenes"], session_id=timestamp)
    total_duration = sum(item["duration"] for item in scene_audios)
    print(f"⏱️ Total Video Duration: {total_duration:.1f} seconds")

    # 3. Synchronized Subtitles
    print("\n🎨 Step 3: Formatting & Synchronizing Subtitles...")
    ass_path = str(TEMP_DIR / f"subtitles_{timestamp}.ass")
    build_scene_subtitles(scene_audios, ass_path)
    print(f"✅ Subtitles generated: {ass_path}")

    # 4. Fetching B-Roll from Pexels
    print("\n🎥 Step 4: Fetching Vertical HD Video Clips from Pexels...")
    scene_clips = fetch_scene_videos(script_data["scenes"])
    print(f"✅ Downloaded {len(scene_clips)} clips.")

    # 5. Video Assembly & Subtitle Burn
    print("\n🎞️ Step 5: Assembling Video and Burning Captions with FFmpeg...")
    final_filename = f"short_{timestamp}.mp4"
    final_video_path = assemble_scenes(
        scene_clips=scene_clips,
        scene_audios=scene_audios,
        subtitles_path=ass_path,
        output_filename=final_filename
    )

    # Save metadata JSON for social media posting
    metadata_path = OUTPUT_DIR / f"metadata_{timestamp}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"🎉 Short Video Successfully Generated!")
    print(f"📁 Video File: {final_video_path}")
    print(f"📄 Metadata: {metadata_path}")
    print("=" * 60)

    return {
        "video_path": final_video_path,
        "metadata_path": str(metadata_path),
        "title": script_data["title"],
        "caption": script_data["caption"]
    }

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(custom_topic=topic)
