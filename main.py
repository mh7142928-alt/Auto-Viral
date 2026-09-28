import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from brain import generate_innovative_script
from tts import generate_scene_audios
from subtitles import build_scene_subtitles
from pexels import fetch_scene_videos
from video_assembler import assemble_scenes
from config import OUTPUT_DIR, TEMP_DIR

def run_creative_pipeline(custom_topic: str = None) -> dict:
    """Generates a complete, 100% free, automated, full-motion viral video."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"viral_{timestamp}"

    print("=" * 65)
    print(f"🎬 إطلاق خط إنتاج الفيديوهات الفيروسية الآلي [{timestamp}]")
    print("=" * 65)

    # 1. Creative Brain
    print("\n🧠 1. توليد فكرة وسيناريو إبداعي عبر الذكاء الاصطناعي...")
    script_data = generate_innovative_script(custom_topic=custom_topic)
    print(f"📌 العنوان: {script_data['title']}")
    print(f"💡 المحور: {script_data.get('topic', 'إبداعي')}")
    print(f"📜 عدد المشاهد: {len(script_data['scenes'])}")

    # 2. Voiceover per scene
    print("\n🎙️ 2. توليد التعليق الصوتي الطبيعي وحساب التوقيتات بدقة...")
    scene_audios = generate_scene_audios(script_data["scenes"], session_id=session_id)
    total_duration = sum(item["duration"] for item in scene_audios)
    print(f"⏱️ مدة الفيديو الإجمالية: {total_duration:.1f} ثانية")

    # 3. Synchronized Subtitles
    print("\n🎨 3. تنسيق الترجمة التلقائية المتزامنة (ASS)...")
    ass_path = str(TEMP_DIR / f"{session_id}_subs.ass")
    build_scene_subtitles(scene_audios, ass_path)

    # 4. Fetch Real HD Full-Motion Videos from Pexels
    print("\n🎥 4. جلب مقاطع فيديو سينمائية متحركة بالكامل بدقة HD من Pexels...")
    video_clips = fetch_scene_videos(script_data["scenes"])
    print(f"✅ تم تنزيل {len(video_clips)} مقطع فيديو حقيقي.")

    # 5. Montage & Assembly
    print("\n🎞️ 5. مونتاج ودمج لقطات الفيديو وتنسيق الأبعاد (9:16) وحرق الترجمة...")
    final_filename = f"viral_short_{timestamp}.mp4"
    final_video = assemble_scenes(
        scene_media_files=video_clips,
        scene_audios=scene_audios,
        subtitles_path=ass_path,
        output_filename=final_filename
    )

    # 6. Save Metadata
    metadata_path = OUTPUT_DIR / f"metadata_{timestamp}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": script_data["title"],
            "topic": script_data.get("topic"),
            "caption": script_data["caption"],
            "full_script": script_data.get("full_script"),
            "video_file": final_filename,
            "created_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 65)
    print("🎉 تم تصدير الفيديو الحقيقي بالكامل بنجاح!")
    print(f"📁 مسار الفيديو: {final_video}")
    print(f"📄 بيانات النشر: {metadata_path}")
    print("=" * 65)

    return {
        "video_path": final_video,
        "metadata_path": str(metadata_path),
        "title": script_data["title"],
        "caption": script_data["caption"]
    }

if __name__ == "__main__":
    topic_arg = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    run_creative_pipeline(custom_topic=topic_arg)
