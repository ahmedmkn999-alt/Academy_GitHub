from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# --- الإعدادات ---
TARGET_URL = "https://uploadi.vercel.app/cur.html"
MY_CODE = "800000"
OUTPUT_FILE = "index.html"
SCREENSHOT_FILE = "final_success.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Injection Result</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #fff; padding: 20px; }}
        h1 {{ color: #4ade80; text-align: center; }}
        .card {{ background: #1e293b; padding: 15px; margin-bottom: 15px; border-radius: 12px; border: 1px solid #334155; display: flex; align-items: center; justify-content: space-between; }}
        .btn {{ background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }}
        .btn:hover {{ background: #1d4ed8; }}
        a {{ color: #38bdf8; text-decoration: none; font-size: 1.1em; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>💉 نتيجة الحقن (الكود: {code})</h1>
    <div id="content">{content}</div>
    <div style="text-align:center; margin-top:30px; color:#aaa">
        <p>تم استخدام تقنية JS Injection لتجاوز حماية React</p>
    </div>
</body>
</html>
"""

def injection_bot():
    print(f"🚀 بدء عملية الحقن للكود {MY_CODE}...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    html_cards = ""
    found = 0

    try:
        driver.get(TARGET_URL)
        time.sleep(5)

        # --- الخطوة 1: الحقن (أهم خطوة) ---
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                box = inputs[0]
                print("💉 جاري حقن الكود...")
                
                # هذه الأوامر تجبر الموقع على قبول الكود
                driver.execute_script(f"arguments[0].value = '{MY_CODE}';", box)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", box)
                driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", box)
                
                print("✅ تم تثبيت الكود في الذاكرة.")
                time.sleep(1)
                
                # --- الخطوة 2: الضغط على "دخول المنصة" ---
                # البحث عن الزرار بالنص العربي اللي شوفناه في الصورة
                targets = driver.find_elements(By.XPATH, "//*[contains(text(), 'دخول المنصة')]")
                if targets:
                    btn = targets[0]
                    driver.execute_script("arguments[0].click();", btn)
                    print("🖱️ تم الضغط على زرار الدخول.")
                else:
                    # لو فشل النص، نجرب نضغط على أي زرار أخضر
                    print("⚠️ النص غير موجود، جاري البحث عن الزرار الأخضر...")
                    btns = driver.find_elements(By.CSS_SELECTOR, "button, div[role='button']")
                    for b in btns:
                        driver.execute_script("arguments[0].click();", b)
                        
                print("⏳ انتظار تحميل البيانات (15 ثانية)...")
                time.sleep(15) # وقت كافي للتحميل
            else:
                print("⚠️ خانة الإدخال غير موجودة!")

        except Exception as e:
            print(f"⚠️ Error during injection: {e}")

        # --- الخطوة 3: الحصاد ---
        driver.save_screenshot(SCREENSHOT_FILE)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # سحب الروابط
        links = soup.find_all('a', href=True)
        for a in links:
            href = a['href']
            text = a.text.strip()
            full = urljoin(TARGET_URL, href)
            
            if "elgizawy" in full.lower() or not text: continue
            
            found += 1
            icon = "📁"
            action = "فتح القسم"
            if "mp4" in full: icon="🎥"; action="تحميل"
            
            html_cards += f"""
            <div class="card">
                <div><span style="font-size:1.5em; margin-left:10px">{icon}</span> <a href="{full}" target="_blank">{text}</a></div>
                <a href="{full}" class="btn" target="_blank">{action}</a>
            </div>
            """

        if found == 0:
            html_cards = "<h3 style='text-align:center; color:orange'>⚠️ الصفحة فارغة. تأكد أن الكود 800000 مازال صالحاً.</h3>"

        # حفظ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(code=MY_CODE, content=html_cards))
            
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    injection_bot()
