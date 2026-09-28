import os
import sys
import subprocess
from pathlib import Path
from tts import generate_scene_audios
from subtitles import build_scene_subtitles
from config import OUTPUT_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, TARGET_FPS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCENES_DATA = [
    {
        "image_file": str(TEMP_DIR / "kareem_scene_1.jpg"),
        "narration": "في ليلة شديدة البرودة، كان الطفل الصغير كريم يقف وحيداً يبيع الورد ليشتري دواءً لأمه المريضة، ولا أحد يشعر به."
    },
    {
        "image_file": str(TEMP_DIR / "kareem_scene_2.jpg"),
        "narration": "وفجأة، مرت سيدة أنيقة مسرعة، فسقط منها هذا الصندوق الأثري الغريب في بركة الماء واختفت بين الزحام كأنها سراب!"
    },
    {
        "image_file": str(TEMP_DIR / "kareem_scene_3.jpg"),
        "narration": "وعندما فتحه كريم ليرى ما بداخله... حدث ما لم يتوقعه أي إنسان وتوهج نور سحري صدمه بالكامل! تابع الجزء الثاني لتعرف ماذا وجد كريم!"
    }
]

def make_story_video():
    print("=" * 60)
    print("🎬 إنتاج الحلقة الأولى: قصة كريم والصندوق الغامض (الجزء 1)")
    print("=" * 60)

    # 1. Voiceover
    print("\n🎙️ 1. توليد الصوت العاطفي والمؤثر...")
    scene_audios = generate_scene_audios(SCENES_DATA, session_id="kareem_ep1")
    total_duration = sum(item["duration"] for item in scene_audios)
    print(f"⏱️ مدة الحلقة: {total_duration:.2f} ثانية")

    # 2. Subtitles
    print("\n🎨 2. إنشاء وتنسيق الترجمة الدرامية...")
    ass_path = str(TEMP_DIR / "kareem_subtitles.ass")
    build_scene_subtitles(scene_audios, ass_path)

    # 3. Create Ken Burns animated video for each scene
    print("\n🎥 3. تطبيق التحريك السينمائي (Ken Burns Effect) على صور الشخصية...")
    segment_files = []
    for i, (scene, audio_info) in enumerate(zip(SCENES_DATA, scene_audios)):
        duration = audio_info["duration"]
        audio_file = audio_info["audio_path"]
        img_file = scene["image_file"]
        segment_path = TEMP_DIR / f"kareem_segment_{i + 1}.mp4"
        
        num_frames = int(round(duration * TARGET_FPS))
        print(f" ▶️ تحريك المشهد {i + 1} ({duration:.2f} ثانية)...")

        # Fast and smooth Ken Burns zoompan with audio mapping
        cmd = [
            "ffmpeg", "-y",
            "-i", img_file,
            "-i", audio_file,
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},zoompan=z='min(zoom+0.0012,1.20)':d={num_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={TARGET_FPS}",
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
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg segment error: {res.stderr[-300:]}")
        segment_files.append(str(segment_path))

    # 4. Concat segments
    print("\n🎞️ 4. دمج المقاطع...")
    concat_list = TEMP_DIR / "kareem_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in segment_files:
            f.write(f"file '{Path(p).as_posix()}'\n")

    concatenated_raw = TEMP_DIR / "kareem_raw.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concatenated_raw)
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)

    # 5. Burn subtitles to final video
    print("\n🔥 5. حرق النصوص والترجمة المتحركة وإخراج الفيديو النهائي...")
    final_output = OUTPUT_DIR / "kareem_part_1.mp4"
    sub_escaped = Path(ass_path).as_posix().replace(":", "\\:")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", str(concatenated_raw),
        "-vf", f"subtitles='{sub_escaped}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(final_output)
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)

    print("\n" + "=" * 60)
    print("🎉 تم إنتاج الحلقة الأولى بنجاح مذهل!")
    print(f"📁 مسار الفيديو: {final_output}")
    print("=" * 60)
    return str(final_output)

if __name__ == "__main__":
    make_story_video()
