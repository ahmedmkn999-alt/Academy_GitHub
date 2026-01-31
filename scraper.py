import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import datetime
from pyvirtualdisplay import Display

# الرابط الجديد
TARGET_URL = "https://thanwyaplus.com/"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Thanwya Plus - Network Analysis</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid #238636; padding-bottom: 20px; margin-bottom: 20px; }}
        .section {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 15px; padding: 15px; }}
        .tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; margin-left: 10px; }}
        .tag-video {{ background: #1f6feb; color: white; }}
        .tag-api {{ background: #d29922; color: black; }}
        .url {{ color: #58a6ff; word-break: break-all; display: block; margin: 10px 0; }}
        .btn {{ background: #238636; color: white; padding: 5px 15px; text-decoration: none; border-radius: 5px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🕵️‍♂️ THANWYA PLUS SNIFFER</h1>
        <p>تحليل حركة الشبكة واستخراج الروابط الخلفية</p>
    </div>
    <div id="results">{content}</div>
</body>
</html>
"""

def analyze_thanwya():
    print("📡 بدء تحليل Thanwya Plus...")
    
    # إعدادات تسجيل الشبكة
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # تشغيل الشاشة الوهمية (لو على سيرفر)
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    driver = uc.Chrome(options=options)
    captured_data = []
    unique_links = set()

    try:
        print(f"🌍 الدخول للموقع: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # وقت كافي (60 ثانية) عشان لو حبيت تسجل دخول أو تتصفح
        print("⏳ جاري الانتظار وتسجيل البيانات (60 ثانية)...")
        time.sleep(60)

        # سحب السجلات
        logs = driver.get_log('performance')
        print(f"📦 تم سحب {len(logs)} عملية شبكة. جاري الفرز...")

        for entry in logs:
            try:
                message = json.loads(entry['message'])['message']
                if message['method'] == 'Network.responseReceived':
                    resp = message['params']['response']
                    url = resp['url']
                    mime = resp['mimeType']
                    
                    # البحث عن فيديو أو API
                    is_video = any(x in mime for x in ['video', 'mpeg', 'mp4']) or any(x in url for x in ['.m3u8', '.mp4', 'vimeo', 'bunny.net'])
                    is_api = 'json' in mime and 'api' in url

                    if (is_video or is_api) and url not in unique_links:
                        unique_links.add(url)
                        
                        tag_type = "tag-video" if is_video else "tag-api"
                        tag_text = "VIDEO FILE" if is_video else "API DATA"
                        
                        captured_data.append(f"""
                        <div class="section">
                            <span class="tag {tag_type}">{tag_text}</span>
                            <span style="color:#8b949e">{mime}</span>
                            <a href="{url}" class="url" target="_blank">{url}</a>
                            <a href="{url}" class="btn" target="_blank">فتح الرابط</a>
                        </div>
                        """)

            except:
                continue

        if not captured_data:
            captured_data = ["<h3 style='text-align:center'>لم يتم رصد ميديا. (قد يحتاج الموقع لتسجيل دخول للوصول للمحتوى)</h3>"]

        # حفظ التقرير
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(content="".join(captured_data)))
            
        print(f"✅ تم الانتهاء! تم رصد {len(unique_links)} رابط مهم.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    analyze_thanwya()
