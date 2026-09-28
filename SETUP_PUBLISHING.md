# 📢 دليل تفعيل النشر التلقائي على المنصات الثلاث (YouTube, Instagram, TikTok)

نظام النشر مدمج ومبرمج بالكامل. لكي يتمكن السكربت من رفع الفيديوهات لحساباتك تلقائياً دون أي تدخل يدوي، تحتاج فقط لإضافة مفاتيح الربط لكل منصة (مرة واحدة فقط).

---

## 1. 🔴 يوتيوب شورتس (YouTube Shorts)
* **الجهة**: Google Cloud Console (مجاني 100%).
* **الخطوات**:
  1. ادخل إلى [Google Cloud Console](https://console.cloud.google.com/).
  2. أنشئ مشروعاً جديداً وفعّل **YouTube Data API v3**.
  3. اذهب إلى **Credentials** -> **Create Credentials** -> **OAuth Client ID** (اختر نوع التطبيق: **Desktop App**).
  4. حمّل ملف الاعتماد وسمّه `client_secrets.json` وضعه في المجلد الرئيسي `d:\Auto\`.
  5. عند تشغيل السكربت لأول مرة على جهازك:
     ```powershell
     python publishers/youtube_uploader.py
     ```
     ستفتح لك صفحة لتسجيل الدخول بحساب قناتك على يوتيوب ومنحه الإذن لرفع الفيديوهات، وسيقوم السكربت تلقائياً بحفظ مفتاح التجديد الدائم في ملف `youtube_token.json`.
  6. **للرفع عبر GitHub Actions سحابياً**: انسخ محتوى ملف `youtube_token.json` كامل وضعه في GitHub Secrets باسم `YOUTUBE_TOKEN_JSON`.

---

## 2. 📸 إنستغرام ريلز (Instagram Reels)
* **الجهة**: Meta for Developers (مجاني 100%).
* **الشروط**: حساب إنستغرام احترافي (Professional/Creator) مربوط بصفحة فيسبوك.
* **المتغيرات المطلوبة في `.env`**:
  * `INSTAGRAM_ACCOUNT_ID`: معرّف حساب إنستغرام الاحترافي الخاص بك.
  * `INSTAGRAM_ACCESS_TOKEN`: توكن الوصول طويل الأمد (Long-Lived Access Token) مع صلاحيات:
    * `instagram_content_publish`
    * `pages_show_list`
    * `pages_read_engagement`

---

## 3. 🎵 تيك توك (TikTok)
* **الجهة**: TikTok for Developers (مجاني).
* **المتغير المطلوب في `.env`**:
  * `TIKTOK_ACCESS_TOKEN`: توكن الحساب مع صلاحية نشر الفيديو (`video.upload` أو `video.publish`).

---

## ⚡ كيف يعمل النظام إذا لم تكن جهزت كل المنصات بعد؟
النظام مصمم بذكاء ومرونة:
* إذا وضعت مفاتيح **يوتيوب فقط**، سينشر تلقائياً على يوتيوب ويتجاوز المنصات الأخرى بأمان.
* إذا وضعت مفاتيح **يوتيوب وإنستغرام**، سينشر عليهما تلقائياً.
* متى ما أضفت منصة جديدة، يتعرف عليها السكربت فوراً ويبدأ بالنشر عليها!
