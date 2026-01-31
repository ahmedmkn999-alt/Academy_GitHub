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

# تصميم الصفحة النهائية (لازم تنسخه كامل)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Course Downloader</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #fff; padding: 20px; }
        h1 { text-align: center; color: #fbbf24; border-bottom: 2px solid #334155; padding-bottom: 20px; }
        .stats { text-align: center; color: #94a3b8; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 15px; transition: 0.3s; }
        .card:hover { border-color: #38bdf8; transform: translateY(-5px); }
        .title { font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
        .btn { display: block; width: 100%; padding: 10px; background: #22c55e; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; }
        .btn:hover { background: #16a34a; }
        video { width: 100%; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🚀 المحتوى الكامل (الكود: 800000)</h1>
    <div class="stats">عدد الملفات: {count}</div>
    <div class="grid">{content}</div>
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

def run_bulldozer():
    driver = setup_driver()
    collected_items = []
    
    try:
        print("🚀 1. الدخول للموقع...")
        driver.get(MAIN_URL)
        time.sleep(5)

        # --- حقن الكود والدخول ---
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if inputs:
            box = inputs[0]
            # الحقن
            driver.execute_script(f"arguments[0].value = '{MY_CODE}';", box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box)
            
            # الضغط
            targets = driver.find_elements(By.XPATH, "//*[contains(text(), 'دخول المنصة')]")
            if targets:
                driver.execute_script("arguments[0].click();", targets[0])
            else:
                box.send_keys(Keys.RETURN)
                
            print("✅ تم الدخول. انتظار التحميل (20 ثانية)...")
            time.sleep(20)

        # --- المسح الشامل ---
        print("🚜 2. بدء الزحف...")
        urls_to_scan = [driver.current_url]
        scanned = set()
        
        # تجميع الروابط الأولية
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for a in soup.find_all('a', href=True):
            full = urljoin(MAIN_URL, a['href'])
            if "elgizawy" not in full and full not in urls_to_scan:
                urls_to_scan.append(full)

        # الدخول لكل رابط
        for url in urls_to_scan:
            if url in scanned: continue
            scanned.add(url)
            
            try:
                if url != driver.current_url:
                    driver.get(url)
                    time.sleep(3)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                title = soup.title.string if soup.title else "ملف"

                # فيديوهات مباشرة
                for vid in soup.find_all('video'):
                    src = vid.get('src')
                    if src:
                        collected_items.append({
                            'type': 'video', 'url': urljoin(url, src), 'name': 'محاضرة فيديو'
                        })

                # روابط خارجية
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_href = urljoin(url, href)
                    text = a.text.strip() or "رابط"
                    
                    if any(x in full_href for x in ['.mp4', 'drive', 'download']):
                        collected_items.append({
                            'type': 'link', 'url': full_href, 'name': text
                        })
                        
            except: continue

        # --- الحفظ ---
        print(f"✅ تم جمع {len(collected_items)} عنصر.")
        html_cards = ""
        for item in collected_items:
            preview = ""
            icon = "fa-file"
            if item['type'] == 'video':
                icon = "fa-video"
                preview = f'<video controls src="{item["url"]}"></video>'
            
            html_cards += f"""
            <div class="card">
                <div class="title"><i class="fas {icon}"></i> {item['name']}</div>
                {preview}
                <a href="{item['url']}" class="btn" download target="_blank">تحميل / مشاهدة</a>
            </div>
            """
            
        if not html_cards: html_cards = "<h3>⚠️ لم يتم العثور على محتوى.</h3>"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(count=len(collected_items), content=html_cards))

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_bulldozer()
