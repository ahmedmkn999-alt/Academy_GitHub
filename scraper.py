import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import datetime
from pyvirtualdisplay import Display

# الرابط الرئيسي
MAIN_URL = "https://coursatk.online/years"
OUTPUT_FILE = "index.html"

# --- تصميم المنصة الفخم (HTML/CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - Cinema Mode</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #e11d48; --bg: #0f0f0f; --card: #1e1e1e; --text: #f1f1f1; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }}
        
        /* الهيدر */
        header {{ background: linear-gradient(to bottom, #27272a, #0f0f0f); padding: 30px; text-align: center; border-bottom: 2px solid var(--primary); }}
        h1 {{ margin: 0; font-size: 2.5rem; color: var(--primary); text-transform: uppercase; letter-spacing: 2px; }}
        
        .container {{ max-width: 1100px; margin: 20px auto; padding: 0 15px; }}

        /* قسم الكورس */
        .section-box {{ background: #18181b; border-radius: 16px; margin-bottom: 40px; overflow: hidden; border: 1px solid #3f3f46; }}
        .section-header {{ background: #27272a; padding: 15px 25px; font-size: 1.4rem; font-weight: bold; color: #fbbf24; border-bottom: 1px solid #3f3f46; }}
        .section-content {{ padding: 20px; }}

        /* مشغل الفيديو السينمائي */
        .video-wrapper {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 12px; background: #000; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 15px; }}
        .video-wrapper iframe, .video-wrapper video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }}
        
        /* شبكة الصور */
        .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px; }}
        .gallery-img {{ width: 100%; height: 150px; object-fit: cover; border-radius: 8px; border: 2px solid #3f3f46; transition: 0.3s; }}
        .gallery-img:hover {{ transform: scale(1.05); border-color: var(--primary); }}

        /* الكروت والروابط */
        .item-card {{ background: var(--card); padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; }}
        .btn {{ background: var(--primary); color: white; padding: 8px 20px; text-decoration: none; border-radius: 50px; font-weight: bold; transition: 0.2s; font-size: 0.9rem; }}
        .btn:hover {{ background: #be123c; transform: translateY(-2px); }}
        
        .badge {{ background: #3f3f46; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; color: #a1a1aa; }}
    </style>
</head>
<body>
    <header>
        <h1><i class="fas fa-play-circle"></i> ACADEMY CINEMA</h1>
        <p>مشغل فيديوهات ومعرض صور للمحتوى التعليمي</p>
        <div style="color:#71717a; font-size:0.8rem; margin-top:10px;">اخر تحديث: {date}</div>
    </header>

    <div class="container">
        {content}
    </div>
</body>
</html>
"""

def deep_scrape_media():
    print("🖥️ تشغيل الشاشة الوهمية...")
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options)
    final_html = ""

    try:
        # 1. الدخول للرئيسية
        print(f"🌍 الدخول للموقع: {MAIN_URL}")
        driver.get(MAIN_URL)
        time.sleep(15) # وقت كافي لتخطي Cloudflare

        soup_main = BeautifulSoup(driver.page_source, 'html.parser')
        
        # سحب الروابط الداخلية
        target_links = set()
        for a in soup_main.find_all('a', href=True):
            href = a['href']
            full = urljoin(MAIN_URL, href)
            # فلترة ذكية: ناخد روابط السنين والكورسات بس
            if MAIN_URL in full and full != MAIN_URL:
                if "login" not in full and "#" not in full:
                    target_links.add(full)

        print(f"🔗 تم العثور على {len(target_links)} قسم. جاري الدخول وسحب الميديا...")

        # 2. الغوص في الصفحات (بحد أقصى 10 صفحات لتجنب التايم أوت)
        for link in list(target_links)[:10]: 
            try:
                print(f"➡️ سحب محتوى: {link}")
                driver.get(link)
                time.sleep(5)
                
                sub_soup = BeautifulSoup(driver.page_source, 'html.parser')
                title = sub_soup.title.text.replace("Coursatk", "").strip() if sub_soup.title else "محتوى إضافي"
                
                content_html = ""
                
                # --- أ. سحب الصور (Gallery) ---
                images_html = ""
                images = sub_soup.find_all('img')
                for img in images:
                    src = img.get('src')
                    if src:
                        full_src = urljoin(link, src)
                        # تجاهل اللوجو والأيقونات الصغيرة
                        if "logo" not in full_src and "icon" not in full_src and ".svg" not in full_src:
                             images_html += f'<a href="{full_src}" target="_blank"><img src="{full_src}" class="gallery-img"></a>'
                
                if images_html:
                    content_html += f'<div style="margin-bottom:10px; color:#a1a1aa;">📸 الصور المرفقة:</div><div class="gallery-grid">{images_html}</div>'

                # --- ب. سحب الفيديوهات (Cinema Player) ---
                # 1. Iframes (YouTube/Embedded)
                iframes = sub_soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src')
                    if src:
                        content_html += f"""
                        <div class="video-wrapper">
                            <iframe src="{src}" allowfullscreen></iframe>
                        </div>
                        <div style="text-align:left; margin-bottom:20px;">
                            <a href="{src}" class="btn" target="_blank"><i class="fas fa-external-link-alt"></i> فتح في نافذة جديدة</a>
                        </div>
                        """

                # 2. Direct Videos
                videos = sub_soup.find_all('video')
                for vid in videos:
                    src = vid.get('src')
                    if src:
                        full_vid = urljoin(link, src)
                        content_html += f"""
                        <div class="video-wrapper">
                            <video controls src="{full_vid}"></video>
                        </div>
                        <div style="margin-bottom:20px;">
                             <a href="{full_vid}" class="btn" download><i class="fas fa-download"></i> تحميل الفيديو</a>
                        </div>
                        """

                # --- ج. الملفات والروابط ---
                file_links = sub_soup.find_all('a', href=True)
                for f in file_links:
                    f_href = f['href']
                    if any(x in f_href for x in ['.pdf', 'drive', 'download', 'mediafire']):
                        content_html += f"""
                        <div class="item-card">
                            <span><i class="fas fa-file-alt"></i> {f.text.strip() or 'ملف للتحميل'}</span>
                            <a href="{f_href}" class="btn" target="_blank">تحميل</a>
                        </div>
                        """

                # إضافة القسم للمنصة لو فيه محتوى
                if content_html:
                    final_html += f"""
                    <div class="section-box">
                        <div class="section-header">{title} <span style="font-size:0.8rem; float:left; color:#71717a">{link}</span></div>
                        <div class="section-content">
                            {content_html}
                        </div>
                    </div>
                    """

            except Exception as e:
                print(f"⚠️ خطأ في رابط: {e}")
                continue

        if not final_html:
            final_html = "<h3 style='text-align:center; padding:50px;'>لم يتم العثور على ميديا. تأكد أن الموقع يعمل.</h3>"

        # حفظ الملف
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(content=final_html, date=datetime.datetime.now()))
        
        print("✅ تم بناء السينما والمعرض بنجاح!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    deep_scrape_media()
