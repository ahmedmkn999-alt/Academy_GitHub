import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import datetime
from pyvirtualdisplay import Display

# الرابط المستهدف
TARGET_URL = "https://coursatk.online/years"
OUTPUT_FILE = "index.html"

# --- تصميم منصة كشف الـ API ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Academy - API Hunter</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        h1 {{ color: #58a6ff; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        .section {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 20px; padding: 15px; }}
        .label {{ display: inline-block; padding: 2px 5px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; font-weight: bold; }}
        .json-tag {{ background: #d29922; color: #000; }}
        .video-tag {{ background: #238636; color: #fff; }}
        .url {{ word-break: break-all; color: #a5d6ff; display: block; margin-bottom: 5px; }}
        .btn {{ display: inline-block; background: #21262d; color: #c9d1d9; text-decoration: none; padding: 5px 10px; border: 1px solid #30363d; border-radius: 6px; margin-top: 5px; }}
        .btn:hover {{ background: #30363d; color: #58a6ff; }}
        .raw-data {{ display: none; background: #000; padding: 10px; margin-top: 10px; border-left: 3px solid #58a6ff; white-space: pre-wrap; }}
    </style>
    <script>
        function toggleDetails(id) {{
            var x = document.getElementById(id);
            if (x.style.display === "none") {{ x.style.display = "block"; }} else {{ x.style.display = "none"; }}
        }}
    </script>
</head>
<body>
    <h1>📡 API & NETWORK SNIFFER</h1>
    <p style="text-align:center">تم اعتراض الاتصالات الخلفية للموقع</p>
    
    <div id="results">
        {content}
    </div>
</body>
</html>
"""

def api_sniffer():
    print("📡 تشغيل وضع التجسس على الشبكة...")
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    # تفعيل تسجيل الشبكة (Performance Logging)
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # دمج القدرات مع الخيارات
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = uc.Chrome(options=options)
    
    captured_requests = []

    try:
        print(f"🌍 الدخول للموقع: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # ننتظر شوية عشان الموقع يحمل كل الـ APIs بتاعته
        print("⏳ جاري تسجيل حركة المرور (30 ثانية)...")
        time.sleep(30)
        
        # سحب سجلات الشبكة
        logs = driver.get_log('performance')
        print(f"📥 تم سحب {len(logs)} سجل شبكة. جاري التحليل...")

        for entry in logs:
            try:
                message = json.loads(entry['message'])['message']
                
                # إحنا مهتمين بالردود اللي جاية من السيرفر (ResponseReceived)
                if message['method'] == 'Network.responseReceived':
                    response = message['params']['response']
                    url = response['url']
                    mime_type = response['mimeType']
                    
                    # فلترة: إحنا عايزين ملفات الفيديو أو الـ JSON (الـ API)
                    is_api = "json" in mime_type or "xml" in mime_type
                    is_video = "video" in mime_type or "mpeg" in mime_type or "mp4" in url or "m3u8" in url
                    
                    # استبعاد ملفات الموقع العادية (CSS, Images, Fonts)
                    if (is_api or is_video) and "google" not in url and "facebook" not in url:
                        tag_class = "json-tag" if is_api else "video-tag"
                        tag_name = "API / DATA" if is_api else "MEDIA FILE"
                        
                        captured_requests.append(f"""
                        <div class="section">
                            <span class="label {tag_class}">{tag_name}</span>
                            <span style="color:#8b949e; font-size:0.8em">{mime_type}</span>
                            <a href="{url}" target="_blank" class="url">{url}</a>
                            <button class="btn" onclick="toggleDetails('details_{len(captured_requests)}')">عرض التفاصيل</button>
                            <a href="{url}" class="btn" target="_blank">فتح الرابط</a>
                            <div id="details_{len(captured_requests)}" class="raw-data">
                                Status: {response['status']} {response['statusText']}
                                <br>Server IP: {response.get('remoteIPAddress', 'N/A')}
                            </div>
                        </div>
                        """)

            except Exception:
                continue

        # حفظ التقرير
        html_content = "".join(captured_requests)
        if not html_content:
            html_content = "<h3 style='text-align:center'>لم يتم اعتراض طلبات API واضحة. قد يكون المحتوى مضمن داخل الـ HTML مباشرة.</h3>"

        final_html = HTML_TEMPLATE.format(content=html_content)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✅ تم الانتهاء! تم رصد {len(captured_requests)} رابط خلفي.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    api_sniffer()
