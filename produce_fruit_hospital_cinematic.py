import os
import sys
import subprocess
from pathlib import Path
from tts import generate_scene_audios
from subtitles import build_scene_subtitles
from config import OUTPUT_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, TARGET_FPS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HOSPITAL_IMG = r"C:\Users\Mohamad\.gemini\antigravity\brain\9662f180-e24b-42cd-9751-621d5adf87e2\fruit_hospital_drama_1790587567104.jpg"

HOSPITAL_SCENES = [
    {
        "narration": "صدمة مدوية في قسم الطوارئ! خرجت الدكتورة فراولة بالتقرير الطبي الصادم، وانهار السيد موزة بالبكاء."
    },
    {
        "narration": "بينما تجمدت السيدة برتقالة في مكانها من هول الفاجعة، وما كشفه التقرير لم يكن في حسبان أي أحد!"
    },
    {
        "narration": "هل سينجو الطفل من هذه الليلة العصيبة؟ ما قالته الدكتورة فراولة في النهاية سيصدمك... تابع الحلقة 2 لتعرف الحقيقة كاملة!"
    }
]

def produce_cinematic_hospital_short():
    print("=" * 65)
    print("🎬 إنتاج فيديو دراما مستشفى الفواكه السينمائي التلقائي")
    print("=" * 65)

    # 1. Voice
    print("\n🎙️ 1. توليد التعليق الصوتي الدرامي الحابس للأنفاس...")
    scene_audios = generate_scene_audios(HOSPITAL_SCENES, session_id="fruit_hospital_v1")
    total_duration = sum(item["duration"] for item in scene_audios)
    print(f"⏱️ مدة الفيديو الإجمالية: {total_duration:.1f} ثانية")

    # 2. Subtitles
    print("\n🎨 2. توليد الترجمة الدرامية المنسقة...")
    ass_path = str(TEMP_DIR / "fruit_hospital_subs.ass")
    build_scene_subtitles(scene_audios, ass_path)

    # 3. Render 3 cinematic camera motion segments from the image
    print("\n🎥 3. إنتاج حركات الكاميرا ثلاثية الأبعاد ومؤثرات المستشفى...")
    segment_files = []

    # Movement 1: Camera floats towards the weeping Banana and Doctor
    # Movement 2: Camera pans slightly towards the shocked Orange
    # Movement 3: Dramatic push-in on the critical medical report and expressions
    motions = [
        # Zoom towards center-left (Banana & Doctor)
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},zoompan=z='min(zoom+0.0010,1.18)':x='iw*0.25*(1-1/zoom)':y='ih*0.35*(1-1/zoom)':d={{num_frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={TARGET_FPS}",
        # Zoom towards center-right (Doctor & Orange)
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},zoompan=z='min(zoom+0.0012,1.22)':x='iw*0.65*(1-1/zoom)':y='ih*0.35*(1-1/zoom)':d={{num_frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={TARGET_FPS}",
        # Dramatic center zoom-in on the trio with slight camera shake
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},zoompan=z='min(zoom+0.0015,1.25)':x='iw*0.45*(1-1/zoom)':y='ih*0.35*(1-1/zoom)':d={{num_frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={TARGET_FPS}"
    ]

    for i, (audio_info, motion_filter) in enumerate(zip(scene_audios, motions)):
        seg_file = TEMP_DIR / f"fruit_hosp_seg_{i + 1}.mp4"
        duration = audio_info["duration"]
        audio_file = audio_info["audio_path"]
        num_frames = int(round(duration * TARGET_FPS))

        print(f" ▶️ رندر حركة المشهد {i + 1} ({duration:.2f} ثانية)...")
        vf = motion_filter.format(num_frames=num_frames)

        cmd = [
            "ffmpeg", "-y",
            "-i", HOSPITAL_IMG,
            "-i", audio_file,
            "-vf", vf,
            "-t", f"{duration:.3f}",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            str(seg_file)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        segment_files.append(str(seg_file))

    # 4. Concat segments
    print("\n🎞️ 4. دمج المقاطع في تسلسل مشوق...")
    concat_list = TEMP_DIR / "fruit_hosp_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in segment_files:
            f.write(f"file '{Path(p).as_posix()}'\n")

    concatenated_raw = TEMP_DIR / "fruit_hosp_raw.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concatenated_raw)
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)

    # 5. Burn subtitles & export final video
    print("\n🔥 5. حرق الترجمة وتصدير الحلقة النهائية...")
    final_output = OUTPUT_DIR / "fruit_hospital_drama_ep01.mp4"
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

    print("\n" + "=" * 65)
    print("🎉 تم إنتاج فيديو دراما مستشفى الفواكه بنجاح تام!")
    print(f"📁 مسار الفيديو: {final_output}")
    print("=" * 65)
    return str(final_output)

if __name__ == "__main__":
    produce_cinematic_hospital_short()
