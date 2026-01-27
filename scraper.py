import os
import time
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# --- إعدادات الرابط ---
TARGET_URL = "https://coursatk.online/years"
OUTPUT_FILE = "index.html"

# --- تصميم المنصة (نفس التصميم الاحترافي) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - المحتوى الشامل</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #3b82f6; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }}
        
        header {{ background: #111827; padding: 2rem; text-align: center; border-bottom: 4px solid var(--primary); }}
        header h1 {{ margin: 0; font-size: 2.5rem; color: var(--primary); text-transform: uppercase; }}
        header p {{ color: #9ca3af; margin-top: 10px; }}

        .container {{ max-width: 1000px; margin: 2rem auto; padding: 0 1rem; display: flex; flex-direction: column; gap: 20px; }}

        .section-title {{ color: #fbbf24; font-size: 1.5rem; margin-top: 2rem; border-right: 4px solid #fbbf24; padding-right: 10px; }}

        .card {{ background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #374151; transition: 0.3s; display: flex; flex-direction: column; }}
        .card:hover {{ transform: translateY(-3px); border-color: var(--primary); }}
        
        .card-body {{ padding: 1.5rem; }}
        .card-title {{ margin: 0 0 10px 0; font-size: 1.1rem; font-weight: bold; color: white; }}
        
        /* مشغل الفيديو */
        video {{ width: 100%; display: block; background: #000; max-height: 400px; }}
        
        /* الصور */
        .img-preview {{ width: 100%; height: auto; object-fit: cover; max-height: 300px; }}

        .btn {{ display: inline-flex; align-items: center; gap: 8px; background: var(--primary); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 10px; }}
        .btn:hover {{ background: #2563eb; }}
        
        .meta-tag {{ background: #374151; color: #d1d5db; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-left: 5px; }}
    </style>
</head>
<body>
    <header>
        <h1><i class="fas fa-university"></i> ACADEMY</h1>
        <p>تم سحب المحتوى بعد فك التشفير</p>
        <div style="font-size: 0.8rem; color: #6b7280;">تاريخ السحب: {date}</div>
    </header>

    <div class="container">
        {content}
    </div>

    <footer style="text-align: center; padding: 2rem; color: #4b5563; margin-top: 2rem;">
        تم الإنشاء بواسطة Academy Tool &copy; 2024
    </footer>
</body>
</html>
"""

def get_content():
    print("🚀 جاري تشغيل المتصفح الذكي (Selenium)...")
    
    # إعدادات المتصفح (يعمل في الخلفية على السيرفر، أو يظهر لك لو على جهازك)
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')  # اجعلها False إذا كنت تشغل الكود على جهازك وتريد رؤية المتصفح
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print(f"🌍 جاري الدخول إلى: {TARGET_URL}")
        driver.get(TARGET_URL)

        # --- مرحلة الانتظار الذكي (لفك البوابة) ---
        print("⏳ ننتظر قليلاً لضمان تحميل الصفحة بالكامل وتخطي أي حماية بسيطة...")
        time.sleep(10) # انتظار 10 ثواني (يمكن زيادتها لو الموقع بطيء)

        # سحب كود الصفحة بعد التحميل الكامل
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        html_content = ""
        count = 0

        # --- تحليل المحتوى بذكاء ---
        
        # 1. العناوين (لفصل الأقسام)
        main_area = soup.find('body')
        
        elements = main_area.find_all(['h1', 'h2', 'a', 'video', 'img', 'div'])
        
        seen_links = set()

        for el in elements:
            # العناوين
            if el.name in ['h1', 'h2'] and el.text.strip():
                html_content += f'<div class="section-title">{el.text.strip()}</div>'
            
            # الروابط (نبحث عن الكورسات والملفات)
            if el.name == 'a':
                href = el.get('href')
                text = el.text.strip()
                if href and href not in seen_links and not href.startswith('#') and not href.startswith('javascript'):
                    full_url = urljoin(TARGET_URL, href)
                    seen_links.add(href)
                    
                    # تصنيف الرابط
                    icon = "fa-link"
                    btn_text = "فتح الرابط"
                    
                    # هل هو ملف؟
                    if any(ext in full_url.lower() for ext in ['.pdf', '.zip', '.rar', '.doc']):
                        icon = "fa-file-arrow-down"
                        btn_text = "تحميل الملف"
                    # هل هو فيديو؟
                    elif any(ext in full_url.lower() for ext in ['.mp4', '.mkv']):
                        icon = "fa-video"
                        btn_text = "تحميل الفيديو"
                    
                    # تجاهل الروابط القصيرة جداً أو روابط القوائم
                    if len(text) > 3 or "http" in text or "video" in str(el):
                        count += 1
                        html_content += f"""
                        <div class="card">
                            <div class="card-body">
                                <h3 class="card-title"><i class="fas {icon}"></i> {text if text else 'عنصر بدون عنوان'}</h3>
                                <div style="font-size:0.8rem; color:#9ca3af; margin-bottom:10px;">{full_url[:60]}...</div>
                                <a href="{full_url}" class="btn" target="_blank">{btn_text}</a>
                            </div>
                        </div>
                        """

            # الفيديوهات المباشرة
            if el.name == 'video':
                src = el.get('src')
                if src:
                    full_url = urljoin(TARGET_URL, src)
                    count += 1
                    html_content += f"""
                    <div class="card">
                        <video controls src="{full_url}"></video>
                        <div class="card-body">
                            <h3 class="card-title">🎥 فيديو مباشر</h3>
                            <a href="{full_url}" class="btn" download>تحميل الفيديو</a>
                        </div>
                    </div>
                    """

            # الصور (لو كانت صور كورسات)
            if el.name == 'img':
                src = el.get('src')
                if src and ('course' in src or 'thumb' in src or 'upload' in src):
                    full_url = urljoin(TARGET_URL, src)
                    html_content += f"""
                    <div class="card" style="max-width: 400px;">
                        <img src="{full_url}" class="img-preview" alt="صورة">
                    </div>
                    """

        if count == 0:
            html_content = "<div style='text-align:center; padding:50px;'><h3>⚠️ لم يتم العثور على محتوى، أو أن الحماية قوية جداً.</h3></div>"

        # الحفظ
        final_html = HTML_TEMPLATE.format(content=html_content, date=datetime.datetime.now())
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✅ تم الانتهاء! تم استخراج {count} عنصر.")

    except Exception as e:
        print(f"❌ خطأ: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_content()
