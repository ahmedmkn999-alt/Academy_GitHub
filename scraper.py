import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime
import os

# الرابط الجديد المفتوح
TARGET_URL = "https://uploadi.vercel.app/cur.html"
OUTPUT_FILE = "index.html"

# تصميم المنصة الاحترافي
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - المحتوى المباشر</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #0ea5e9; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); color: var(--text); padding: 20px; }}
        header {{ text-align: center; border-bottom: 3px solid var(--primary); padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ color: var(--primary); margin: 0; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }}
        .card {{ background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #334155; transition: transform 0.3s; }}
        .card:hover {{ transform: translateY(-5px); border-color: var(--primary); }}
        
        .media-box {{ position: relative; background: #000; }}
        .media-box video, .media-box iframe {{ width: 100%; display: block; }}
        iframe {{ height: 250px; border: none; }}
        
        .card-body {{ padding: 15px; }}
        .card-title {{ font-weight: bold; margin-bottom: 10px; color: #fbbf24; }}
        .link-url {{ font-size: 0.8em; color: #94a3b8; word-break: break-all; margin-bottom: 15px; }}
        
        .btn {{ display: flex; align-items: center; justify-content: center; gap: 10px; background: var(--primary); color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; transition: 0.3s; }}
        .btn:hover {{ background: #0284c7; }}
        .btn-download {{ background: #22c55e; }}
        .btn-download:hover {{ background: #16a34a; }}
    </style>
</head>
<body>
    <header>
        <h1>💎 ACADEMY DIRECT</h1>
        <p>تم سحب المحتوى من الرابط المباشر</p>
        <div style="font-size:0.8em; color:#aaa">{date}</div>
    </header>
    <div class="grid">{content}</div>
    <footer style="text-align:center; margin-top:30px; color:#aaa; font-size:0.8em">Academy Tool v3</footer>
</body>
</html>
"""

def fast_scrape():
    print("🚀 بدء الماسح السريع...")
    # استخدام هيدر لتمويه الطلب كمتصفح حقيقي
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    html_cards = ""
    count = 0
    seen_urls = set()

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status() # التأكد أن الصفحة تعمل
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("✅ تم الاتصال بالصفحة. جاري تحليل العناصر...")

        # 1. البحث عن فيديوهات مباشرة (Video Tag)
        for vid in soup.find_all('video'):
            src = vid.get('src')
            if src:
                full = urljoin(TARGET_URL, src)
                if full not in seen_urls:
                    count += 1
                    seen_urls.add(full)
                    html_cards += f"""
                    <div class="card">
                        <div class="media-box"><video controls src="{full}"></video></div>
                        <div class="card-body">
                            <div class="card-title">🎥 فيديو مباشر {count}</div>
                            <a href="{full}" class="btn btn-download" download target="_blank"><i class="fas fa-download"></i> تحميل الفيديو</a>
                        </div>
                    </div>
                    """

        # 2. البحث عن إطارات مضمنة (Iframes - مثل يوتيوب)
        for frame in soup.find_all('iframe'):
            src = frame.get('src')
            if src:
                full = urljoin(TARGET_URL, src)
                if full not in seen_urls:
                    count += 1
                    seen_urls.add(full)
                    html_cards += f"""
                    <div class="card">
                        <div class="media-box"><iframe src="{full}" allowfullscreen></iframe></div>
                        <div class="card-body">
                            <div class="card-title">📺 فيديو مضمن {count}</div>
                            <a href="{full}" class="btn" target="_blank"><i class="fas fa-external-link-alt"></i> فتح المصدر</a>
                        </div>
                    </div>
                    """

        # 3. البحث عن روابط عادية (Links)
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            if href and "#" not in href:
                full = urljoin(TARGET_URL, href)
                if full not in seen_urls and full != TARGET_URL:
                    # استبعاد الروابط غير المفيدة
                    if "vercel.app" in full and ".html" not in full and ".mp4" not in full: continue

                    count += 1
                    seen_urls.add(full)
                    
                    icon = "fa-link"
                    btn_text = "فتح الرابط"
                    btn_class = "btn"
                    
                    # تخصيص الأيقونة حسب نوع الرابط
                    if any(x in full.lower() for x in ['.mp4', '.mkv', 'video']): icon = "fa-video"; btn_text="تحميل/مشاهدة"; btn_class="btn btn-download"
                    elif any(x in full.lower() for x in ['.pdf', 'drive', 'download']): icon = "fa-file-arrow-down"; btn_text="تحميل الملف"

                    html_cards += f"""
                    <div class="card">
                        <div class="card-body">
                            <div class="card-title"><i class="fas {icon}"></i> {text if text else f'رابط رقم {count}'}</div>
                            <div class="link-url">{full}</div>
                            <a href="{full}" class="{btn_class}" target="_blank">{btn_text}</a>
                        </div>
                    </div>
                    """

        if count == 0:
            html_cards = "<h3 style='text-align:center; padding:50px'>⚠️ لم يتم العثور على محتوى ظاهر. قد تكون الصفحة فارغة أو تعتمد على جافاسكريبت.</h3>"

        # حفظ الملف
        final_html = HTML_TEMPLATE.format(content=html_cards, date=datetime.datetime.now())
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
        print(f"🎉 تم الانتهاء! تم استخراج {count} عنصر.")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"<h1>حدث خطأ في الاتصال: {e}</h1>")

if __name__ == "__main__":
    fast_scrape()
