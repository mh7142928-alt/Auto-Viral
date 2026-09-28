import json
import requests
import random
from config import GEMINI_API_KEY

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
- قسّم النص إلى 3 إلى 5 مشاهد على الأكثر.
- تجنب تماماً المقدمات الطويلة مثل "أهلاً بكم في فيديو اليوم". ابدأ مباشرة بالمعلومة الصادمة.
"""

def generate_script(topic: str = None) -> dict:
    """Generates an engaging shorts script with visual search queries using Gemini Flash."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing! Please set it in your .env file.")

    if not topic:
        topic = random.choice(TOPIC_IDEAS)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
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
            "temperature": 0.8,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    content_text = result["candidates"][0]["content"]["parts"][0]["text"]
    
    data = json.loads(content_text)
    return data

if __name__ == "__main__":
    import sys
    print("Testing Brain script generator...")
    try:
        data = generate_script()
        print(f"\nTitle: {data['title']}")
        print(f"\nScript: {data['full_script']}")
        print(f"\nScenes ({len(data['scenes'])}):")
        for i, scene in enumerate(data['scenes'], 1):
            print(f" {i}. [{scene['search_query']}] -> {scene['narration']}")
    except Exception as e:
        print(f"Error: {e}")
