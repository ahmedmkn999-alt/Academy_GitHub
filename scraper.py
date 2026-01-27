import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime

# --- إعدادات الرابط ---
TARGET_URL = "https://uploadi.vercel.app/cur.html"
OUTPUT_FILE = "index.html"

# --- تصميم المنصة (النسخة المتطورة) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - المنصة الكاملة</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #3b82f6; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }}
        
        /* الهيدر */
        header {{ background: #111827; padding: 2rem; text-align: center; border-bottom: 4px solid var(--primary); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); }}
        header h1 {{ margin: 0; font-size: 2.5rem; color: var(--primary); text-transform: uppercase; letter-spacing: 2px; }}
        header p {{ color: #9ca3af; margin-top: 10px; }}

        /* الحاوية */
        .container {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem; display: flex; flex-direction: column; gap: 20px; }}

        /* كارت المحتوى العام */
        .card {{ background: var(--card); border-radius: 16px; overflow: hidden; border: 1px solid #374151; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-3px); border-color: var(--primary); }}
        
        /* كارت الفيديو */
        .video-card {{ padding: 0; }}
        .video-wrapper {{ position: relative; width: 100%; background: #000; }}
        video {{ width: 100%; display: block; max-height: 500px; }}
        .card-body {{ padding: 1.5rem; }}
        .card-title {{ margin: 0 0 10px 0; font-size: 1.25rem; font-weight: bold; color: white; }}
        
        /* الأزرار */
        .btn {{ display: inline-flex; align-items: center; gap: 8px; background: var(--primary); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: 0.2s; }}
        .btn:hover {{ background: #2563eb; }}
        .btn-download {{ background: #10b981; }}
        .btn-download:hover {{ background: #059669; }}

        /* الصور */
        .img-card img {{ width: 100%; height: auto; display: block; }}
        
        /* العناوين الفاصلة (الكورسات) */
        .section-title {{ color: #fbbf24; font-size: 1.8rem; margin: 2rem 0 1rem 0; border-right: 5px solid #fbbf24; padding-right: 15px; background: rgba(251, 191, 36, 0.1); padding: 10px; border-radius: 8px; }}

        .footer {{ text-align: center; padding: 2rem; color: #6b7280; font-size: 0.9rem; margin-top: 3rem; border-top: 1px solid #374151; }}
    </style>
</head>
<body>

    <header>
        <h1><i class="fas fa-university"></i> ACADEMY</h1>
        <p>تم سحب المحتوى الكامل: فيديوهات - صور - ملفات</p>
        <div style="font-size: 0.8rem; color: #6b7280; margin-top: 5px;">تاريخ التحديث: {date}</div>
    </header>

    <div class="container">
        {content}
    </div>

    <div class="footer">
        Generated automatically by Academy Scraper &copy; 2024
    </div>

</body>
</html>
"""

def build_site():
    print("🚀 بدء عملية السحب الشامل...")
    try:
        # 1. الاتصال بالموقع
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        html_content = ""
        items_count = 0

        # 2. البحث الذكي (Smart Scanning)
        # سنقوم بالبحث عن العناصر بالترتيب لضمان بقاء هيكل الموقع كما هو
        # نبحث عن: عناوين (h1-h3)، فيديوهات، صور، وروابط
        
        # نحدد المنطقة الرئيسية للمحتوى (body أو main) لتجنب القوائم الجانبية
        main_content = soup.find('main') or soup.find('body')
        
        if not main_content:
            main_content = soup

        for element in main_content.find_all(['h1', 'h2', 'h3', 'video', 'img', 'a', 'iframe']):
            
            # --- الحالة 1: العناوين (اسم الكورس أو القسم) ---
            if element.name in ['h1', 'h2', 'h3']:
                text = element.text.strip()
                if text:
                    html_content += f'<h2 class="section-title">{text}</h2>'

            # --- الحالة 2: الفيديوهات المباشرة (<video>) ---
            elif element.name == 'video':
                src = element.get('src')
                # لو مفيش src مباشر، ندور جوه <source>
                if not src:
                    source_tag = element.find('source')
                    if source_tag:
                        src = source_tag.get('src')
                
                if src:
                    full_src = urljoin(TARGET_URL, src)
                    items_count += 1
                    html_content += f"""
                    <div class="card video-card">
                        <div class="video-wrapper">
                            <video controls preload="metadata">
                                <source src="{full_src}" type="video/mp4">
                                متصفحك لا يدعم الفيديو.
                            </video>
                        </div>
                        <div class="card-body">
                            <h3 class="card-title">🎥 فيديو تعليمي #{items_count}</h3>
                            <a href="{full_src}" class="btn btn-download" download target="_blank">
                                <i class="fas fa-download"></i> تحميل الفيديو
                            </a>
                        </div>
                    </div>
                    """

            # --- الحالة 3: الصور (محتوى الكورس المصور) ---
            elif element.name == 'img':
                src = element.get('src')
                if src:
                    full_src = urljoin(TARGET_URL, src)
                    # نتجاهل الأيقونات الصغيرة جداً
                    if "icon" not in full_src.lower() and "logo" not in full_src.lower(): 
                        html_content += f"""
                        <div class="card img-card">
                            <img src="{full_src}" alt="صورة توضيحية">
                        </div>
                        """

            # --- الحالة 4: الروابط (قد تكون فيديوهات مخفية) ---
            elif element.name == 'a':
                href = element.get('href')
                text = element.text.strip()
                if href and href != "#":
                    full_href = urljoin(TARGET_URL, href)
                    
                    # هل الرابط يؤدي لفيديو؟
                    is_video_link = any(full_href.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.avi'])
                    
                    if is_video_link:
                        items_count += 1
                        name = text if text else f"فيديو رقم {items_count}"
                        html_content += f"""
                        <div class="card">
                            <div class="card-body" style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <h3 class="card-title" style="margin:0; font-size:1rem;">🎬 {name}</h3>
                                    <span style="color:#94a3b8; font-size:0.8rem;">ملف فيديو جاهز للتحميل</span>
                                </div>
                                <a href="{full_href}" class="btn btn-download" download target="_blank">
                                    <i class="fas fa-download"></i> تحميل
                                </a>
                            </div>
                        </div>
                        """

        if items_count == 0 and not html_content:
            html_content = "<div style='text-align:center; padding:40px; color:#ef4444;'><h3>⚠️ لم يتم العثور على محتوى واضح.</h3><p>قد يكون الموقع يستخدم تقنيات حماية متقدمة.</p></div>"

        # حفظ الملف النهائي
        final_html = HTML_TEMPLATE.format(content=html_content, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✅ تم الانتهاء! تم استخراج {items_count} عنصر فيديو وملف.")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        # تسجيل الخطأ في ملف HTML عشان نشوفه
        error_html = HTML_TEMPLATE.format(content=f"<h3 style='color:red; text-align:center;'>خطأ في النظام: {e}</h3>", date=datetime.datetime.now())
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(error_html)

if __name__ == "__main__":
    build_site()
