from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# --- الإعدادات ---
TARGET_URL = "https://uploadi.vercel.app/cur.html"
MY_CODE = "800000"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Academy Explorer</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #fff; padding: 20px; }}
        h1 {{ text-align: center; color: #fbbf24; border-bottom: 2px solid #334155; padding-bottom: 15px; }}
        .stats {{ text-align: center; color: #94a3b8; margin-bottom: 30px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        
        /* كارت الفيديو */
        .card-video {{ background: #1e293b; border: 1px solid #3b82f6; border-radius: 10px; overflow: hidden; }}
        .card-video video {{ width: 100%; display: block; }}
        .card-video .info {{ padding: 15px; }}
        .btn-dl {{ display: block; background: #2563eb; color: white; text-align: center; padding: 10px; margin-top: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; }}
        
        /* كارت المجلدات/الروابط */
        .card-link {{ background: #334155; border-radius: 10px; padding: 20px; border: 1px solid #475569; transition: 0.3s; }}
        .card-link:hover {{ transform: translateY(-5px); background: #475569; }}
        .card-link a {{ color: #38bdf8; text-decoration: none; font-size: 1.1em; font-weight: bold; display: block; word-break: break-all; }}
        .icon {{ font-size: 2em; float: right; opacity: 0.2; }}
    </style>
</head>
<body>
    <h1>💎 المستكشف الشامل (الكود: {code})</h1>
    <div class="stats">تم العثور على: {vid_count} فيديو | {link_count} قسم/رابط</div>
    <div class="grid">{content}</div>
    <div style="margin-top:50px; text-align:center; color:#555">تم الفحص باستخدام الروبوت الذكي v4</div>
</body>
</html>
"""

def deep_scan():
    print(f"🚀 بدء الزحف بالكود {MY_CODE}...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    html_cards = ""
    videos_found = 0
    links_found = 0

    try:
        # 1. الدخول
        print(f"🌍 فتح الموقع: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(5)

        # 2. كتابة الكود
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                box = inputs[0]
                box.clear()
                box.send_keys(MY_CODE)
                box.send_keys(Keys.RETURN)
                print("✅ تم إدخال الكود، جاري تحميل الصفحة الرئيسية...")
                time.sleep(8) # انتظار تحميل "المواد"
            else:
                print("⚠️ لم أجد خانة للكود، سأفحص الصفحة الحالية.")
        except Exception as e:
            print(f"Error Entering Code: {e}")

        # 3. الفحص الشامل (Scanning)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # --- أولاً: الفيديوهات المباشرة ---
        for vid in soup.find_all('video'):
            src = vid.get('src')
            if src:
                full_url = urljoin(TARGET_URL, src)
                videos_found += 1
                html_cards += f"""
                <div class="card-video">
                    <video controls src="{full_url}"></video>
                    <div class="info">
                        <h3>🎥 فيديو مباشر {videos_found}</h3>
                        <a href="{full_url}" class="btn-dl" download target="_blank">⬇️ تحميل الفيديو</a>
                    </div>
                </div>
                """

        # --- ثانياً: الروابط والأقسام (المواد/المدرسين) ---
        # هنجيب كل الروابط عشان لو هي دي "المواد"
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            full_url = urljoin(TARGET_URL, href)
            
            # فلترة الروابط (نستبعد الروابط الفارغة)
            if href in ["#", "javascript:void(0)"] or not text:
                continue

            links_found += 1
            
            # تحديد نوع الأيقونة
            icon = "📁" # افتراضي (مجلد/مادة)
            label = "فتح القسم/المادة"
            btn_color = "#38bdf8"
            
            if any(x in full_url for x in ['.mp4', '.mkv', 'drive', 'download']):
                icon = "🎬"
                label = "رابط فيديو خارجي"
                btn_color = "#f472b6"
            
            html_cards += f"""
            <div class="card-link">
                <div class="icon">{icon}</div>
                <h3>{text if text else 'رابط بدون عنوان'}</h3>
                <p style="color:#aaa; font-size:0.8em">{full_url}</p>
                <a href="{full_url}" target="_blank" style="color:{btn_color}">🔗 {label}</a>
            </div>
            """

        if videos_found == 0 and links_found == 0:
            html_cards = """
            <div style="grid-column: 1/-1; text-align:center; padding:50px; background:#334155; border-radius:10px;">
                <h2>⚠️ لم يتم العثور على محتوى!</h2>
                <p>تأكد أن الكود 800000 مازال صالحاً، أو أن الصفحة لا تحتاج لضغطات إضافية.</p>
                <p>سيقوم المطور بتحليل الصفحة بناءً على هذا التقرير.</p>
            </div>
            """

        # الحفظ
        final_html = HTML_TEMPLATE.format(
            code=MY_CODE, 
            vid_count=videos_found, 
            link_count=links_found, 
            content=html_cards
        )
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✅ تم. فيديوهات: {videos_found}, روابط: {links_found}")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>Error Occurred: {e}</h1>")
    finally:
        driver.quit()

if __name__ == "__main__":
    deep_scan()
