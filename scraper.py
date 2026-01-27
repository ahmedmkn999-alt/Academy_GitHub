import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import datetime
from pyvirtualdisplay import Display

# الرابط الرئيسي
MAIN_URL = "https://coursatk.online/years"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - العميق</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #7c3aed; --bg: #111827; --card: #1f2937; --text: #f3f4f6; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid var(--primary); padding-bottom: 20px; margin-bottom: 30px; }}
        .course-section {{ background: #374151; padding: 15px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #4b5563; }}
        .course-title {{ color: #fbbf24; font-size: 1.5rem; margin-bottom: 15px; border-right: 4px solid #fbbf24; padding-right: 10px; }}
        .card {{ background: var(--card); padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #374151; display: flex; flex-direction: column; gap: 10px; }}
        .btn {{ background: var(--primary); color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; text-align: center; width: fit-content; display: inline-block; }}
        iframe {{ width: 100%; height: 300px; border-radius: 8px; border: none; background: #000; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ACADEMY DEEP DIVE 🤿</h1>
        <p>تم الدخول للصفحات الداخلية وسحب المحتوى</p>
        <div style="color:#9ca3af; font-size:0.8rem">{date}</div>
    </div>
    <div id="container">{content}</div>
</body>
</html>
"""

def deep_scrape():
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
        # 1. الدخول للصفحة الرئيسية (الصالة)
        print(f"🌍 الدخول للرئيسية: {MAIN_URL}")
        driver.get(MAIN_URL)
        time.sleep(10) # انتظار عبور الحماية

        # سحب روابط الكورسات/السنين من الصفحة الرئيسية
        soup_main = BeautifulSoup(driver.page_source, 'html.parser')
        course_links = set()
        
        # بنجمع كل اللينكات اللي شكلها داخلي (مش تسجيل دخول ولا خروج)
        for a in soup_main.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(MAIN_URL, href)
            # فلترة اللينكات المهمة بس
            if MAIN_URL in full_url and full_url != MAIN_URL:
                if "login" not in full_url and "register" not in full_url and "contact" not in full_url:
                    course_links.add(full_url)

        print(f"🔗 وجدنا {len(course_links)} قسم داخلي. جاري الدخول عليهم...")

        # 2. الدخول في كل رابط (الغرف)
        for link in list(course_links)[:8]: # هناخد أول 8 أقسام عشان الوقت (ممكن تزود الرقم)
            try:
                print(f"➡️ جاري فحص: {link}")
                driver.get(link)
                time.sleep(6) # استنى الصفحة تحمل
                
                # سحب المحتوى الداخلي
                sub_soup = BeautifulSoup(driver.page_source, 'html.parser')
                page_title = sub_soup.title.text if sub_soup.title else "قسم بدون عنوان"
                
                # تجميع محتوى الصفحة دي
                page_content = ""
                
                # أ. سحب الفيديوهات (Iframes)
                iframes = sub_soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src')
                    if src:
                        page_content += f'<div class="card"><h3>📺 فيديو</h3><iframe src="{src}"></iframe><a href="{src}" class="btn" target="_blank">فتح الفيديو</a></div>'

                # ب. سحب الفيديوهات المباشرة (Video tags)
                videos = sub_soup.find_all('video')
                for vid in videos:
                    src = vid.get('src')
                    if src:
                        full_vid = urljoin(link, src)
                        page_content += f'<div class="card"><h3>🎥 ملف فيديو</h3><a href="{full_vid}" class="btn">تحميل</a></div>'

                # ج. سحب روابط التحميل (PDF / Drive)
                links = sub_soup.find_all('a', href=True)
                for l in links:
                    l_href = l['href']
                    if any(x in l_href for x in ['.pdf', 'drive.google', 'mediafire', 'download']):
                         page_content += f'<div class="card"><h3>📄 ملف/رابط</h3><a href="{l_href}" class="btn" target="_blank">{l.text.strip() or "تحميل"}</a></div>'

                # لو لقينا محتوى في الصفحة دي، نضيفه للمنصة
                if page_content:
                    final_html += f'<div class="course-section"><div class="course-title">{page_title}</div>{page_content}</div>'
                
            except Exception as e:
                print(f"⚠️ تجاوز رابط بسبب خطأ: {e}")
                continue

        if not final_html:
            final_html = "<h3 style='text-align:center; color:red'>لم يتم العثور على فيديوهات داخل الأقسام. قد يحتاج الموقع لتسجيل دخول.</h3>"

        # الحفظ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.format(content=final_html, date=datetime.datetime.now()))
        
        print("✅ تم الانتهاء من السحب العميق.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    deep_scrape()
