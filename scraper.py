import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import datetime

# إعدادات الرابط
TARGET_URL = "https://uploadi.vercel.app/cur.html"
OUTPUT_FILE = "index.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academy - المحتوى المستخرج</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #0ea5e9; padding-bottom: 20px; }}
        .card {{ background: #1e293b; padding: 15px; margin: 10px auto; border-radius: 10px; border: 1px solid #334155; max-width: 800px; display: flex; justify-content: space-between; align-items: center; }}
        .btn {{ background: #22c55e; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
        .time {{ color: #94a3b8; font-size: 0.8rem; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ACADEMY LIBRARY</h1>
        <p>تم التحديث: {date}</p>
    </div>
    <div id="content">{content}</div>
</body>
</html>
"""

def build_site():
    print("Starting scraper...")
    try:
        response = requests.get(TARGET_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = ""
        count = 0
        
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.text.strip()
            if href:
                full_url = urljoin(TARGET_URL, href)
                # شروط الفيديو
                if any(x in full_url.lower() for x in ['.mp4', '.mkv', 'video', 'watch']):
                    count += 1
                    name = text if text else f"فيديو رقم {count}"
                    cards += f"""
                    <div class="card">
                        <div><i class="fas fa-video"></i> {name}</div>
                        <a href="{full_url}" class="btn" target="_blank">تحميل/مشاهدة</a>
                    </div>
                    """
        
        if count == 0:
            cards = "<h3 style='text-align:center'>⚠️ لم يتم العثور على فيديوهات مباشرة حالياً</h3>"

        final_html = HTML_TEMPLATE.format(content=cards, date=datetime.datetime.now())
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_html)
        print("Done!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_site()
