import os
import subprocess
from pathlib import Path
from config import VIDEO_WIDTH, VIDEO_HEIGHT, TARGET_FPS, TEMP_DIR, OUTPUT_DIR

def assemble_scenes(scene_clips: list, scene_audios: list, subtitles_path: str, output_filename: str = "final_short.mp4") -> str:
    """
    Creates individual synchronized scene segments (looping video if needed to match narration duration),
    concatenates them, and burns in the styled subtitles.
    """
    output_path = OUTPUT_DIR / output_filename
    segment_files = []

    print(f"🎬 Processing {len(scene_clips)} scene segments...")

    for i, (clip_path, audio_info) in enumerate(zip(scene_clips, scene_audios)):
        segment_path = TEMP_DIR / f"segment_{i + 1}.mp4"
        duration = audio_info["duration"]
        audio_file = audio_info["audio_path"]

        print(f" ▶️ Rendering segment {i + 1} (duration: {duration:.2f}s)...")

        # FFmpeg command per segment:
        # -stream_loop -1 allows looping short stock clips seamlessly
        # scale & crop ensures exact 1080x1920 vertical format
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-t", f"{duration:.3f}",
            "-i", clip_path,
            "-i", audio_file,
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,fps={TARGET_FPS}",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(segment_path)
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"FFmpeg error on segment {i + 1}:\n{res.stderr}")
            raise RuntimeError(f"FFmpeg segment error: {res.stderr[-500:]}")
        
        segment_files.append(str(segment_path))

    # Step 2: Write concat list file
    concat_list_file = TEMP_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for seg in segment_files:
            clean_path = Path(seg).as_posix()
            f.write(f"file '{clean_path}'\n")

    concatenated_raw = TEMP_DIR / "concatenated_raw.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(concatenated_raw)
    ]
    res_concat = subprocess.run(cmd_concat, capture_output=True, text=True)
    if res_concat.returncode != 0:
        raise RuntimeError(f"FFmpeg concat error: {res_concat.stderr[-500:]}")

    # Step 3: Burn subtitles into final output
    sub_path_escaped = Path(subtitles_path).as_posix().replace(":", "\\:")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", str(concatenated_raw),
        "-vf", f"subtitles='{sub_path_escaped}'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(output_path)
    ]
    
    print("🔥 Burning subtitles and finishing final render...")
    res_final = subprocess.run(cmd_final, capture_output=True, text=True)
    if res_final.returncode != 0:
        # If subtitle filter fails (e.g. font issue), fallback to raw concatenated video
        print(f"Subtitle burn warning: {res_final.stderr[-300:]}. Using video without burnt subtitles as fallback.")
        import shutil
        shutil.copy(str(concatenated_raw), str(output_path))

    print(f"✅ Video ready at: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    print("Assembler module ready.")
