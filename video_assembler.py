import os
import subprocess
from pathlib import Path
from config import VIDEO_WIDTH, VIDEO_HEIGHT, TARGET_FPS, TEMP_DIR, OUTPUT_DIR

def is_image_file(path_str: str) -> bool:
    """Checks if the file is an image based on extension."""
    return Path(path_str).suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]

def assemble_scenes(scene_media_files: list, scene_audios: list, subtitles_path: str, output_filename: str = "final_episode.mp4") -> str:
    """
    Renders synchronized scene segments for either images (via dynamic Ken Burns zoompan)
    or video clips, concatenates them and burns in styled subtitles.
    """
    output_path = OUTPUT_DIR / output_filename
    segment_files = []

    print(f"🎬 Processing {len(scene_media_files)} scene segments...")

    for i, (media_path, audio_info) in enumerate(zip(scene_media_files, scene_audios)):
        segment_path = TEMP_DIR / f"segment_{i + 1}.mp4"
        duration = audio_info["duration"]
        audio_file = audio_info["audio_path"]
        num_frames = int(round(duration * TARGET_FPS))

        print(f" ▶️ Rendering segment {i + 1} (duration: {duration:.2f}s)...")

        if is_image_file(media_path):
            # Dynamic Ken Burns camera zoom for 3D character images
            vf_filter = (
                f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},"
                f"zoompan=z='min(zoom+0.0012,1.20)':d={num_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={TARGET_FPS}"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", media_path,
                "-i", audio_file,
                "-vf", vf_filter,
                "-t", f"{duration:.3f}",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                str(segment_path)
            ]
        else:
            # Video clip trimming and looping
            vf_filter = f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,fps={TARGET_FPS}"
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-t", f"{duration:.3f}",
                "-i", media_path,
                "-i", audio_file,
                "-vf", vf_filter,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(segment_path)
            ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"FFmpeg segment {i + 1} error: {res.stderr[-400:]}")
            raise RuntimeError(f"FFmpeg error: {res.stderr[-300:]}")

        segment_files.append(str(segment_path))

    # Step 2: Concat list
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
        raise RuntimeError(f"FFmpeg concat error: {res_concat.stderr[-400:]}")

    # Step 3: Burn subtitles into final output
    sub_path_escaped = Path(subtitles_path).as_posix().replace(":", "\\:")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", str(concatenated_raw),
        "-vf", f"subtitles='{sub_path_escaped}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(output_path)
    ]

    print("🔥 Burning subtitles and finishing final render...")
    res_final = subprocess.run(cmd_final, capture_output=True, text=True)
    if res_final.returncode != 0:
        print(f"Subtitle burn warning, using raw video: {res_final.stderr[-200:]}")
        import shutil
        shutil.copy(str(concatenated_raw), str(output_path))

    print(f"✅ Episode successfully rendered: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    print("Video assembler module ready.")
