import os
import sys
import json
import random
import string
import hashlib
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"
PORT = 8080

auth_code = None

def generate_pkce_pair():
    """Generates code_verifier and hex-encoded SHA256 code_challenge required by TikTok."""
    chars = string.ascii_letters + string.digits + "-._~"
    code_verifier = "".join(random.choice(chars) for _ in range(64))
    # TikTok specifically requires HEX-encoded SHA256
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).hexdigest()
    return code_verifier, code_challenge

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("""
                <html><body style="font-family:sans-serif; text-align:center; padding:50px;">
                <h1 style="color:#22c55e;">🎉 تم ربط تيك توك بنجاح!</h1>
                <p>تم استلام كود التفويض. يمكنك إغلاق هذه الصفحة والعودة للـ Terminal الآن.</p>
                </body></html>
                """.encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                err = params.get("error_description", ["Unknown error"])[0]
                self.wfile.write(f"Error: {err}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence console log noise from HTTP requests
        return

def run_tiktok_auth():
    if not CLIENT_KEY or not CLIENT_SECRET:
        print("❌ Error: TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET missing in .env")
        return

    # Generate PKCE verifier and challenge
    code_verifier, code_challenge = generate_pkce_pair()

    scopes = "video.publish,video.upload,user.info.basic"
    params = {
        "client_key": CLIENT_KEY,
        "scope": scopes,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urllib.parse.urlencode(params)}"

    print("=" * 60)
    print("🚀 بدء عملية المصادقة مع تيك توك (TikTok PKCE Authorization)")
    print("=" * 60)
    print(f"\n🌐 جاري فتح صفحة تسجيل الدخول في المتصفح تلقائياً...\n")

    server = HTTPServer(("localhost", PORT), OAuthHandler)
    webbrowser.open(auth_url)

    print("⏳ بانتظار موافقتك في صفحة تيك توك...")
    while auth_code is None:
        server.handle_request()

    print(f"\n✅ تم استلام كود التفويض بنجاح!")
    print("🔄 جاري استبدال الكود بـ Access Token دائم...")

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }

    res = requests.post(token_url, headers=headers, data=data, timeout=30)
    token_resp = res.json()

    if "data" in token_resp and "access_token" in token_resp["data"]:
        access_token = token_resp["data"]["access_token"]

        # Save to tiktok_token.json
        token_file = "D:/Auto/tiktok_token.json"
        with open(token_file, "w", encoding="utf-8") as f:
            json.dump(token_resp["data"], f, indent=2)

        # Update .env
        env_file = "D:/Auto/.env"
        with open(env_file, "r", encoding="utf-8") as f:
            env_content = f.read()

        if "TIKTOK_ACCESS_TOKEN=" in env_content:
            import re
            env_content = re.sub(r"TIKTOK_ACCESS_TOKEN=.*", f"TIKTOK_ACCESS_TOKEN={access_token}", env_content)
        else:
            env_content += f"\nTIKTOK_ACCESS_TOKEN={access_token}\n"

        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)

        print("\n" + "=" * 60)
        print("🎉 تم استخراج توكن تيك توك بنجاح وحفظه في المشروع!")
        print(f"📁 ملف التوكن: {token_file}")
        print(f"🔑 TIKTOK_ACCESS_TOKEN:\n{access_token}")
        print("=" * 60)
        print("\n📌 الخطوة الأخيرة: انسخ هذا التوكن وضعه في GitHub Secrets باسم 'TIKTOK_ACCESS_TOKEN'")
    else:
        print(f"\n❌ استجابة تيك توك:\n{token_resp}")

if __name__ == "__main__":
    run_tiktok_auth()
