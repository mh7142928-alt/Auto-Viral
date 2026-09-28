import json
import re
import sys
import requests
import random
from config import GEMINI_API_KEY

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONTENT_PILLARS = [
    "حقائق نفسية مدهشة وسلوكيات بشرية غامضة تفسر مشاعرنا وتصرفاتنا اليومية",
    "أغرب الصدف التاريخية الموثقة التي غيرت مجرى العالم بأسره بالصدفة البحتة",
    "أماكن ساحرة وغامضة على كوكب الأرض ستظن من شدة جمالها أنها من عالم آخر",
    "عجائب الطبيعة وظواهر حقيقية نادرة ومرعبة لا يجد لها العلم تفسيراً",
    "عادات يومية بسيطة تميز أذكى وأنجح 1% من البشر وأسرار تفكيرهم",
    "اختراعات وتطورات تكنولوجية خيالية ستغير شكل حياة البشر في السنوات القادمة",
    "أسرار مذهلة عن قدرات العقل البشري وقوة الإدراك التي لا نستخدمها",
    "أعماق البحار والمخلوقات النادرة التي تعيش في أشد بقاع الكوكب عزلة"
]

CREATIVE_PROMPT = """أنت صانع محتوى فيروسي عبقري (Top Viral Creator) على TikTok وInstagram Reels وYouTube Shorts.
مهمتك ابتكار فكرة جديدة كلياً وممتعة ومبهرة بناءً على هذا المحور: "{pillar}".

شروط كتابة السيناريو:
1. الخطاف (Hook): ابدأ أول ثانيتين بسؤال صادم أو معلومة تثير الدهشة فوراً (تجنب المقدمات التقليدية مثل: أهلاً بكم أو مرحباً).
2. المحتوى المشوق: معلومات أو نقاط سريعة، ممتعة، ومكتوبة بلغة عربية فصيحة سلسة وجذابة للغاية ومريحة للأذن.
3. الخاتمة التفاعلية والدعوة للإعجاب والاشتراك (إلزامي في المشهد الأخير دائماً):
   - يجب أن ينتهي المشهد الأخير دائماً بسؤال تفاعلي ذكي مرتبط بمحتوى الفيديو يُحفز المشاهدين على كتابة رأيهم في التعليقات.
   - يليه مباشرة تذكير صريح ولبق بضرورة الإعجاب بالفيديو والاشتراك في القناة/الحساب لمتابعة كل جديد.
   - مثال واقعي للنص المنطوق للمشهد الأخير: "والآن أخبرنا برأيك في التعليقات: هل تعتقد أن...؟ لا تنسَ الضغط على زر الإعجاب والاشتراك لمتابعة المزيد من الأسرار المدهشة!"
4. مدة النص الإجمالية: تتراوح بين 30 إلى 45 ثانية عند القراءة لتكون مناسبة تماماً كفيديو قصير متكامل.
5. المشاهد البصرية: قسّم الفيديو إلى 3 إلى 5 مشاهد، ولكل مشهد اكتب `search_query` باللغة الإنجليزية حصراً يكون دقيقاً ومصمماً للبحث عن لقطات فيديو سينمائية عمودية حقيقية عالية الجودة (HD/4K) على موقع Pexels (مثال: drone aerial tropical waterfall, mysterious ancient library interior, deep ocean bioluminescence macro, person typing comments on smartphone).

يجب إرجاع النتيجة بصيغة JSON حصراً بالهيكل التالي:
{{
  "topic": "عنوان الفكرة المبتكرة باختصار",
  "title": "عنوان مثير وجذاب جداً مع إيموجي",
  "caption": "وصف جذاب للمنشور يحتوي على السؤال التفاعلي ودعوة للاشتراك والإعجاب مع 5 إلى 7 هاشتاجات شائعة",
  "full_script": "النص الكامل المتصل باللغة العربية",
  "scenes": [
    {{
      "narration": "الجملة المقروءة لهذا المشهد باللغة العربية (تأكد أن المشهد الأخير يحتوي على السؤال التفاعلي وتذكير اللايك والاشتراك)",
      "search_query": "Cinematic HD English video search query for Pexels"
    }}
  ]
}}
"""

MODELS_LIST = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash"
]

def generate_innovative_script(custom_topic: str = None) -> dict:
    """Generates a dynamic, highly creative viral script across diverse pillars."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing! Please set it in your .env file.")

    pillar = custom_topic if custom_topic else random.choice(CONTENT_PILLARS)
    prompt = CREATIVE_PROMPT.format(pillar=pillar)

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
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

    raise RuntimeError(f"All models failed to generate script. Last error: {last_error}")

if __name__ == "__main__":
    print("Testing Creative Brain...")
    data = generate_innovative_script()
    print(f"\nTitle: {data['title']}")
    print(f"Topic: {data.get('topic')}")
    print(f"\nScenes ({len(data['scenes'])}):")
    for i, s in enumerate(data['scenes'], 1):
        print(f" {i}. [{s['search_query']}] -> {s['narration']}")
