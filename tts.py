import asyncio
import subprocess
from pathlib import Path
import edge_tts
from config import DEFAULT_VOICE, VOICE_RATE, TEMP_DIR

async def _save_speech(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = VOICE_RATE):
    """Saves speech to MP3 using Edge-TTS."""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_path)

def get_audio_duration(file_path: str) -> float:
    """Uses ffprobe to obtain audio duration in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def generate_scene_audios(scenes: list, session_id: str) -> list:
    """
    Generates TTS audio for each scene individually and measures exact duration.
    Returns a list of dicts with {audio_path, duration, narration}.
    """
    results = []
    for idx, scene in enumerate(scenes):
        narration = scene.get("narration", "").strip()
        if not narration:
            continue

        audio_path = str(TEMP_DIR / f"{session_id}_scene_{idx + 1}.mp3")
        print(f"Generating voice for scene {idx + 1}...")
        asyncio.run(_save_speech(narration, audio_path))
        
        duration = get_audio_duration(audio_path)
        print(f" Scene {idx + 1} audio duration: {duration:.2f}s")
        
        results.append({
            "index": idx + 1,
            "narration": narration,
            "audio_path": audio_path,
            "duration": duration,
            "search_query": scene.get("search_query", "nature background")
        })

    return results

if __name__ == "__main__":
    test_scenes = [
        {"narration": "هل تعلم أن كوكب المشتري هو أضخم كواكب المجموعة الشمسية؟", "search_query": "jupiter planet"},
        {"narration": "حجمه يتسع لأكثر من ألف وثلاثمائة كوكب بحجم الأرض!", "search_query": "space earth"}
    ]
    res = generate_scene_audios(test_scenes, "test")
    print("Done:", res)
