import streamlit as st
import requests
import json
from datetime import datetime
import base64
from gtts import gTTS
import io

# إعدادات النظام
st.set_page_config(page_title="🛰️ مركز رصد الشرق الأوسط", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; direction: rtl; }
.stApp { background: #020617; color: #f8fafc; }
.alert-card { background: #450a0a; border: 2px solid #ef4444; padding: 20px; border-radius: 12px; margin-bottom: 15px; animation: blinker 2s linear infinite; }
.news-card { background: #0f172a; border-right: 5px solid #38bdf8; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #1e293b; }
@keyframes blinker { 50% { opacity: 0.7; } }
</style>
""", unsafe_allow_html=True)

# المفاتيح (يجب وضع مفتاح Gemini الخاص بك هنا)
GEMINI_KEY = "AIzaSyDuOADJ6YDyqBjOYFC2x-0ql1hgb0kIWaQ"
NEWS_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"

# كلمات البحث والإنذار
CRITICAL_ZONES = ["عمان", "السعودية", "الإمارات", "قطر", "البحرين", "الكويت", "إيران", "إسرائيل", "فلسطين"]
URGENT_KEYWORDS = ["انفجار", "هجوم", "قصف", "صواريخ", "ضربة جوية", "اغتيال", "استهداف"]

def trigger_audio_alert():
    # صوت بييب عسكري
    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

def speak_news(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_b64 = base64.b64encode(fp.read()).decode()
    st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

def ask_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=15)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return "خطأ في التحليل"

# الواجهة الرئيسية
st.markdown("<h1 style='text-align:center; color:#38bdf8;'>🛰️ وكيل الاستخبارات العسكري (مباشر)</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>📅 {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')} - رصد الخليج وإيران وإسرائيل</p>", unsafe_allow_html=True)

tabs = st.tabs(["🔴 الأخبار العاجلة", "🎙️ الموجز الصوتي", "🗺️ الخريطة والعمليات", "📺 البث المباشر"])

# جلب الأخبار
query = "(Oman OR Saudi OR UAE OR Qatar OR Kuwait OR Bahrain OR Iran OR Israel) AND (attack OR strike OR explosion OR military)"
news_url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_KEY}&sortBy=publishedAt&pageSize=6"

with tabs[0]:
    st.subheader("📡 التغذية الإخبارية (ترجمة وتحليل لحظي)")
    try:
        articles = requests.get(news_url).json().get("articles", [])
        brief_text = "إليك آخر التطورات العسكرية في المنطقة. "
        
        for art in articles:
            # ترجمة العنوان للعربية للتحقق من كلمات الإنذار
            title_ar = ask_gemini(f"ترجم هذا العنوان للعربية بدقة: {art['title']}")
            
            # كشف التنبيه (عمان، السعودية، إلخ أو انفجار، قصف)
            is_urgent = any(word in title_ar for word in CRITICAL_ZONES + URGENT_KEYWORDS)
            
            if is_urgent:
                st.markdown(f"<div class='alert-card'><h3>🚨 عاجل: {title_ar}</h3><p>المصدر: {art['source']['name']}</p></div>", unsafe_allow_html=True)
                trigger_audio_alert()
            else:
                st.markdown(f"<div class='news-card'><b>🔹 {title_ar}</b><br><small>المصدر: {art['source']['name']}</small></div>", unsafe_allow_html=True)
            
            brief_text += title_ar + " . "
        
        st.session_state['briefing'] = brief_text
    except:
        st.error("يرجى التأكد من مفاتيح الـ API.")

with tabs[1]:
    st.subheader("🎙️ التقرير الاستخباري المسموع")
    if st.button("🔊 تشغيل قراءة الموجز الآن"):
        if 'briefing' in st.session_state:
            speak_news(st.session_state['briefing'])
        else:
            st.warning("لا يوجد أخبار للقراءتها حالياً.")

with tabs[2]:
    st.subheader("🗺️ رادار المواقع الاستراتيجية")
    
    st.info("📍 يتم رصد التحركات في مضيق هرمز، القواعد العسكرية، والمطارات الدولية.")
    st.image("https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?q=80&w=1000", caption="رؤية رادارية افتراضية للمنطقة")

with tabs[3]:
    st.subheader("📺 القنوات الإخبارية المباشرة")
    c1, c2 = st.columns(2)
    with c1: st.video("https://www.youtube.com/watch?v=B-sk6R4AJ5E") # الجزيرة مباشر
    with c2: st.video("https://www.youtube.com/watch?v=GkBj6pJBHpo") # العربية مباشر

st.markdown("---")
st.caption("نظام الرصد العسكري الموحد 2026 - يعمل بالذكاء الاصطناعي")
