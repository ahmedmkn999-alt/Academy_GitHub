import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import os

# الرابط الافتراضي
TARGET_URL = "https://thanwyaplus.com/"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Network Analysis Result</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        .header {{ border-bottom: 2px solid #238636; padding-bottom: 20px; margin-bottom: 20px; text-align: center; }}
        .item {{ background: #161b22; border: 1px solid #30363d; margin-bottom: 10px; padding: 15px; border-radius: 6px; }}
        .tag {{ padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 10px; font-size: 0.8em; }}
        .video {{ background: #1f6feb; color: white; }}
        .api {{ background: #d29922; color: black; }}
        .url {{ color: #58a6ff; display: block; margin-top: 5px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header"><h1>🕵️‍♂️ تقرير تحليل الشبكة</h1><p>{url}</p></div>
    <div id="content">{content}</div>
</body>
</html>
"""

def run_sniffer():
    print("🚀 بدء التشغيل...")
    
    # إعدادات المتصفح لمنع الانهيار
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # تفعيل مراقبة الشبكة
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = None
    try:
        # تشغيل المتصفح
        driver = uc.Chrome(options=options, version_main=None) # version_main=None ليختار الآلية تلقائياً
        
        print(f"🌍 الدخول إلى: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        print("⏳ انتظار تحميل البيانات (45 ثانية)...")
        time.sleep(45)

        # سحب السجلات
        logs = driver.get_log('performance')
        html_content = ""
        unique_urls = set()

        for entry in logs:
            try:
                message = json.loads(entry['message'])['message']
                if message['method'] == 'Network.responseReceived':
                    resp = message['params']['response']
                    url = resp['url']
                    mime = resp['mimeType']
                    
                    is_video = any(x in mime for x in ['video', 'mpeg', 'mp4']) or '.m3u8' in url
                    is_api = 'json' in mime and 'api' in url

                    if (is_video or is_api) and url not in unique_urls:
                        unique_urls.add(url)
                        tag_class = "video" if is_video else "api"
                        tag_name = "VIDEO" if is_video else "API/DATA"
                        
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
            html_content = "<h3 style='text-align:center'>لم يتم رصد ملفات ميديا ظاهرة. قد يحتاج الموقع لتسجيل دخول.</h3>"

        # الحفظ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(url=TARGET_URL, content=html_content))
            
        print("✅ تم الحفظ بنجاح.")

    except Exception as e:
        print(f"❌ Error: {e}")
        # تسجيل الخطأ في الملف لنراه
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>حدث خطأ أثناء التشغيل:</h1><pre>{e}</pre>")
            
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    run_sniffer()
