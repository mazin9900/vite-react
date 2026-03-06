import streamlit as st
import requests
import json
from datetime import datetime

# إعداد الصفحة بتصميم داكن
st.set_page_config(page_title="🛰️ وكيل الأخبار العسكري", layout="wide", initial_sidebar_state="collapsed")

# تصميم واجهة احترافية
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; direction: rtl; }
.stApp { background: #04090f; color: #e2e8f0; }
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { background-color: #0d1e30; border-radius: 5px; color: white; padding: 10px; }
iframe { border-radius: 12px; border: 1px solid #1e3a5f; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

# --- جلب المفاتيح من ملف secrets.toml ---
NEWS_KEY = st.secrets.get("NEWS_KEY", "")
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")

if not NEWS_KEY or not GEMINI_KEY:
    st.error("⚠️ لم يتم العثور على المفاتيح! تأكد من وجود ملف .streamlit/secrets.toml في جذر المشروع.")

# الهيدر
st.markdown("<h1 style='text-align:center; color:#38bdf8;'>🛰️ وكيل الأخبار العسكري</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b;'>الخليج • إيران • إسرائيل • أمريكا | مراقبة حية 2026</p>", unsafe_allow_html=True)

# إنشاء التبويبات
tabs = st.tabs(["📺 بث مباشر", "📰 أخبار عاجلة", "🟠 Reddit", "🤖 تحليل Gemini"])

# ══ TAB 1 — البث المباشر (روابط Live ثابتة) ══
with tabs[0]:
    channels = {
        "🌍 الجزيرة": "UCPzE-fJp0P9fM9S_O0Csh9Q",
        "📺 العربية": "UCahpxixMCwoANAftn6IxotA",
        "📡 سكاي نيوز": "UC0T7ptOInS_N6S96_6Wp0mQ",
        "🇬🇧 BBC Arabic": "UC6o-unh_Xp7V67DQU97u9Xg",
        "🔴 الميادين": "UC8p8O95Gv0Yv77f_HPrC-mw"
    }
    sel_name = st.selectbox("اختر القناة للمراقبة:", list(channels.keys()))
    channel_id = channels[sel_name]
    # رابط البث المباشر التلقائي
    live_url = f"https://www.youtube.com/embed/live_stream?channel={channel_id}&autoplay=1"
    st.components.v1.iframe(live_url, height=520, scrolling=False)

# ══ TAB 2 — أخبار اليوم (News API) ══
with tabs[1]:
    if st.button("🔄 تحديث أخبار عمان والخليج", type="primary"):
        if NEWS_KEY:
            with st.spinner("جاري جلب آخر الأخبار العسكرية..."):
                url = f"https://newsapi.org/v2/everything?q=military Oman OR Gulf OR missile&apiKey={NEWS_KEY}&language=ar&sortBy=publishedAt"
                res = requests.get(url).json()
                articles = res.get("articles", [])
                for art in articles[:8]:
                    st.info(f"📰 {art['source']['name']} | {art['title']}")
                    st.write(art['description'])
                    st.markdown(f"[🔗 رابط الخبر]({art['url']})")
                    st.divider()
        else:
            st.warning("يرجى إدخال NEWS_KEY أولاً.")

# ══ TAB 3 — Reddit ══
with tabs[2]:
    if st.button("🟠 جلب منشورات Reddit الحالية"):
        with st.spinner("جاري البحث في Reddit..."):
            headers = {"User-Agent": "MilitaryNewsAgent/2.0"}
            res = requests.get("https://www.reddit.com/r/worldnews/search.json?q=Middle East war&sort=new&limit=10", headers=headers).json()
            posts = res.get("data", {}).get("children", [])
            for p in posts:
                st.success(f"📌 {p['data']['title']}")
                st.caption(f"👍 Upvotes: {p['data']['score']} | [🔗 الرابط](https://reddit.com{p['data']['permalink']})")

# ══ TAB 4 — التحليل الذكي (Gemini) ══
with tabs[3]:
    if st.button("🤖 توليد تقرير استخباراتي عسكري"):
        if GEMINI_KEY:
            with st.spinner("Gemini يقوم بتحليل الموقف الآن..."):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
                payload = {"contents": [{"parts": [{"text": "أنت محلل استخباراتي. قدم تقريراً عن الوضع العسكري في الخليج وعمان اليوم باختصار شديد ولهجة احترافية."}]}]}
                r = requests.post(url, json=payload).json()
                st.markdown(r['candidates'][0]['content']['parts'][0]['text'])
        else:
            st.error("مفتاح Gemini غير موجود!")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#475569;'>نظام المراقبة العسكري v2.2 | صنع لدعم راديو الصمود 🛰️</p>", unsafe_allow_html=True)
