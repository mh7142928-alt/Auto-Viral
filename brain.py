import json
import re
import sys
import requests
import random
from config import GEMINI_API_KEY

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONTENT_PILLARS = [
    "أحاديث نبوية شريفة صحيحة وشرح أثرها وفضلها في تفريج الهموم وصلاح الحياة",
    "أدعية نبوية مأثورة وأذكار مجربة لجلب الرزق والسكينة وطمأنينة القلب",
    "قصص وعبر ملهمة ومؤثرة من السيرة النبوية ومواقف الصحابة الكرام والأنبياء",
    "نصائح وتوجيهات دينية تبث الأمل والراحة النفسية وتطرد القلق وحسن الظن بالله",
    "أسرار وفضائل الأعمال الصالحة البسيطة ذات الأجور المضاعفة (الصدقة، الاستغفار، الصلاة على النبي)",
    "سنن نبوية مهجورة تجلب البركة في البيت وتغير حياتك إلى الأفضل",
    "لطائف وتأملات إيمانية في آيات القرآن الكريم تدعو للتفكر في عظمة الخالق",
    "مواقف إنسانية عظيمة تفيض بالرحمة من حياة النبي صلى الله عليه وسلم وأخلاقه"
]

CREATIVE_PROMPT = """أنت صانع محتوى إسلامي هادف ومؤثر (Viral Islamic Content Creator) على TikTok وInstagram Reels وYouTube Shorts.
مهمتك كتابة فيديو قصير مؤثر وراقٍ يلامس القلوب ويبعث الطمأنينة والسكينة بناءً على هذا المحور: "{pillar}".

شروط كتابة السيناريو:
1. الدقة والأصالة: اعتمد فقط على أحاديث نبوية صحيحة وموثوقة، أو نصوص قرآنية سليمة، أو عبر إسلامية حقيقية ذات أثر طيب.
2. الخطاف (Hook): ابدأ أول ثانيتين بجملة مؤثرة جداً أو سؤال وجداني يشد الانتباه فوراً ويبعث الرغبة في الاستماع (تجنب المقدمات التقليدية مثل: أهلاً بكم أو اليوم سنتحدث).
   - مثال: "حديث نبوي يغفر ذنوبك كلها وإن كانت مثل زبد البحر..." أو "لو أغلقت كل الأبواب في وجهك، فهذا الدعاء النبوي سيفتحها بإذن الله..."
3. المحتوى الإيماني المشوق: ركّز على الأثر الروحي والعملي للمعلومة بلغة عربية فصيحة، عذبة، سلسة ومريحة للأذن تنشر السكينة والأمل.
4. الخاتمة التفاعلية ومشاركة الأجر (إلزامي في المشهد الأخير دائماً):
   - يجب أن ينتهي المشهد الأخير دائماً بحث أو سؤال تفاعلي إيماني يُحفز المشاهدين على التعليق ومشاركة الأجر (مثل: الصلاة على النبي ﷺ، أو كتابة ذكر، أو مشاركة دعاء).
   - يليه مباشرة تذكير صريح ولبق بضرورة الإعجاب بالفيديو والاشتراك/المتابعة لنشر الخير والمشاركة في الأجر (فالدال على الخير كفاعله).
   - مثال واقعي للنص المنطوق للمشهد الأخير: "والآن صَلِّ على الحبيب المصطفى ﷺ في التعليقات، ولا تنسَ الإعجاب بالفيديو والاشتراك في القناة لتشاركنا الأجر ومتابعة المزيد من المقاطع الإيمانية المؤثرة!"
5. مدة النص الإجمالية: تتراوح بين 30 إلى 45 ثانية عند القراءة لتكون مناسبة تماماً كفيديو قصير متكامل.
6. المشاهد البصرية: قسّم الفيديو إلى 3 إلى 5 مشاهد، ولكل مشهد اكتب `search_query` باللغة الإنجليزية حصراً يكون دقيقاً ومصمماً للبحث عن لقطات فيديو سينمائية عمودية حقيقية عالية الجودة (HD/4K) على موقع Pexels، مثل:
   - لقطات طبيعة مهيبة تدعو للتفكر: شروق أو غروب الشمس، غيوم ذهبية، جبال شامخة، سماء ليلية ونجوم، أنهار جارية، صحراء هادئة (peaceful sunrise golden clouds desert, starry night sky milky way time lapse, flowing crystal clear river forest).
   - لقطات معمارية وروحانية: مآذن، مساجد، إضاءة هادئة، كتاب أو مصحف مفتوح بإضاءة دافئة (majestic mosque minaret aerial architecture, open antique holy book warm candle light, silhouette person contemplating calm landscape).

يجب إرجاع النتيجة بصيغة JSON حصراً بالهيكل التالي:
{{
  "topic": "عنوان الفكرة الإيمانية باختصار",
  "title": "عنوان جذاب ومؤثر جداً مع إيموجي هادئ",
  "caption": "وصف جذاب ومؤثر للمنشور يحتوي على الحث على الصلاة على النبي أو الذكر ودعوة للاشتراك ومشاركة الأجر مع 6 إلى 8 هاشتاجات إسلامية شائعة (#اسلاميات #أحاديث #دعاء #قرآن #راحة_نفسية #خواطر_دينية #Shorts #Reels)",
  "full_script": "النص الكامل المتصل باللغة العربية",
  "scenes": [
    {{
      "narration": "الجملة المقروءة لهذا المشهد باللغة العربية (تأكد أن المشهد الأخير يحتوي على الحث الإيماني في التعليقات وتذكير اللايك والاشتراك)",
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
