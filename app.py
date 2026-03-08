import streamlit as st
import requests
import json
import feedparser
from datetime import datetime, timezone
from html.parser import HTMLParser

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="🛰️ وكيل الأخبار العسكري", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; }
.stApp { background: #04090f; color: #e2e8f0; }
h1,h2,h3,h4 { color: #38bdf8 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] {
    background-color: #0d1e30;
    border-radius: 5px;
    padding: 10px;
    color: white;
}
div[data-testid="metric-container"] {
    background: #0d1e30;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #1e3a5f;
}
</style>
""", unsafe_allow_html=True)

# --- 2. المفاتيح (تأكد من صحتها) ---
NEWS_KEY   = "2aff2eb940e54eb8bfb441c4ad07bbc1"
GEMINI_KEY = "AIzaSyBd9Y8Yc-nKvPRmQm_VlI-DqO-BPIPe4Ws"

# --- 3. الدوال الذكية (Gemini & Utils) ---

@st.cache_data(ttl=3600)  # تخزين النتائج لمدة ساعة لتوفير استهلاك الـ API
def ask_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ]

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": safety_settings
        }

        r = requests.post(url, json=payload, timeout=30)
        data = r.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        
        return f"⚠️ لم يتم إنشاء تحليل. السبب المحتمل: {data.get('error', {}).get('message', 'قيود أمنية أو تقنية')}"
    except Exception as e:
        return f"📡 خطأ في الاتصال بـ Gemini: {e}"

def translate_ar(text):
    if not text or not GEMINI_KEY: return text
    return ask_gemini(f"ترجم للعربية فقط بأسلوب إخباري رصين:\n{text}")

# --- 4. الهيدر (العنوان الرئيسي) ---
st.markdown("""
<div style='text-align:center;padding:20px;background:linear-gradient(135deg,#04090f,#0d1e30);border-radius:12px;margin-bottom:20px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>تطوير: مازن | نظام تحليل استخباراتي مدعوم بـ Gemini 2.0</p>
  <p style='color:#ef4444;font-size:12px;margin:0'>● مراقبة حية للخليج والشرق الأوسط</p>
</div>
""", unsafe_allow_html=True)

# --- 5. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    news_type = st.selectbox("نوع الأخبار:", ["الكل", "عسكري", "سياسي", "اقتصادي"])
    auto_translate = st.toggle("🌐 ترجمة عربية تلقائية", value=True)
    st.divider()
    st.info("هذا التطبيق مخصص للتحليل الإعلامي العسكري")

# --- 6. التببات الرئيسية (المحتوى) ---
TABS = st.tabs([
    "📰 أخبار اليوم", 
    "🤖 تحليل Gemini الشامل", 
    "🗺️ خريطة القصف",
    "📡 Telegram & RSS"
])

# -- التبابة 1: أخبار اليوم --
with TABS[0]:
    st.subheader("📰 آخر المستجدات الإقليمية")
    if st.button("🔄 تحديث الأخبار الآن", type="primary"):
        with st.spinner("جارٍ جلب الأخبار من NewsAPI..."):
            # هنا تضع دالة fetch_news الخاصة بك
            st.success("تم التحديث بنجاح (ملاحظة: تأكد من دمج دوال الجلب في ملفك)")

# -- التبابة 2: التحليل الذكي (الذي أصلحناه) --
with TABS[1]:
    st.subheader("🤖 مختبر التحليل الاستخباراتي")
    analysis_option = st.selectbox("اختر نوع التحليل:", [
        "📊 تقرير شامل عن الوضع العسكري الآن",
        "🎯 توقع الضربات القادمة في 48 ساعة",
        "🇴🇲 دور عُمان ومستوى أمانها"
    ])
    
    custom_q = st.text_input("أو اكتب سؤالك الخاص:")
    
    if st.button("🚀 ابدأ التحليل الشامل", use_container_width=True):
        final_query = custom_q if custom_q else analysis_option
        with st.spinner("🤖 Gemini يحلل البيانات ويقوم بإعداد التقرير..."):
            result = ask_gemini(final_query)
            st.markdown("---")
            st.markdown(f"### 📋 التقرير الناتح:\n{result}")

# -- التبابة 3: الخريطة --
with TABS[2]:
    st.subheader("🗺️ خريطة الأحداث العسكرية")
    st.info("هذا القسم يعرض مواقع القصف والاعتراضات الأخيرة")
    # هنا تضع كود الخريطة (Leaflet) الذي أرسلته سابقاً

# -- التبابة 4: المصادر الأخرى --
with TABS[3]:
    st.subheader("📡 مراقبة القنوات المفتوحة")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📡 Telegram Channels")
    with col2:
        st.write("📰 RSS Feeds")

# --- 7. التذييل (Footer) ---
st.markdown("---")
st.markdown("<div style='text-align:center;color:#475569;font-size:11px'>🛰️ وكيل الأخبار العسكري | النسخة 2.0 | سلطنة عُمان</div>", unsafe_allow_html=True)
