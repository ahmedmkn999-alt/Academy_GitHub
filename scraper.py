from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os

# --- الإعدادات ---
TARGET_URL = "https://uploadi.vercel.app/cur.html"
MY_CODE = "800000"
OUTPUT_FILE = "index.html"
SCREENSHOT_FILE = "screenshot.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Academy Login Debug</title>
    <style>
        body {{ font-family: sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }}
        .card {{ background: #1e293b; padding: 15px; margin: 10px auto; max-width: 600px; border-radius: 10px; border: 1px solid #334155; }}
        a {{ color: #38bdf8; text-decoration: none; font-weight: bold; font-size: 1.2em; display: block; }}
        h1 {{ color: #fbbf24; }}
        .debug-img {{ max-width: 100%; border: 2px solid #ef4444; margin-top: 20px; border-radius: 10px; }}
    </style>
</head>
<body>
    <h1>تتبع عملية الدخول 🕵️‍♂️</h1>
    <div style="background:#334155; padding:10px; margin-bottom:20px;">
        <p>تم محاولة الدخول بالكود: <strong>{code}</strong></p>
        <p>عدد الروابط المكتشفة: {count}</p>
    </div>
    
    <h2>👇 ماذا يرى الروبوت الآن؟ 👇</h2>
    <p>قم بتحميل ملف screenshot.png من الـ Artifacts لرؤية الصورة بوضوح</p>
    
    <div id="links">{content}</div>
</body>
</html>
"""

def force_login_scan():
    print(f"🚀 محاولة اقتحام بالكود {MY_CODE}...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,720") # حجم شاشة موبايل/لابتوب
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    html_cards = ""
    links_found = 0

    try:
        driver.get(TARGET_URL)
        time.sleep(5)

        # --- محاولة الدخول العنيفة ---
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                box = inputs[0]
                box.clear()
                box.send_keys(MY_CODE)
                print("✅ تم كتابة الكود.")
                time.sleep(1)
                
                # 1. نجرب Enter الأول
                box.send_keys(Keys.RETURN)
                time.sleep(2)
                
                # 2. نجرب نضغط على أي زرار "Submit" أو "Button" في الصفحة
                buttons = driver.find_elements(By.TAG_NAME, "button")
                inputs_submit = driver.find_elements(By.XPATH, "//input[@type='submit']")
                
                # نضغط على كل الأزرار المتاحة (محاولة إجبارية)
                all_clickables = buttons + inputs_submit
                if all_clickables:
                    print(f"Found {len(all_clickables)} buttons, clicking them...")
                    for btn in all_clickables:
                        try:
                            if btn.is_displayed():
                                btn.click()
                                print("🖱️ تم الضغط على زرار!")
                                time.sleep(1)
                        except:
                            pass
                
                print("⏳ انتظار تحميل الصفحة التالية (10 ثواني)...")
                time.sleep(10)
            else:
                print("⚠️ لم يتم العثور على خانة للكود!")

        except Exception as e:
            print(f"⚠️ خطأ أثناء الدخول: {e}")

        # --- اللقطة الحاسمة (Screenshot) ---
        driver.save_screenshot(SCREENSHOT_FILE)
        print("📸 تم التقاط صورة للوضع الحالي.")

        # --- سحب الروابط ---
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # تجميع كل الروابط (عشان نشوف لو "المواد" ظهرت)
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            full = urljoin(TARGET_URL, href)
            
            # استبعاد روابط المطور والروابط الفارغة
            if "elgizawy" in full or not text:
                continue

            links_found += 1
            html_cards += f"""
            <div class="card">
                <a href="{full}" target="_blank">📂 {text}</a>
                <span style="font-size:0.8em; color:#aaa">{full}</span>
            </div>
            """
            
        if links_found == 0:
            html_cards = "<h3>⚠️ لم نتحرك من صفحة الدخول (انظر الصورة المرفقة)</h3>"

        # حفظ التقرير
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(code=MY_CODE, count=links_found, content=html_cards))

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    force_login_scan()
