from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# --- إعدادات الروبوت ---
MAIN_URL = "https://uploadi.vercel.app/cur.html"
MY_CODE = "800000"
OUTPUT_FILE = "index.html"

# تصميم الصفحة النهائية (مع زرار التحميل)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>All Courses & Videos</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #fff; padding: 20px; }}
        h1 {{ text-align: center; color: #fbbf24; padding-bottom: 20px; border-bottom: 2px solid #334155; }}
        .stats {{ text-align: center; color: #94a3b8; margin: 10px 0 30px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; overflow: hidden; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); border-color: #38bdf8; }}
        
        .card-header {{ background: #334155; padding: 15px; font-weight: bold; display: flex; align-items: center; gap: 10px; }}
        .card-body {{ padding: 15px; }}
        
        .btn-download {{ display: block; width: 100%; padding: 12px; background: #22c55e; color: white; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; }}
        .btn-download:hover {{ background: #16a34a; }}
        
        .btn-open {{ background: #0ea5e9; margin-bottom: 5px; }}
        .btn-open:hover {{ background: #0284c7; }}
        
        video {{ width: 100%; border-radius: 5px; margin-bottom: 10px; }}
        .path {{ font-size: 0.8em; color: #64748b; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>💎 المحتوى الكامل للمنصة (الكود: {code})</h1>
    <div class="stats">تم العثور على: <strong>{count}</strong> عنصر</div>
    
    <div class="grid">
