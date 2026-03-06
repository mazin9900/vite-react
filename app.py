import streamlit as st
import requests
import json
import feedparser
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="🛰️ وكيل الأخبار العسكري", page_icon="🛰️", layout="wide")

# التصميم CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; }
.stApp { background: #04090f; color: #e2e8f0; }
h1,h2,h3,h4 { color: #38bdf8 !important; }
div[data-testid="metric-container"] { background: #0d1e30; border-radius:10px; padding:10px; border:1px solid #1e3a5f; }
iframe { border-radius: 12px; border: 1px solid #1e3a5f; background: #000; }
</style>
""", unsafe_allow_html=True)

# --- جلب المفاتيح من ملف secrets.toml ---
try:
    NEWS_KEY = st.secrets["NEWS_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
except Exception as e:
    st.error("❌ لم يتم العثور على المفاتيح في ملف secrets.toml. تأكد من أسماء المتغيرات.")
    st.stop()

# الهيدر
st.markdown("""
<div style='text-align:center;padding:15px;background:#0d1e30;border-radius:12px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>الخليج · إيران · إسرائيل · أمريكا | مراقبة حية 2026</p>
</div>
""", unsafe_allow_html=True)

# --- الدوال المساعدة ---
def ask_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, headers={"Content-Type":"application/json"},
            json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=30)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return "خطأ في تحليل البيانات عبر Gemini."

def fetch_news(q):
    url = f"https://newsapi.org/v2/everything?q={q}&apiKey={NEWS_KEY}&language=en&sortBy=publishedAt&pageSize=10"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("articles", [])
    except: return []

def fetch_reddit(sub, q=""):
    try:
        # إضافة User-Agent ضروري لعمل Reddit API
        headers = {"User-Agent": "MilitaryNewsAgent/1.0"}
        url = f"https://www.reddit.com/r/{sub}/search.json?q={q}&sort=new&limit=10&restrict_sr=1"
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()["data"]["children"]
    except: return []

# --- التبويبات ---
TABS = st.tabs(["📺 بث مباشر", "📰 أخبار اليوم", "🟠 Reddit", "🚨 كشف التزييف", "🤖 تحليل استراتيجي"])

# ══ TAB 1 — البث المباشر (روابط محدثة) ══
with TABS[0]:
    st.markdown("### 📺 القنوات الإخبارية المباشرة")
    channels = {
        "🌍 الجزيرة مباشر": "https://www.youtube.com/embed/bNyUyrR0PHo?autoplay=1",
        "📺 العربية": "https://www.youtube.com/embed/td2XyXpPZAw?autoplay=1",
        "📡 سكاي نيوز عربية": "https://www.youtube.com/embed/9AuqejyN64E?autoplay=1",
        "🔴 الميادين": "https://www.youtube.com/embed/Z2DLh2GlN_I?autoplay=1",
        "🇬🇧 BBC Arabic": "https://www.youtube.com/embed/vH8v0H2o66k?autoplay=1"
    }
    sel_ch = st.selectbox("اختر القناة للمراقبة:", list(channels.keys()))
    st.components.v1.iframe(channels[sel_ch], height=500, scrolling=False)

# ══ TAB 2 — أخبار اليوم ══
with TABS[1]:
    if st.button("🔄 تحديث الأخبار العاجلة", type="primary", use_container_width=True):
        with st.spinner("جاري جلب البيانات من News API..."):
            st.session_state['military_news'] = fetch_news("military strike Oman Gulf")
    
    if 'military_news' in st.session_state:
        for art in st.session_state['military_news']:
            st.info(f"📰 {art['source']['name']} | {art['title']}")
            st.markdown(f"[🔗 اقرأ الخبر كاملاً]({art['url']})")
            st.divider()

# ══ TAB 3 — Reddit ══
with TABS[2]:
    st.markdown("### 🟠 مراقبة Reddit")
    sub_input = st.selectbox("اختر المنتدى:", ["worldnews", "MiddleEast", "CombatFootage"])
    if st.button("📥 تحميل البيانات من Reddit", use_container_width=True):
        with st.spinner("جاري الاتصال بـ Reddit..."):
            posts = fetch_reddit(sub_input, "war missile")
            if posts:
                for p in posts:
                    st.success(f"📌 {p['data']['title']}")
                    st.caption(f"👍 Upvotes: {p['data']['score']}")
            else:
                st.warning("لم يتم العثور على منشورات جديدة.")

# ══ TAB 5 — التحليل الاستراتيجي ══
with TABS[4]:
    st.markdown("### 🤖 تحليل Gemini الذكي")
    if st.button("📊 توليد تقرير استخباراتي", type="primary", use_container_width=True):
        with st.spinner("Gemini يقوم بتحليل الموقف الحالي..."):
            analysis = ask_gemini("قدم تحليل مختصر للوضع الأمني في سلطنة عمان والخليج العربي لعام 2026.")
            st.markdown(analysis)

st.markdown("---")
st.markdown("<center style='color:#475569'>🛰️ وكيل الأخبار العسكري | تم الربط بملف secrets.toml بنجاح</center>", unsafe_allow_html=True)
