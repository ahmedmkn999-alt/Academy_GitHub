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
SCREENSHOT_FILE = "final_result.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Sniper Result</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #fff; padding: 20px; }}
        h1 {{ color: #4ade80; text-align: center; border-bottom: 2px solid #334155; padding-bottom: 20px; }}
        .card {{ background: #1e293b; padding: 20px; margin-bottom: 15px; border-radius: 12px; border: 1px solid #334155; display: flex; align-items: center; justify-content: space-between; }}
        .card:hover {{ border-color: #38bdf8; }}
        a {{ color: #38bdf8; text-decoration: none; font-weight: bold; font-size: 1.1em; }}
        .icon {{ font-size: 1.5em; margin-left: 15px; }}
        .btn {{ background: #2563eb; color: white; padding: 8px 15px; border-radius: 6px; text-decoration: none; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>🎯 نتيجة القناص (الكود: {code})</h1>
    <p style="text-align:center; color:#94a3b8">تم استهداف زرار "دخول المنصة"</p>
    
    <div id="content">{content}</div>
    
    <div style="margin-top:30px; text-align:center; border-top:1px solid #333; padding-top:20px">
        <p>📸 لو لسه مفيش نتيجة، حمل الصورة المرفقة final_result.png</p>
    </div>
</body>
</html>
"""

def sniper_bot():
    print(f"🚀 القناص جاهز للكود {MY_CODE}...")
    
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

        # --- الخطوة 1: الكتابة ---
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                box = inputs[0]
                box.clear()
                box.send_keys(MY_CODE)
                print("✅ تم كتابة الكود.")
                time.sleep(1)
                
                # --- الخطوة 2: القنص (دخول المنصة) ---
                # البحث عن أي عنصر يحتوي على النص "دخول المنصة"
                target_text = "دخول المنصة"
                targets = driver.find_elements(By.XPATH, f"//*[contains(text(), '{target_text}')]")
                
                if targets:
                    print(f"🔥 تم رصد الهدف: {len(targets)} زرار. جاري الإطلاق...")
                    for t in targets:
                        try:
                            if t.is_displayed():
                                driver.execute_script("arguments[0].click();", t) # ضغط إجباري
                                print("💥 تم الضغط!")
                                time.sleep(1)
                        except: pass
                else:
                    print("⚠️ لم أجد الزرار بالنص المحدد! سأجرب Enter.")
                    box.send_keys(Keys.RETURN)

                print("⏳ انتظار فتح البوابة (10 ثواني)...")
                time.sleep(10)
            else:
                print("⚠️ لا يوجد خانة كتابة!")

        except Exception as e:
            print(f"⚠️ خطأ تكتيكي: {e}")

        # --- الخطوة 3: التوثيق والسحب ---
        driver.save_screenshot(SCREENSHOT_FILE)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # تجميع المواد
        links = soup.find_all('a', href=True)
        for a in links:
            href = a['href']
            text = a.text.strip()
            full = urljoin(TARGET_URL, href)
            
            # تجاهل الروابط الإدارية
            if "elgizawy" in full.lower() or not text: continue
            
            found += 1
            icon = "📁"
            action = "فتح"
            if "mp4" in full: icon="🎥"; action="تحميل"
            
            html_cards += f"""
            <div class="card">
                <div>
                    <span class="icon">{icon}</span>
                    <a href="{full}" target="_blank">{text}</a>
                </div>
                <a href="{full}" class="btn" target="_blank">{action}</a>
            </div>
            """

        if found == 0:
            html_cards = "<h3 style='text-align:center; color:orange'>⚠️ الصفحة مازالت فارغة. انظر الصورة المرفقة.</h3>"

        # الحفظ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(code=MY_CODE, content=html_cards))
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    sniper_bot()
