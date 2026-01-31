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
        body { font-family: Tahoma, sans-serif; background: #111; color: white; padding: 20px; text-align: center; }
        .card { background: #222; border: 1px solid #444; margin: 10px auto; padding: 15px; border-radius: 10px; max-width: 600px; }
        .btn { display: block; background: #28a745; color: white; padding: 10px; text-decoration: none; border-radius: 5px; margin-top: 10px; }
        .btn:hover { background: #218838; }
        h3 { color: #ffc107; margin: 0 0 10px 0; }
    </style>
</head>
<body>
    <h1>نتائج البحث (الكود: 800000)</h1>
    <div id="container">{content}</div>
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
    html_content = ""
    
    try:
        print("🚀 تشغيل الروبوت...")
        driver.get(MAIN_URL)
        time.sleep(5)

        # --- خطوة الدخول (الحقن) ---
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if inputs:
            box = inputs[0]
            driver.execute_script(f"arguments[0].value = '{MY_CODE}';", box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box)
            
            # محاولة الضغط على الزرار
            btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'دخول')]")
            if btns:
                driver.execute_script("arguments[0].click();", btns[0])
            else:
                box.send_keys(Keys.RETURN)
            
            print("✅ تم الدخول، انتظار التحميل 15 ثانية...")
            time.sleep(15)

        # --- خطوة سحب الفيديوهات ---
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        found = 0
        
        # تجميع الفيديوهات
        for vid in soup.find_all('video'):
            src = vid.get('src')
            if src:
                full = urljoin(MAIN_URL, src)
                found += 1
                html_content += f"""
                <div class="card">
                    <h3>🎥 فيديو {found}</h3>
                    <video controls src="{full}" width="100%"></video>
                    <a href="{full}" class="btn" download>تحميل الفيديو</a>
                </div>
                """

        # تجميع الروابط
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            full = urljoin(MAIN_URL, href)
            
            if "elgizawy" not in full and text:
                html_content += f"""
                <div class="card">
                    <h3>🔗 {text}</h3>
                    <a href="{full}" class="btn" target="_blank">فتح الرابط</a>
                </div>
                """

        if not html_content:
            html_content = "<h3>⚠️ لم يتم العثور على محتوى.</h3>"

        # حفظ الملف
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(content=html_content))
        
        print("✅ تم الحفظ بنجاح.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_scraping()
