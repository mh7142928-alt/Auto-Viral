import json
import re
import sys
import requests
import random
from config import GEMINI_API_KEY

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOPIC_IDEAS = [
    "حقائق مذهلة وغريبة عن الفضاء والكون لم تسمع بها من قبل",
    "أسرار تاريخية غامضة لم يجد لها العلماء تفسيراً حتى اليوم",
    "عادات يومية بسيطة تميز الأشخاص الناجحين والأذكياء",
    "معلومات صادمة عن أعماق المحيطات والمخلوقات التي تعيش هناك",
    "حقائق نفسية مدهشة تفسر تصرفات البشر وطريقة تفكيرهم",
    "اكتشافات علمية وتكنولوجية ستغير شكل المستقبل قريباً",
    "أغرب الظواهر الطبيعية النادرة حول العالم"
]

SYSTEM_PROMPT = """أنت صانع محتوى محترف وخبير في كتابة نصوص فيديوهات قصيرة وسريعة الانتشار (Viral Shorts/Reels/TikTok).
مهمتك كتابة محتوى لفيديو مدته حوالي 30 ثانية باللغة العربية الفصحى السلسة والمشوقة.

يجب أن ترجع النتيجة بصيغة JSON حصراً بدون أي نصوص خارج الـ JSON بالبنية التالية:
{
  "topic": "موضوع الفيديو باختصار",
  "title": "عنوان جذاب جداً مع إيموجي",
  "caption": "وصف قصير للنشر مع 5 إلى 7 هاشتاجات شائعة",
  "full_script": "النص الكامل المقروء بالصوت متصل بدون أسماء المشاهد، يبدأ بخطاف صادم يشعل الفضول في أول ثانيتين، ثم 3 حقائق سريعة ومثيرة، ثم خاتمة سريعة تحث على المتابعة",
  "scenes": [
    {
      "narration": "الجملة المقروءة في هذا المشهد",
      "search_query": "English keywords to search for vertical stock videos on Pexels (e.g. galaxy space stars 4k, mysterious dark ocean, ancient ruins cinematic)"
    }
  ]
}

ملاحظات هامة جداً:
- `search_query` يجب أن تكون باللغة الإنجليزية دائماً ومحددة وتصلح للبحث في مكتبات الفيديو مثل Pexels.
- قسّم النص إلى 3 إلى 4 مشاهد على الأكثر.
- تجنب تماماً المقدمات الطويلة مثل "أهلاً بكم في فيديو اليوم". ابدأ مباشرة بالمعلومة الصادمة.
"""

MODELS_LIST = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash"
]

def generate_script(topic: str = None) -> dict:
    """Generates an engaging shorts script with visual search queries using Gemini Flash."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing! Please set it in your .env file.")

    if not topic:
        topic = random.choice(TOPIC_IDEAS)

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nالموضوع المطلوب لهذا الفيديو: {topic}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }

    last_error = None
    for model in MODELS_LIST:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])
                if not candidates:
                    raise ValueError("No candidates returned from Gemini API")
                
                parts = candidates[0].get("content", {}).get("parts", [])
                text_parts = [p.get("text", "") for p in parts if not p.get("thought", False)]
                content_text = "".join(text_parts).strip()

                if content_text.startswith("```"):
                    content_text = re.sub(r"^```(?:json)?\s*", "", content_text)
                    content_text = re.sub(r"\s*```$", "", content_text)

                return json.loads(content_text)
            else:
                last_error = f"{model} returned {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"{model} processing error: {e}"
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

if __name__ == "__main__":
    print("Testing Brain script generator...")
    try:
        data = generate_script()
        print(f"\nTitle: {data['title']}")
        print(f"\nTopic: {data.get('topic')}")
        print(f"\nScenes ({len(data['scenes'])}):")
        for i, scene in enumerate(data['scenes'], 1):
            print(f" {i}. [{scene['search_query']}] -> {scene['narration']}")
    except Exception as e:
        print(f"Error: {e}")
