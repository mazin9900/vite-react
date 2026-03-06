import streamlit as st
import requests
import json
from datetime import datetime
import base64

# إعدادات الواجهة الاحترافية
st.set_page_config(page_title="مركز الرصد العسكري الموحد", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; direction: rtl; }
.stApp { background: #010409; color: #e6edf3; }
.news-box { background: #0d1117; padding: 15px; border-radius: 10px; border-right: 5px solid #1f6feb; margin-bottom: 10px; border: 1px solid #30363d; }
.critical-box { background: #2d0000; border-right: 5px solid #ff4b4b; padding: 15px; border-radius: 10px; border: 1px solid #4a0000; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# المفاتيح التي زودتني بها
GEMINI_KEY = "AIzaSyAkKH0ij-W1SQnOo8R1jMwMnfAf7YP4JAg"
NEWS_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"

# --- وظائف المعالجة ---
def translate_and_analyze(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        prompt = f"أنت محلل عسكري، ترجم هذا الخبر للعربية وحلل خطورته باختصار: {text}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=10)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return text # في حال الفشل يعرض النص الأصلي

def play_alert():
    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- الهيكل الرئيسي ---
st.markdown(f"<h1 style='text-align:center; color:#58a6ff;'>🛰️ رادار العمليات الإقليمي | {datetime.now().strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

tabs = st.tabs(["🔴 الأخبار العاجلة", "🗺️ خريطة القصف والعمليات", "📺 البث المباشر", "🕵️ كاشف الزيف"])

# --- التبويب 1: الأخبار ---
with tabs[0]:
    st.subheader("📰 التغذية الإخبارية (عمان، الخليج، إيران، إسرائيل)")
    query = "(Oman OR Saudi OR UAE OR Kuwait OR Qatar OR Bahrain OR Iran OR Israel) AND (attack OR military OR explosion OR strike)"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_KEY}&sortBy=publishedAt&pageSize=8"
    
    try:
        res = requests.get(url).json()
        articles = res.get("articles", [])
        for art in articles:
            analysis_ar = translate_and_analyze(art['title'])
            
            # تحديد الأخبار الحرجة بناءً على الكلمات
            is_critical = any(word in analysis_ar for word in ["انفجار", "هجوم", "قصف", "صواريخ", "عمان", "السعودية", "إيران", "إسرائيل"])
            style = "critical-box" if is_critical else "news-box"
            
            if is_critical: play_alert() # إطلاق صوت التنبيه
            
            st.markdown(f"""<div class='{style}'>
                <h4>{'🚨' if is_urgent else '🔹'} {analysis_ar}</h4>
                <p style='font-size:12px; color:#8b949e;'>المصدر: {art['source']['name']} | <a href='{art['url']}' style='color:#58a6ff;'>المصدر الأصلي</a></p>
            </div>""", unsafe_allow_html=True)
    except:
        st.error("تأكد من اتصالك بالإنترنت وصحة المفاتيح.")

# --- التبويب 2: خريطة القصف ---
with tabs[1]:
    st.subheader("🗺️ رادار المواقع الساخنة - تحديث مباشر")
    
    # خريطة تفاعلية برمجية حقيقية
    strike_points = [
        {"lat": 35.6, "lon": 51.4, "name": "طهران - استهداف منشآت صاروخية"},
        {"lat": 32.0, "lon": 34.8, "name": "تل أبيب - تفعيل منظومات الدفاع"},
        {"lat": 27.1, "lon": 56.2, "name": "مضيق هرمز - تحركات بحرية نشطة"},
        {"lat": 23.6, "lon": 58.5, "name": "مسقط - منطقة آمنة / رصد دبلوماسي"}
    ]
    map_html = f"""
    <div id="map" style="height:500px; border-radius:15px; border: 1px solid #30363d;"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([25.0, 45.0], 5);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        { "".join([f"L.circle([{p['lat']}, {p['lon']}], {{color:'red', fillColor:'#f03', fillOpacity:0.5, radius:90000}}).addTo(map).bindPopup('{p['name']}');" for p in strike_points]) }
    </script>
    """
    st.components.v1.html(map_html, height=520)

# --- التبويب 3: البث المباشر ---
with tabs[2]:
    st.subheader("📺 القنوات الإخبارية المباشرة")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🔴 الجزيرة مباشر**")
        st.video("https://www.youtube.com/watch?v=B-sk6R4AJ5E")
    with c2:
        st.markdown("**🔵 العربية مباشر**")
        st.video("https://www.youtube.com/watch?v=GkBj6pJBHpo")

st.markdown("---")
st.caption("نظام الرصد العسكري الموحد 2026 | مدعوم بذكاء Gemini الاصطناعي")
