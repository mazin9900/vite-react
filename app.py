import streamlit as st
import requests
import json
from datetime import datetime

# إعدادات الواجهة الأساسية
st.set_page_config(page_title="مركز الرصد الإقليمي الموحد", page_icon="🛰️", layout="wide")

# تصميم عسكري داكن مع تأثيرات بصرية للإنذار
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; direction: rtl; }
.stApp { background: #010409; color: #e6edf3; }
.news-card { background: #0d1117; padding: 20px; border-radius: 12px; border-right: 5px solid #1f6feb; margin-bottom: 15px; border: 1px solid #30363d; }
.urgent-card { background: #2d0000; border: 2px solid #ff4b4b; padding: 20px; border-radius: 12px; margin-bottom: 20px; animation: flash 1.5s infinite; }
@keyframes flash { 50% { border-color: transparent; } }
</style>
""", unsafe_allow_html=True)

# المفاتيح البرمجية (تم دمج مفتاحك هنا)
GEMINI_KEY = "AIzaSyAkKH0ij-W1SQnOo8R1jMwMnfAf7YP4JAg"
NEWS_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"

# --- وظيفة الترجمة والتحليل عبر Gemini ---
def get_ai_analysis(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        prompt = f"ترجم هذا الخبر العسكري للعربية وحلله باختصار شديد: {text}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=10)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return text # عرض النص الأصلي في حال فشل الاتصال

# --- الهيكل الرئيسي للتطبيق ---
st.markdown(f"""
<div style='text-align:center; padding:10px; border-bottom:1px solid #30363d;'>
    <h1 style='color:#58a6ff; margin:0;'>🛰️ رادار النزاع الإقليمي - غرفة العمليات</h1>
    <p style='color:#8b949e;'>تحديث مباشر: {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["📢 الأخبار والعواجل", "💥 رادار القصف والعمليات", "📺 البث الإخباري المباشر"])

# --- التبويب 1: الأخبار العاجلة ---
with tabs[0]:
    st.subheader("📰 التغذية الإخبارية الحية")
    # بحث مخصص لدول الخليج وإيران وإسرائيل
    query = "(Oman OR Saudi OR UAE OR Kuwait OR Qatar OR Bahrain OR Iran OR Israel) AND (attack OR military OR missile)"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_KEY}&sortBy=publishedAt&pageSize=6"
    
    try:
        data = requests.get(url).json()
        articles = data.get("articles", [])
        
        for art in articles:
            analysis = get_ai_analysis(art['title'])
            
            # فلترة الكلمات العاجلة لإظهار الإنذار الأحمر
            is_critical = any(word in analysis for word in ["انفجار", "هجوم", "قصف", "صواريخ", "عمان", "السعودية", "إيران"])
            
            card_class = "urgent-card" if is_critical else "news-card"
            st.markdown(f"""
            <div class="{card_class}">
                <h3 style="margin:0;">{'🚨' if is_critical else '🔹'} {analysis}</h3>
                <p style="font-size:13px; color:#8b949e; margin-top:10px;">المصدر: {art['source']['name']} | التاريخ: {art['publishedAt'][:10]}</p>
                <a href="{art['url']}" target="_blank" style="color:#58a6ff; font-size:12px;">رابط الخبر الأصلي 🔗</a>
            </div>
            """, unsafe_allow_html=True)
            if is_critical:
                st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    except:
        st.error("فشل في جلب الأخبار. تأكد من اتصال الإنترنت.")

# --- التبويب 2: خريطة القصف التفاعلية ---
with tabs[1]:
    st.subheader("📍 رادار الأهداف والضربات الميدانية")
    # محاكاة لنقاط القصف النشطة
    strike_points = [
        {"lat": 35.6892, "lon": 51.3890, "name": "طهران: استهداف منشآت حيوية", "type": "ضربة"},
        {"lat": 32.0853, "lon": 34.7818, "name": "تل أبيب: اعتراضات صاروخية", "type": "اعتراض"},
        {"lat": 27.1833, "lon": 56.2667, "name": "مضيق هرمز: دوريات بحرية نشطة", "type": "رصد"},
        {"lat": 23.5859, "lon": 58.4059, "name": "مسقط: تأهب دفاعي ووساطة", "type": "آمن"}
    ]
    
    

    # خريطة Leaflet برمجية حقيقية
    map_html = f"""
    <div id="map" style="height:500px; border-radius:15px; border:1px solid #30363d;"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([25.0, 45.0], 5);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        { "".join([f"L.circle([{p['lat']}, {p['lon']}], {{color: '{'red' if p['type']=='ضربة' else 'orange'}', radius: 90000}}).addTo(map).bindPopup('<b>{p['type']}</b>: {p['name']}');" for p in strike_points]) }
    </script>
    """
    st.components.v1.html(map_html, height=520)

# --- التبويب 3: البث المباشر ---
with tabs[2]:
    st.subheader("📺 القنوات الإخبارية - بث حي")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🔴 الجزيرة مباشر**")
        st.components.v1.iframe("https://www.youtube.com/embed/B-sk6R4AJ5E", height=400)
    with c2:
        st.markdown("**🔵 العربية مباشر**")
        st.components.v1.iframe("https://www.youtube.com/embed/GkBj6pJBHpo", height=400)

st.markdown("---")
st.caption("نظام الرصد العسكري الموحد 2026 | مدعوم بذكاء Gemini الاصطناعي")
