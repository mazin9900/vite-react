import streamlit as st
import requests
import json
from datetime import datetime
import base64
from gtts import gTTS
import io

# إعدادات الواجهة
st.set_page_config(page_title="🛰️ رادار الخليج والشرق الأوسط", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; direction: rtl; }
.stApp { background: #010409; color: #e6edf3; }
.critical-alert { background: #4a0000; border: 2px solid #ff0000; padding: 15px; border-radius: 12px; margin: 10px 0; animation: blinker 2s linear infinite; }
@keyframes blinker { 50% { opacity: 0.7; } }
.country-tag { background: #1f6feb; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px; margin-left: 5px; }
</style>
""", unsafe_allow_html=True)

GEMINI_KEY = "AIzaSyDuOADJ6YDyqBjOYFC2x-0ql1hgb0kIWaQ"
NEWS_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"

# --- قائمة الكلمات والمناطق الحرجة ---
CRITICAL_WORDS = [
    "انفجار", "هجوم", "قصف", "صواريخ", "ضربة", "حرب", "اشتباك", "تسلل",
    "عمان", "مسقط", "الكويت", "الإمارات", "السعودية", "الرياض", "قطر", "الدوحة",
    "البحرين", "المنامة", "إيران", "طهران", "إسرائيل", "تل أبيب", "القدس"
]

def play_military_alarm():
    # صوت إنذار عسكري حاد
    audio_url = "https://www.soundjay.com/buttons/beep-01a.mp3"
    st.markdown(f'<audio autoplay><source src="{audio_url}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

def ask_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=10)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return "خطأ في الاتصال."

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align:center; color:#ff4b4b;'>🚨 نظام الإنذار المبكر للمنطقة</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>مراقبة نشطة: دول الخليج | إيران | إسرائيل</p>", unsafe_allow_html=True)

# جلب الأخبار
st.subheader("📡 التغذية الإخبارية الفورية")
query = "(Oman OR Kuwait OR UAE OR Saudi OR Qatar OR Bahrain OR Iran OR Israel) AND (military OR attack OR explosion)"
news_url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_KEY}&sortBy=publishedAt&pageSize=6"

try:
    articles = requests.get(news_url).json().get("articles", [])
    
    for art in articles:
        # ترجمة العنوان للعربية للبحث عن الكلمات الحرجة
        title_ar = ask_gemini(f"ترجم بدقة للعربية: {art['title']}")
        
        # التحقق من وجود كلمة حرجة
        found_critical = any(word in title_ar for word in CRITICAL_WORDS)
        
        if found_critical:
            st.markdown(f"""
            <div class="critical-alert">
                <h3 style="margin:0;">⚠️ تنبيه عاجل: {title_ar}</h3>
                <p style="margin:5px 0 0 0; font-size:14px;">المصدر: {art['source']['name']} | الحساسية: عالية 🔴</p>
            </div>
            """, unsafe_allow_html=True)
            play_military_alarm() # إطلاق صوت البييب
        else:
            with st.expander(f"🔹 {title_ar}"):
                st.write(f"المصدر: {art['source']['name']}")
                st.write(f"[رابط الخبر الأصلي]({art['url']})")

except Exception as e:
    st.error("يرجى التأكد من مفاتيح الـ API.")

# --- قسم الخريطة والتحليل ---
col1, col2 = st.columns([2, 1])
with col1:
    st.info("📍 يتم الآن مراقبة إحداثيات (مضيق هرمز، القواعد الجوية، والمطارات الدولية) في الدول المذكورة.")
    # خريطة مبسطة
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Middle_East_map.png/800px-Middle_East_map.png", caption="رادار التغطية الإقليمي")

with col2:
    st.subheader("🕵️ كاشف الزيف")
    check_input = st.text_area("ضع الخبر هنا للفحص:")
    if st.button("تحليل"):
        res = ask_gemini(f"هل هذا الخبر عن {', '.join(CRITICAL_WORDS[:10])} حقيقي أم إشاعة؟ حلل عسكرياً: {check_input}")
        st.write(res)

st.markdown("---")
st.caption("نظام وكيل الأخبار العسكري الذكي - تحديث مباشر 2026")
