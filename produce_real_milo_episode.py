import os
import sys
import json
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pexels import search_and_download_video
from tts import generate_scene_audios
from subtitles import build_scene_subtitles
from video_assembler import assemble_scenes
from config import OUTPUT_DIR, TEMP_DIR

MILO_EP1_SCENES = [
    {
        "search_query": "cute ginger kitten looking sad in street",
        "fallback_query": "cute baby kitten alone",
        "narration": "في ليلة باردة وعاصفة، كان ميلو القط الصغير يتجول وحيداً في شوارع المدينة باحثاً عن مأوى يحميه من الأمطار الغزيرة."
    },
    {
        "search_query": "cute fluffy kitten cozy warm place",
        "fallback_query": "cute ginger kitten looking up",
        "narration": "وفجأة، لمح نافذة صغيرة دافئة ينبعث منها ضوء ذهبي مريح ورائحة مخبوزات طازجة ملأت قلبه الصغير بالأمل."
    },
    {
        "search_query": "cute kitten big eyes looking at camera",
        "fallback_query": "cute ginger cat close up",
        "narration": "دفع ميلو الباب برأسه الصغير، وما رآه في الداخل لم يكن مخبزاً عادياً... بل بداية سر عظيم! تابع الحلقة 2 لترى المفاجأة التي تنتظر ميلو!"
    }
]

def produce_real_motion_episode():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 65)
    print("🎬 إنتاج حلقة فيديو حقيقية بالكامل (Real Full-Motion Video)")
    print("🐾 سلسلة الحيوانات الكيوت: رحلة ميلو القط الصغير | الحلقة 1")
    print("=" * 65)

    # 1. Audio
    print("\n🎙️ 1. تسجيل التعليق الصوتي الدرامي بالذكاء الاصطناعي...")
    scene_audios = generate_scene_audios(MILO_EP1_SCENES, session_id=f"milo_real_{timestamp}")
    total_duration = sum(item["duration"] for item in scene_audios)
    print(f"⏱️ مدة الفيديو: {total_duration:.1f} ثانية")

    # 2. Subtitles
    print("\n🎨 2. تنسيق الترجمة الاحترافية المتزامنة...")
    ass_path = str(TEMP_DIR / f"milo_subs_{timestamp}.ass")
    build_scene_subtitles(scene_audios, ass_path)

    # 3. Fetch Real HD Vertical Videos from Pexels
    print("\n🎥 3. جلب مقاطع فيديو حقيقية متحركة بالكامل بدقة HD من Pexels...")
    video_clips = []
    for idx, scene in enumerate(MILO_EP1_SCENES):
        out_clip = str(TEMP_DIR / f"milo_clip_{idx + 1}_{timestamp}.mp4")
        q = scene["search_query"]
        print(f" 🔍 جلب فيديو حقيقي للمشهد {idx + 1}: '{q}'...")
        try:
            clip = search_and_download_video(q, out_clip)
        except Exception:
            fallback = scene["fallback_query"]
            print(f" استخدام البديل: '{fallback}'...")
            clip = search_and_download_video(fallback, out_clip)
        video_clips.append(clip)

    # 4. Assemble real full-motion video
    print("\n🎞️ 4. مونتاج وتجميع لقطات الفيديو وقصها وحرق الترجمة...")
    final_filename = f"milo_real_video_ep01_{timestamp}.mp4"
    final_video = assemble_scenes(
        scene_media_files=video_clips,
        scene_audios=scene_audios,
        subtitles_path=ass_path,
        output_filename=final_filename
    )

    print("\n" + "=" * 65)
    print("🎉 تم تصدير الحلقة كفيديو حقيقي 100% بدون أي شرائح!")
    print(f"📁 مسار الفيديو: {final_video}")
    print("=" * 65)
    return final_video

if __name__ == "__main__":
    produce_real_motion_episode()
