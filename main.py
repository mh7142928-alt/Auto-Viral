import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from series_manager import load_state, advance_episode
from story_brain import generate_episode_script
from tts import generate_scene_audios
from subtitles import build_scene_subtitles
from image_generator import generate_scenes_images
from video_assembler import assemble_scenes
from config import OUTPUT_DIR, TEMP_DIR

def run_series_pipeline(series_key: str) -> dict:
    """Executes the full pipeline for an episodic series (fruits or animals)."""
    state = load_state()
    if series_key not in state:
        raise ValueError(f"Unknown series key: {series_key}. Must be 'fruits' or 'animals'.")

    series_info = state[series_key]
    current_ep = series_info["current_episode"]
    total_eps = series_info["total_episodes"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"{series_key}_ep{current_ep}_{timestamp}"

    print("=" * 65)
    print(f"🎬 Producing: {series_info['series_title']}")
    print(f"📺 Episode: {current_ep} of {total_eps} | Universe: {series_key.upper()}")
    print("=" * 65)

    # 1. Script Generation
    print("\n🧠 Step 1: Writing dramatic episode script with Gemini...")
    episode_data = generate_episode_script(series_info)
    print(f"📌 Episode Title: {episode_data['episode_title']}")
    print(f"📜 Scenes to animate: {len(episode_data['scenes'])}")

    # 2. Voiceover Generation
    print("\n🎙️ Step 2: Generating storytelling voiceover per scene (Edge-TTS)...")
    scene_audios = generate_scene_audios(episode_data["scenes"], session_id=session_id)
    total_duration = sum(item["duration"] for item in scene_audios)
    print(f"⏱️ Episode Duration: {total_duration:.1f} seconds")

    # 3. Subtitles Generation
    print("\n🎨 Step 3: Generating synchronized dramatic subtitles (ASS)...")
    ass_path = str(TEMP_DIR / f"{session_id}_subtitles.ass")
    build_scene_subtitles(scene_audios, ass_path)

    # 4. Generate 3D Character Scene Images
    print("\n🖼️ Step 4: Generating consistent 3D character images...")
    media_files = generate_scenes_images(
        episode_data["scenes"],
        session_prefix=session_id,
        fixed_seed=42 + current_ep * 11
    )

    # 5. Video Assembly & Motion Render
    print("\n🎞️ Step 5: Assembling video with Ken Burns motion & burning subtitles...")
    final_filename = f"{series_key}_ep_{current_ep:02d}_{timestamp}.mp4"
    final_video_path = assemble_scenes(
        scene_media_files=media_files,
        scene_audios=scene_audios,
        subtitles_path=ass_path,
        output_filename=final_filename
    )

    # Save metadata for posting
    metadata_path = OUTPUT_DIR / f"{series_key}_ep_{current_ep:02d}_{timestamp}_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "series_key": series_key,
            "series_title": series_info["series_title"],
            "episode_number": current_ep,
            "total_episodes": total_eps,
            "episode_title": episode_data["episode_title"],
            "caption": episode_data["caption"],
            "video_file": final_filename,
            "created_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

    # Advance episode memory in state
    summary = episode_data.get("episode_summary_for_memory", episode_data["episode_title"])
    advance_episode(series_key, summary)

    print("\n" + "=" * 65)
    print(f"🎉 Episode {current_ep} Successfully Created!")
    print(f"📁 Video Path: {final_video_path}")
    print(f"📄 Metadata: {metadata_path}")
    print("=" * 65)

    return {
        "video_path": final_video_path,
        "metadata_path": str(metadata_path),
        "title": episode_data["episode_title"],
        "caption": episode_data["caption"]
    }

def main():
    parser = argparse.ArgumentParser(description="Automated Shorts & Series Generator")
    parser.add_argument("--series", choices=["fruits", "animals", "auto"], default="auto",
                        help="Choose which dramatic series to advance (fruits or animals)")
    args = parser.parse_args()

    series_to_run = args.series
    if series_to_run == "auto":
        # If morning/afternoon (hour < 16), run fruits; if evening/night, run animals
        current_hour = datetime.now().hour
        series_to_run = "fruits" if current_hour < 16 else "animals"
        print(f"⏰ Auto-schedule detected: Running '{series_to_run}' series for current hour ({current_hour}:00).")

    run_series_pipeline(series_to_run)

if __name__ == "__main__":
    main()
