# 🚀 مصنع الفيديوهات القصيرة الآلي (Automated Shorts Pipeline)

نظام متكامل ومجاني 100% لتوليد فيديوهات قصيرة عمودية (9:16) ونشرها على TikTok, Instagram Reels, YouTube Shorts بدون أي تدخل يدوي.

---

## 🏗️ هيكلية المشروع
```
d:\Auto\
├── .github/workflows/
│   └── generate_and_publish.yml  # الجدولة السحابية التلقائية عبر GitHub Actions
├── temp/                         # مجلد الملفات المؤقتة (صوت، مشاهد، ترجمات)
├── output/                       # مجلد حفظ الفيديو النهائي وملفات الوصف JSON
├── .env                          # مفاتيح التشغيل الخاصة بك (لا ترفعه إلى GitHub)
├── .env.example                  # نموذج لمتغيرات البيئة
├── requirements.txt              # مكتبات بايثون المطلوبة
├── config.py                     # إعدادات المقاسات والأصوات والمفاتيح
├── brain.py                      # توليد السيناريو والـ Prompts عبر Gemini Flash
├── tts.py                        # توليد الصوت العربي الطبيعي عبر Edge-TTS
├── pexels.py                     # البحث وتنزيل لقطات B-Roll العمودية من Pexels
├── subtitles.py                  # إنشاء وتنسيق الترجمة المتزامنة (ASS)
├── video_assembler.py            # دمج ومونتاج الفيديو وحرق الترجمة عبر FFmpeg
└── main.py                       # السكربت الرئيسي لتشغيل دورة الإنتاج كاملة
```

---

## 🔑 المتطلبات الأساسية
1. **GEMINI_API_KEY**: احصل عليه مجاناً من [Google AI Studio](https://aistudio.google.com/app/apikey).
2. **PEXELS_API_KEY**: احصل عليه مجاناً من [Pexels Developers](https://www.pexels.com/api/).

---

## 💻 التشغيل المحلي السريع

1. قم بإنشاء ملف `.env` في المجلد الرئيسي وضع مفاتيحك:
```env
GEMINI_API_KEY=your_key_here
PEXELS_API_KEY=your_key_here
```

2. تشغيل النظام لإنتاج فيديو عشوائي فوري:
```powershell
python main.py
```

3. أو تحديد موضوع معين ترغب في إنتاج فيديو عنه:
```powershell
python main.py "حقائق مرعبة عن ثقوب الفضاء السوداء"
```

ستجد الفيديو النهائي بصيغة MP4 وبدقة 1080x1920 داخل مجلد `output/`.
