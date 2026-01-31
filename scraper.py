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
MAIN_URL = "https://uploadi.vercel.app/cur.html"
MY_CODE = "800000"
OUTPUT_FILE = "index.html"

# تصميم الصفحة (HTML)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Course Videos</title>
    <style>
        body {{ font-family: Tahoma, sans-serif; background: #111; color: white; padding: 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .card {{ background: #222; border: 1px solid #444; margin-bottom: 20px; padding: 15px; border-radius: 10px; text-align: right; }}
        .btn {{ display: inline-block; background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
        .btn:hover {{ background: #218838; }}
        h1 {{ color: #ffc107; margin-bottom: 30px; }}
        h3 {{ margin-top: 0; color: #8fd3fe; }}
        .error {{ color: #ff4444; border: 1px solid #ff4444; padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 محتوى المنصة (الكود: {code})</h1>
        <div id="content">{content}</div>
    </div>
</body>
</html>
"""

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def start_scraping():
    driver = setup_driver()
    html_cards = ""
    
    try:
        print("🚀 تشغيل الروبوت...")
        driver.get(MAIN_URL)
        time.sleep(5)

        # --- خطوة الدخول (الحقن) ---
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if inputs:
            box = inputs[0]
            # حقن الكود
            driver.execute_script(f"arguments[0].value = '{MY_CODE}';", box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", box)
            time.sleep(1)
            
            # محاولة الضغط (بحث عن زرار أو ضغط Enter)
            btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'دخول')]")
            if btns:
                driver.execute_script("arguments[0].click();", btns[0])
            else:
                box.send_keys(Keys.RETURN)
            
            print("✅ تم الدخول، انتظار التحميل 10 ثواني...")
            time.sleep(10)

        # --- خطوة سحب الفيديوهات ---
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items_found = 0
        
        # 1. الفيديوهات
        for vid in soup.find_all('video'):
            src = vid.get('src')
            if src:
                full = urljoin(MAIN_URL, src)
                items_found += 1
                html_cards += f"""
                <div class="card">
                    <h3>🎥 فيديو رقم {items_found}</h3>
                    <video controls src="{full}" width="100%"></video>
                    <br>
                    <a href="{full}" class="btn" download target="_blank">⬇️ تحميل الفيديو</a>
                </div>
                """

        # 2. الروابط
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            full = urljoin(MAIN_URL, href)
            
            if "elgizawy" not in full and text:
                items_found += 1
                html_cards += f"""
                <div class="card">
                    <h3>🔗 {text}</h3>
                    <a href="{full}" class="btn" target="_blank">فتح الرابط</a>
                </div>
                """

        if not html_cards:
            html_cards = "<div class='error'><h3>⚠️ لم يتم العثور على محتوى!</h3><p>تأكد أن الكود صحيح، أو أن الموقع لم يغير نظام الحماية.</p></div>"

        # حفظ الملف
        final_html = HTML_TEMPLATE.format(code=MY_CODE, content=html_cards)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        print(f"✅ تم الحفظ. عدد العناصر: {items_found}")

    except Exception as e:
        print(f"❌ Error: {e}")
        # كتابة الخطأ في ملف HTML عشان نشوفه
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>حدث خطأ: {e}</h1>")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    start_scraping()
