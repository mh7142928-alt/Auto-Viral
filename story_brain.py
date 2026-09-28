import json
import re
import sys
import requests
from config import GEMINI_API_KEY
from brain import MODELS_LIST

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SERIES_EPISODE_PROMPT = """أنت كاتب سيناريو ومؤلف درامي محترف ومختص في كتابة مسلسلات الرسوم المتحركة ثلاثية الأبعاد الفيروسية على إنستغرام وتيك توك (بأسلوب Pixar/Disney).
مهمتك كتابة الحلقة رقم {current_episode} من أصل {total_episodes} حلقة من السلسلة.

معلومات السلسلة الحالية:
- عنوان السلسلة: {series_title}
- نوع العالم: {universe_type}
- بطل القصة: {protagonist}
- وصف مظهر الشخصية البصري: {character_prompt}
- الحبكة العامة للسلسلة: {overall_plot}
- ملخص ما حدث سابقاً: {previous_summary}

شروط وقواعد الحلقة:
1. مدة الحلقة: حوالي 25 إلى 35 ثانية مقسمة إلى 3 أو 4 مشاهد درامية شيقة.
2. بناء الأحداث: (بداية تشد الانتباه → حدث غير متوقع ومؤثر → نهاية معلقة بصدمة Cliffhanger تدفع المشاهدين لمتابعة الحلقة القادمة وترك مئات التعليقات).
3. يجب أن تكون خاتمة الحلقة تشويقية جداً وتدعو صراحة لمتابعة الحلقة {next_episode}.
4. لكل مشهد، اكتب جملة التعليق الصوتي بالعربية الفصحى السلسة والمؤثرة، واكتب معه `visual_prompt` بالإنجليزية يصف المشهد بدقة مستخدماً نفس مواصفات الشخصية للحفاظ على ثباتها.

يجب أن ترجع النتيجة بصيغة JSON حصراً بالهيكلية التالية:
{{
  "episode_number": {current_episode},
  "episode_title": "عنوان مشوق مع إيموجي | الحلقة {current_episode}",
  "caption": "وصف جذاب للمنشور مع حث على التعليق ومتابعة السلسلة وهاشتاجات فيروسية",
  "scenes": [
    {{
      "narration": "الجملة المقروءة بصوت الراوي لهذا المشهد",
      "visual_prompt": "{character_prompt}, [Scene specific action, background, emotional expression, dramatic lighting]"
    }}
  ],
  "episode_summary_for_memory": "سطرين يلخصان ما حدث في هذه الحلقة لإضافتها لذاكرة السلسلة للحلقة القادمة"
}}
"""

def generate_episode_script(series_info: dict) -> dict:
    """Generates a cohesive, serialized dramatic episode using Gemini."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing! Please set it in your .env file.")

    current_ep = series_info.get("current_episode", 1)
    total_eps = series_info.get("total_episodes", 30)
    next_ep = current_ep + 1

    formatted_prompt = SERIES_EPISODE_PROMPT.format(
        current_episode=current_ep,
        total_episodes=total_eps,
        next_episode=next_ep,
        series_title=series_info.get("series_title", ""),
        universe_type=series_info.get("universe_type", ""),
        protagonist=series_info.get("protagonist", ""),
        character_prompt=series_info.get("character_prompt", ""),
        overall_plot=series_info.get("overall_plot", ""),
        previous_summary=series_info.get("previous_summary", "")
    )

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": formatted_prompt}]}],
        "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}
    }

    last_error = None
    for model in MODELS_LIST:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                result = res.json()
                candidates = result.get("candidates", [])
                if not candidates:
                    continue
                parts = candidates[0].get("content", {}).get("parts", [])
                text_parts = [p.get("text", "") for p in parts if not p.get("thought", False)]
                content = "".join(text_parts).strip()
                if content.startswith("```"):
                    content = re.sub(r"^```(?:json)?\s*", "", content)
                    content = re.sub(r"\s*```$", "", content)
                return json.loads(content)
            else:
                last_error = f"{model} returned {res.status_code}"
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(f"Failed to generate story episode script: {last_error}")

if __name__ == "__main__":
    from series_manager import load_state
    state = load_state()
    print("Testing story brain for fruits...")
    ep_data = generate_episode_script(state["fruits"])
    print(f"\nTitle: {ep_data['episode_title']}")
    print(f"Scenes count: {len(ep_data['scenes'])}")
    for i, s in enumerate(ep_data['scenes'], 1):
        print(f"\nScene {i}: {s['narration']}")
        print(f"Visual: {s['visual_prompt'][:100]}...")
