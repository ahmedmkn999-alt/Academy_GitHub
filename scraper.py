from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os

# --- الإعدادات ---
TARGET_URL = "https://uploadi.vercel.app/cur.html"
MY_CODE = "800000"
OUTPUT_FILE = "index.html"
SCREENSHOT_FILE = "debug_view.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Force Login Result</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
        h1 {{ text-align: center; color: #38bdf8; }}
        .card {{ background: #1e293b; border: 1px solid #334155; padding: 15px; margin-bottom: 15px; border-radius: 8px; }}
        a {{ color: #fbbf24; text-decoration: none; font-weight: bold; font-size: 1.1em; display: block; }}
        .tag {{ background: #0ea5e9; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; }}
        .debug {{ text-align: center; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="debug">
        <h1>🕵️‍♂️ نتائج عملية الاقتحام</h1>
        <p>تم البحث عن: <strong>المواد / المدرسين / الكورسات</strong></p>
        <p>الحالة: {status}</p>
    </div>
    
    <div id="content">
        {content}
    </div>
    
    <div style="margin-top:30px; text-align:center;">
        <h3>📸 لقطة لما يراه الروبوت الآن:</h3>
        <p>حمل ملف debug_view.png لترى الصفحة بعينك</p>
    </div>
</body>
</html>
"""

def force_entry_scraper():
    print(f"🚀 بدء الهجوم بالكود {MY_CODE}...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    html_cards = ""
    found_items = 0
    status_msg = "جاري الفحص..."

    try:
        driver.get(TARGET_URL)
        time.sleep(5)

        # --- المرحلة 1: إدخال الكود بالطرق الصعبة ---
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                box = inputs[0]
                print("🔑 تم العثور على الخانة، جاري الحقن...")
                
                # 1. مسح وكتابة عادية
                box.clear()
                box.send_keys(MY_CODE)
                time.sleep(0.5)
                
                # 2. حقن جافاسكريبت (للمواقع الحديثة React/Vue)
                # هذا يجبر الموقع على استشعار الكتابة
                driver.execute_script("arguments[0].value = arguments[1];", box, MY_CODE)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", box)
                
                print("✅ تم كتابة الكود 800000.")
                
                # --- المرحلة 2: الضغط على "أي حاجة" ---
                # محاولة 1: زر Enter
                box.send_keys(Keys.RETURN)
                time.sleep(1)
                
                # محاولة 2: البحث عن أي زرار في الصفحة والضغط عليه
                # نضغط على button, input[submit], أو أي div واخد شكل زرار
                clickables = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], [role='button'], .btn, .button")
                
                if clickables:
                    print(f"🔥 تم العثور على {len(clickables)} زرار، جاري الضغط عليهم...")
                    for btn in clickables:
                        try:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn) # ضغط إجباري بالجافاسكريبت
                                time.sleep(0.5)
                        except: pass
                
                # محاولة 3: إرسال الفورم مباشرة لو موجودة
                try:
                    driver.execute_script("document.forms[0].submit()")
                    print("🚀 تم إجبار الفورم على الإرسال.")
                except: pass
                
                print("⏳ انتظار فتح الخزنة (10 ثواني)...")
                time.sleep(10)
                
            else:
                print("⚠️ لم أجد خانة للكتابة!")
                status_msg = "فشل: لم يتم العثور على مربع نص"

        except Exception as e:
            print(f"⚠️ خطأ في عملية الدخول: {e}")

        # --- المرحلة 3: سحب الغنائم (المواد/الفيديوهات) ---
        driver.save_screenshot(SCREENSHOT_FILE) # توثيق اللحظة
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # تجميع الروابط (المواد/الكورسات)
        links = soup.find_all('a', href=True)
        
        if not links:
            # لو ملقاش روابط a، ممكن تكون div شغالة كروابط
            html_cards = "<h3 style='color:orange; text-align:center'>⚠️ الصفحة تبدو فارغة أو مازالت في الدخول. (انظر الصورة)</h3>"
            status_msg = "فشل في الدخول"
        else:
            status_msg = "تم الدخول بنجاح ✅"
            for a in links:
                href = a['href']
                text = a.text.strip() or "رابط بدون عنوان"
                full_url = urljoin(TARGET_URL, href)
                
                # فلترة الروابط المهمة فقط
                if "javascript" in href or href == "#" or not text: continue
                
                found_items += 1
                icon = "📁" # مجلد (مادة/مدرس)
                btn_txt = "فتح القسم"
                
                # لو فيديو مباشر
                if any(x in full_url.lower() for x in ['.mp4', 'video', 'watch']):
                    icon = "🎥"
                    btn_txt = "مشاهدة/تحميل"

                html_cards += f"""
                <div class="card">
                    <span class="tag">{icon}</span>
                    <a href="{full_url}" target="_blank">{text}</a>
                    <div style="margin-top:5px; font-size:0.9em; color:#94a3b8">{full_url}</div>
                </div>
                """

        # الحفظ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(status=status_msg, content=html_cards))
            
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>Error: {e}</h1>")
    finally:
        driver.quit()

if __name__ == "__main__":
    force_entry_scraper()
