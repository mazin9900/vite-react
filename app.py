import streamlit as st
import requests
import json
import feedparser
from datetime import datetime, timezone
from html.parser import HTMLParser

# --- إعدادات الصفحة ---
st.set_page_config(page_title="🛰️ وكيل الأخبار العسكري", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; }
.stApp { background: #04090f; color: #e2e8f0; }
h1,h2,h3,h4 { color: #38bdf8 !important; }
div[data-testid="metric-container"] {
    background: #0d1e30;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #1e3a5f;
}
</style>
""", unsafe_allow_html=True)

# --- المفاتيح (تأكد من وضع مفاتيحك هنا) ---
NEWS_KEY   = "2aff2eb940e54eb8bfb441c4ad07bbc1"
GEMINI_KEY = "AIzaSyBd9Y8Yc-nKvPRmQm_VlI-DqO-BPIPe4Ws"

# --- دالة Gemini المحدثة مع التخزين المؤقت وفلاتر الأمان ---
@st.cache_data(ttl=3600)  # تخزين النتائج لمدة ساعة لتوفير الكريديت والسرعة
def ask_gemini(prompt):
    if not GEMINI_KEY or GEMINI_KEY.startswith("AIza"): # التحقق من وجود مفتاح
        pass
    else:
        return "❌ يرجى التأكد من مفتاح Gemini API"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        
        # إعدادات الأمان للسماح بتحليل الأخبار العسكرية دون حجب
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": safety_settings
        }

        r = requests.post(url, json=payload, timeout=30)
        data = r.json()

        # معالجة الاستجابة بأمان لتجنب خطأ 'candidates'
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
            else:
                return "⚠️ تم حجب المحتوى من قبل سياسات Google."
        elif "error" in data:
            return f"❌ خطأ من API: {data['error']['message']}"
        else:
            return "🔍 لم يتم العثور على تحليل دقيق لهذه البيانات."

    except Exception as e:
        return f"📡 خطأ في الاتصال: {str(e)}"

# --- الدوال المساعدة الأخرى (نفس منطقك السابق مع تحسينات بسيطة) ---

def translate_ar(text):
    if not text: return text
    return ask_gemini(f"ترجم للعربية فقط وبدقة إعلامية:\n{text}")

def detect_fake_news(title, content=""):
    prompt = f"""أنت خبير في كشف الأخبار المزيفة والدعاية الإعلامية في منطقة الخليج.
حلل الخبر التالي وأعطِ تقييماً دقيقاً بصيغة JSON فقط:
{{
  "fake_score": 0-100,
  "verdict": "حقيقي|مشبوه|مزيف",
  "reasons": ["سبب1","سبب2"],
  "warning": "تحذير قصير"
}}
الخبر: {title}
{content}"""
    result = ask_gemini(prompt)
    try:
        # تنظيف الاستجابة من علامات الكود
        clean = result.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return None

# --- [بقية الدوال: build_query, fetch_news, fetch_telegram, إلخ...] ---
# ملاحظة: استبدل استدعاء ask_gemini في كل مكان بـ ask_gemini المحدثة أعلاه.

# --- واجهة التطبيق الرئيسية ---
st.markdown("""
<div style='text-align:center;padding:15px;background:linear-gradient(135deg,#04090f,#0d1e30);border-radius:12px;margin-bottom:10px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>تطوير: مازن | نظام تحليل استخباراتي مدعوم بـ Gemini 2.0</p>
</div>
""", unsafe_allow_html=True)

# استكمل بقية التابات (TABS) كما هي في كودك الأصلي...
