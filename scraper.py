from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# الرابط المستهدف
TARGET_URL = "https://thanwyaplus.com/"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Network Sniffer Result</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        .item {{ background: #161b22; border: 1px solid #30363d; margin-bottom: 10px; padding: 15px; border-radius: 6px; }}
        .tag {{ padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 10px; font-size: 0.8em; }}
        .video {{ background: #1f6feb; color: white; }}
        .api {{ background: #d29922; color: black; }}
        .url {{ color: #58a6ff; display: block; margin-top: 5px; word-break: break-all; }}
    </style>
</head>
<body>
    <h1 style="text-align:center; color:#238636">تم التحليل بنجاح ✅</h1>
    <div id="content">{content}</div>
</body>
</html>
"""

def stable_sniffer():
    print("🚀 بدء التشغيل المستقر...")
    
    # إعدادات المتصفح (مهمة جداً لمنع الانهيار)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # وضع بدون شاشة حديث
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # تفعيل تسجيل الشبكة
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    for key, value in caps.items():
        chrome_options.set_capability(key, value)

    driver = None
    try:
        # تشغيل المتصفح باستخدام المدير الآلي
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"🌍 الدخول للموقع: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        print("⏳ جاري الانتظار 30 ثانية لتحميل الشبكة...")
        time.sleep(30) # انتظار كافي

        # سحب السجلات
        logs = driver.get_log('performance')
        html_content = ""
        unique_urls = set()

        print(f"📦 تم سحب {len(logs)} سجل. جاري الفرز...")

        for entry in logs:
            try:
                message = json.loads(entry['message'])['message']
                if message['method'] == 'Network.responseReceived':
                    resp = message['params']['response']
                    url = resp['url']
                    mime = resp.get('mimeType', '')
                    
                    # فلاتر البحث
                    is_video = any(x in mime for x in ['video', 'mpeg', 'mp4', 'octet-stream']) or \
                               any(x in url for x in ['.m3u8', '.mp4', 'bunny', 'vimeo'])
                    
                    is_api = 'json' in mime and 'api' in url

                    if (is_video or is_api) and url not in unique_urls:
                        unique_urls.add(url)
                        tag_class = "video" if is_video else "api"
                        tag_name = "MEDIA" if is_video else "API"
                        
                        html_content += f"""
                        <div class="item">
                            <span class="tag {tag_class}">{tag_name}</span>
                            <span style="color:#8b949e">{mime}</span>
                            <a href="{url}" class="url" target="_blank">{url}</a>
                        </div>
                        """
            except:
                continue
        
        if not html_content:
            html_content = "<h3 style='text-align:center'>لم يتم رصد ترافيك فيديو (قد يحتاج تسجيل دخول).</h3>"

        # حفظ الملف
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(content=html_content))
            
        print("✅ تم الحفظ.")

    except Exception as e:
        print(f"❌ Error: {e}")
        # كتابة الخطأ في الملف لنراه
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>Error Log:</h1><pre>{e}</pre>")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    stable_sniffer()
