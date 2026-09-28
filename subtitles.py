from pathlib import Path
from config import TEMP_DIR

ASS_HEADER = """[Script Info]
Title: Auto Shorts
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsText,Segoe UI,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,450,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_time(seconds: float) -> str:
    """Formats float seconds into ASS timestamp H:MM:SS.cs."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

def split_text_into_chunks(text: str, max_words: int = 5) -> list:
    """Splits a long Arabic sentence into digestible 4-6 word chunks for viral reel readability."""
    words = text.strip().split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def build_scene_subtitles(scene_audios: list, output_ass_path: str) -> str:
    """
    Builds an ASS subtitle file synchronized with each scene's duration.
    Splits scene text into readable chunks with highlighted colors.
    """
    dialogues = []
    current_time = 0.0

    for item in scene_audios:
        duration = item["duration"]
        narration = item["narration"]
        
        chunks = split_text_into_chunks(narration, max_words=5)
        if not chunks:
            current_time += duration
            continue

        chunk_duration = duration / len(chunks)
        for chunk in chunks:
            start_str = format_ass_time(current_time)
            end_str = format_ass_time(current_time + chunk_duration)
            dialogues.append(f"Dialogue: 0,{start_str},{end_str},ShortsText,,0,0,0,,{chunk}")
            current_time += chunk_duration

    ass_content = ASS_HEADER + "\n".join(dialogues) + "\n"
    
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    return output_ass_path

if __name__ == "__main__":
    test_data = [
        {"duration": 4.5, "narration": "هل تعلم أن هناك كوكباً تمطر فيه السماء زجاجاً أفقياً؟"},
        {"duration": 3.8, "narration": "بسرعة تتجاوز سبعة آلاف كيلومتر في كل ساعة!"}
    ]
    path = build_scene_subtitles(test_data, "temp/test_subs.ass")
    print(f"Generated subtitles at: {path}")
