import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import datetime
from pyvirtualdisplay import Display

# الرابط المباشر (بدون تسجيل دخول)
TARGET_URL = "https://uploadi.vercel.app/cur.html"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Academy - المحتوى المباشر (Selenium)</title>
    <style>
        body {{ font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; padding: 20px; }}
        .card {{ background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #334155; }}
        .btn {{ background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1 style="text-align:center">💎 تم سحب المحتوى (JS Mode)</h1>
    <div id="content">{content}</div>
</body>
</html>
"""

def selenium_no_login():
    print("🚀 تشغيل المتصفح الخفي (JS Enabled)...")
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    
    html_cards = ""

    try:
        driver.get(TARGET_URL)
        print("⏳ جاري تحميل الصفحة وتشغيل السكريبتات...")
        time.sleep(10) # انتظار تحميل الجافاسكريبت والفيديوهات
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 1. سحب الفيديوهات المباشرة
        for vid in soup.find_all('video'):
            src = vid.get('src')
            if src:
                full = urljoin(TARGET_URL, src)
                html_cards += f'<div class="card"><h3>🎥 فيديو</h3><video controls src="{full}" width="100%"></video><a href="{full}" class="btn" download>تحميل</a></div>'

        # 2. سحب الروابط
        for a in soup.find_all('a', href=True):
            href = a['href']
            full = urljoin(TARGET_URL, href)
            if "mp4" in full or "mkv" in full:
                html_cards += f'<div class="card"><h3>🔗 رابط فيديو</h3><a href="{full}" class="btn">تحميل الفيديو</a></div>'

        if not html_cards:
            html_cards = "<h3>لم يتم العثور على فيديو. هل الرابط يعمل عندك؟</h3>"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(content=html_cards))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    selenium_no_login()
