import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import datetime
import random
from pyvirtualdisplay import Display

TARGET_URL = "https://coursatk.online/years"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - المحتوى الكامل</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #2563eb; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }}
        body {{ font-family: Tahoma, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 3px solid var(--primary); padding-bottom: 20px; margin-bottom: 30px; }}
        .card {{ background: var(--card); padding: 20px; margin: 15px auto; border-radius: 12px; border: 1px solid #334155; max-width: 900px; display: flex; flex-direction: column; gap: 10px; }}
        .btn {{ background: var(--primary); color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; text-align: center; font-weight: bold; width: fit-content; }}
        .section-title {{ color: #fbbf24; font-size: 1.6rem; margin: 30px 0 10px 0; border-right: 5px solid #fbbf24; padding-right: 15px; font-weight: bold; }}
        .error-box {{ background: #7f1d1d; color: #fca5a5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 ACADEMY PRO</h1>
        <p>تم سحب المحتوى باستخدام الشاشة الوهمية</p>
        <div style="font-size:0.8rem; color:#94a3b8">{date}</div>
    </div>
    <div id="content">{content}</div>
</body>
</html>
"""

def scrape_with_display():
    print("🖥️ جاري تشغيل الشاشة الوهمية (Virtual Screen)...")
    # تشغيل شاشة وهمية عشان المتصفح يفتكر إنه على كمبيوتر حقيقي
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    print("🚀 تشغيل المتصفح...")
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # لاحظ: شيلنا وضع headless عشان احنا دلوقتي عندنا شاشة وهمية
    
    driver = uc.Chrome(options=options)

    try:
        print(f"🌍 الدخول إلى: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # انتظار ذكي لعبور الحماية
        print("⏳ جاري الانتظار 20 ثانية لعبور Cloudflare...")
        time.sleep(10)
        
        # محاولة عمل Scroll بسيط لإقناع الموقع أننا بشر
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(10)

        title = driver.title
        print(f"📄 عنوان الصفحة الحالي: {title}")

        if "Just a moment" in title:
            print("⚠️ ما زال في صفحة الحماية.. سننتظر 10 ثواني إضافية")
            time.sleep(10)

        # سحب المحتوى
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        html_content = ""
        count = 0
        seen = set()

        # تحليل العناصر
        for el in soup.find_all(['h1', 'h2', 'h3', 'a', 'video']):
            # العناوين
            if el.name in ['h1', 'h2', 'h3'] and len(el.text.strip()) > 3:
                 html_content += f'<div class="section-title">{el.text.strip()}</div>'
            
            # الفيديوهات المباشرة
            if el.name == 'video':
                src = el.get('src')
                if src:
                    full = urljoin(TARGET_URL, src)
                    count += 1
                    html_content += f'<div class="card"><h3>🎥 فيديو مباشر</h3><video controls src="{full}" width="100%"></video><a href="{full}" class="btn">تحميل</a></div>'

            # الروابط
            if el.name == 'a':
                href = el.get('href')
                text = el.text.strip()
                if href and href not in seen and not href.startswith('#'):
                    full = urljoin(TARGET_URL, href)
                    if "cloudflare" in full or "coursatk" == full: continue
                    
                    seen.add(href)
                    count += 1
                    icon = "📄"
                    if any(x in full for x in ['.mp4', 'video']): icon = "🎬"
                    
                    html_content += f"""
                    <div class="card">
                        <h3>{icon} {text if text else 'رابط'}</h3>
                        <a href="{full}" class="btn" target="_blank">فتح / تحميل</a>
                    </div>
                    """

        if count == 0:
            html_content = f"<div class='error-box'><h2>⚠️ لم يتم العثور على روابط</h2><p>العنوان: {driver.title}</p></div>"

        # حفظ
        final_html = HTML_TEMPLATE.format(content=html_content, date=datetime.datetime.now())
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
        print("✅ تم الحفظ.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        display.stop() # قفل الشاشة الوهمية

if __name__ == "__main__":
    scrape_with_display()
