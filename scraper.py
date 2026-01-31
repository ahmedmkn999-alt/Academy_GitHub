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
# الكود بتاعك محطوط هنا جاهز 👇
MY_CODE = "800000" 
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Course Videos</title>
    <style>
        body {{ font-family: sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }}
        .card {{ background: #1e293b; border: 1px solid #334155; padding: 20px; margin: 20px auto; max-width: 600px; border-radius: 10px; }}
        .btn {{ display: block; background: #2563eb; color: white; padding: 12px; margin-top: 15px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
        .btn:hover {{ background: #1d4ed8; }}
        h1 {{ color: #fbbf24; }}
    </style>
</head>
<body>
    <h1>نتائج الكود: {code} 🔓</h1>
    <div id="content">{content}</div>
</body>
</html>
"""

def run_bot():
    print(f"🚀 تشغيل الروبوت بالكود {MY_CODE}...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    html_content = ""

    try:
        print(f"🌍 الدخول للموقع: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(5) # انتظار فتح الصفحة

        # --- كتابة الكود ---
        try:
            print(f"🔑 جاري كتابة الكود...")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                box = inputs[0]
                box.clear()
                box.send_keys(MY_CODE) # كتابة 800000
                box.send_keys(Keys.RETURN)
                print("✅ تم الإدخال، جاري انتظار الفيديوهات...")
                time.sleep(8) # ندي وقت للفيديو يحمل
            else:
                print("⚠️ لم أجد مكان للكتابة، سأفحص الصفحة كما هي.")
        except Exception as e:
            print(f"⚠️ مشكلة بسيطة في الكتابة: {e}")

        # --- سحب الفيديوهات ---
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        found = False
        
        # فيديوهات مباشرة
        for vid in soup.find_all('video'):
            src = vid.get('src')
            if src:
                full = urljoin(TARGET_URL, src)
                found = True
                html_content += f"""
                <div class="card">
                    <h3>🎥 محاضرة فيديو</h3>
                    <video controls src="{full}" width="100%"></video>
                    <a href="{full}" class="btn" download>⬇️ تحميل الفيديو</a>
                </div>
                """
        
        # روابط
        for a in soup.find_all('a', href=True):
            href = a['href']
            full = urljoin(TARGET_URL, href)
            if "mp4" in full or "drive" in full:
                found = True
                html_content += f"""
                <div class="card">
                    <h3>🔗 رابط خارجي</h3>
                    <a href="{full}" class="btn" target="_blank">فتح الرابط</a>
                </div>
                """

        if not found:
            html_content = "<h3>⚠️ لم تظهر فيديوهات. هل الكود 800000 صحيح؟</h3>"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(code=MY_CODE, content=html_content))
            
        print("✅ تم الانتهاء.")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>Error: {e}</h1>")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_bot()
