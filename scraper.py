import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import datetime
from pyvirtualdisplay import Display
import random

# الرابط الرئيسي
MAIN_URL = "https://coursatk.online/years"
OUTPUT_FILE = "index.html"

# --- تصميم المنصة (الخزنة) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - الخزنة</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #fbbf24; --bg: #1a1a1a; --card: #2d2d2d; --text: #eaeaea; }}
        body {{ font-family: Tahoma, sans-serif; background: var(--bg); color: var(--text); padding: 20px; }}
        header {{ text-align: center; border-bottom: 2px solid var(--primary); padding-bottom: 20px; margin-bottom: 30px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #444; display: flex; flex-direction: column; }}
        
        .video-box {{ position: relative; padding-bottom: 56.25%; height: 0; background: #000; border-bottom: 1px solid #444; }}
        .video-box iframe, .video-box video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
        
        .card-body {{ padding: 15px; flex-grow: 1; }}
        .card-title {{ font-size: 1.1rem; color: var(--primary); font-weight: bold; margin-bottom: 10px; }}
        .path {{ font-size: 0.8rem; color: #888; margin-bottom: 10px; }}
        
        .btn {{ display: block; background: #2563eb; color: white; text-align: center; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: auto; }}
        .btn:hover {{ background: #1d4ed8; }}
        
        .stats {{ background: #333; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; color: #aaa; font-family: monospace; }}
    </style>
</head>
<body>
    <header>
        <h1>💎 ACADEMY VAULT</h1>
        <p>تم استخراج الفيديوهات من العمق</p>
    </header>

    <div class="stats">
        {stats}
    </div>

    <div class="grid">
        {content}
    </div>
</body>
</html>
"""

def deep_excavator():
    # 1. إعداد الشاشة الوهمية والمتصفح
    print("🚜 تشغيل الحفار...")
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options)
    
    extracted_data = [] # هنا هنخزن الفيديوهات اللي نلاقيها
    visited_urls = set() # عشان مندخلش صفحة مرتين
    urls_to_visit = [MAIN_URL] # القائمة اللي هيمشي عليها (طابور)

    try:
        # 2. الدخول الأولي والانتظار اليدوي
        print(f"🌍 الدخول للموقع: {MAIN_URL}")
        driver.get(MAIN_URL)
        
        print("⏳ معك 60 ثانية الآن! لو الموقع محتاج تسجيل دخول، ادخل بحسابك يدوياً...")
        # هنا بنديك وقت لو عايز تعمل login
        time.sleep(60) 
        
        print("🚀 بدء الزحف العميق! (هياخد وقت، سيبه يشتغل)...")

        # 3. حلقة الزحف (Crawler Loop)
        # هنلف بحد أقصى 50 صفحة عشان السيرفر ميفصلش (ممكن تزودها)
        max_pages = 50 
        pages_scanned = 0

        while urls_to_visit and pages_scanned < max_pages:
            current_url = urls_to_visit.pop(0) # خد أول رابط في الطابور
            
            if current_url in visited_urls:
                continue
            
            try:
                print(f"[{pages_scanned+1}/{max_pages}] جاري فحص: {current_url}")
                driver.get(current_url)
                time.sleep(5) # استنى الصفحة تحمل
                visited_urls.add(current_url)
                pages_scanned += 1

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                page_title = soup.title.text.strip() if soup.title else "بدون عنوان"

                # --- أ. التفتيش عن فيديوهات في الصفحة دي ---
                found_on_page = False
                
                # 1. Iframes
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src')
                    if src and ("youtube" in src or "vimeo" in src or "video" in src or "embed" in src):
                        extracted_data.append({
                            "type": "iframe", "src": src, "title": page_title, "origin": current_url
                        })
                        found_on_page = True
                        print("   ✅ تم العثور على فيديو!")

                # 2. Video Tags
                for vid in soup.find_all('video'):
                    src = vid.get('src')
                    if src:
                        full_src = urljoin(current_url, src)
                        extracted_data.append({
                            "type": "video", "src": full_src, "title": page_title, "origin": current_url
                        })
                        found_on_page = True
                        print("   ✅ تم العثور على ملف فيديو!")

                # --- ب. لو مفيش فيديو، دور على روابط تانية وضيفها للطابور ---
                # (بس نضيف الروابط الداخلية فقط عشان ميسرحش في جوجل وفيسبوك)
                if not found_on_page:
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        full_link = urljoin(current_url, href)
                        
                        # شروط الرابط عشان ندخله:
                        # 1. يكون تبع الموقع (مش خارجي)
                        # 2. ميكونش زرار خروج أو لوجين
                        # 3. ميكونش شوفناه قبل كدة
                        if "coursatk.online" in full_link and full_link not in visited_urls and full_link not in urls_to_visit:
                            if not any(x in full_link for x in ["login", "logout", "register", "#", "contact"]):
                                urls_to_visit.append(full_link)

            except Exception as e:
                print(f"⚠️ خطأ في الصفحة: {e}")

        # 4. بناء ملف HTML النهائي
        html_cards = ""
        if not extracted_data:
            html_cards = "<h2 style='text-align:center; padding:50px; color:#ef4444'>للأسف لم يتم العثور على فيديوهات حتى بعد البحث العميق.</h2>"
        else:
            for item in extracted_data:
                media_html = ""
                btn_text = ""
                btn_link = item['src']

                if item['type'] == 'iframe':
                    media_html = f'<iframe src="{item["src"]}" allowfullscreen></iframe>'
                    btn_text = "مشاهدة المصدر"
                else:
                    media_html = f'<video controls src="{item["src"]}"></video>'
                    btn_text = "تحميل الفيديو"

                html_cards += f"""
                <div class="card">
                    <div class="video-box">{media_html}</div>
                    <div class="card-body">
                        <div class="card-title">{item['title']}</div>
                        <div class="path">المصدر: {item['origin']}</div>
                        <a href="{btn_link}" class="btn" target="_blank">{btn_text}</a>
                    </div>
                </div>
                """

        stats_text = f"تم مسح {pages_scanned} صفحة | تم العثور على {len(extracted_data)} فيديو"
        
        final_html = HTML_TEMPLATE.format(stats=stats_text, content=html_cards)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        print(f"🎉 تم الانتهاء! النتيجة: {stats_text}")

    except Exception as e:
        print(f"❌ خطأ قاتل: {e}")
    finally:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    deep_excavator()
