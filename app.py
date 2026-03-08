import streamlit as st
import requests
import json
import feedparser
from datetime import datetime, timezone

st.set_page_config(page_title="🛰️ وكيل الأخبار العسكري", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; }
.stApp { background: #04090f; color: #e2e8f0; }
h1,h2,h3,h4 { color: #38bdf8 !important; }
div[data-testid="metric-container"] { background: #0d1e30; border-radius:10px; padding:10px; border:1px solid #1e3a5f; }
</style>
""", unsafe_allow_html=True)

NEWS_KEY   = "2aff2eb940e54eb8bfb441c4ad07bbc1"
GEMINI_KEY = "AIzaSyDuOADJ6YDyqBjOYFC2x-0ql1hgb0kIWaQ"

st.markdown("""
<div style='text-align:center;padding:15px;background:linear-gradient(135deg,#04090f,#0d1e30);border-radius:12px;margin-bottom:10px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>الخليج · إيران · إسرائيل · أمريكا | Telegram | Reddit | كشف الأخبار المزيفة</p>
  <p style='color:#ef4444;font-size:12px;margin:0'>● أخبار اليوم فقط</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌍 المناطق")
    regions = st.multiselect(
        "اختر:",
        ["عُمان","الخليج العربي","إيران","إسرائيل","أمريكا","اليمن","العراق","لبنان"],
        default=["عُمان","الخليج العربي","إيران","إسرائيل"]
    )
    st.markdown("---")
    news_type = st.selectbox("نوع الأخبار:", ["الكل","عسكري","سياسي","صواريخ وضربات","دبلوماسي"])
    st.markdown("---")
    custom_query = st.text_input("🔍 بحث:", placeholder="صواريخ حوثية...")
    st.markdown("---")
    auto_translate = st.toggle("🌐 ترجمة عربية تلقائية", value=True)


def ask_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"خطأ: {e}"


def translate_ar(text):
    if not text or GEMINI_KEY.startswith("ضع"):
        return text
    return ask_gemini(f"ترجم للعربية فقط بدون شرح:\n{text}")


# -----------------------------
# تحسين بناء الاستعلام
# -----------------------------
def build_query():
    region_map = {
        "عُمان": '"Oman" OR "Muscat"',
        "الخليج العربي": '"Gulf" OR "Saudi Arabia" OR "UAE" OR "Qatar" OR "Bahrain" OR "Kuwait"',
        "إيران": '"Iran"',
        "إسرائيل": '"Israel"',
        "أمريكا": '"United States" OR "US military" OR "Pentagon"',
        "اليمن": '"Yemen" OR "Houthis" OR "Houthi"',
        "العراق": '"Iraq"',
        "لبنان": '"Lebanon" OR "Hezbollah"'
    }

    type_map = {
        "عسكري": '"military" OR "army" OR "airstrike" OR "strike" OR "missile" OR "drone"',
        "سياسي": '"politics" OR "government" OR "minister" OR "president"',
        "صواريخ وضربات": '"missile" OR "rocket" OR "strike" OR "bombing" OR "drone attack"',
        "دبلوماسي": '"diplomacy" OR "talks" OR "ceasefire" OR "negotiation"',
        "الكل": '"war" OR "conflict" OR "military" OR "politics"'
    }

    if custom_query.strip():
        return custom_query.strip()

    selected_regions = [region_map[r] for r in regions if r in region_map]
    region_part = " OR ".join(selected_regions) if selected_regions else '"Middle East"'
    type_part = type_map.get(news_type, '"war" OR "conflict"')

    return f"({region_part}) AND ({type_part})"


# -----------------------------
# تنظيف النتائج
# -----------------------------
def normalize_articles(articles):
    clean = []
    seen = set()

    for a in articles:
        title = (a.get("title") or "").strip()
        url = (a.get("url") or "").strip()

        if not title or title == "[Removed]" or not url:
            continue

        key = (title.lower(), url)
        if key in seen:
            continue
        seen.add(key)

        clean.append(a)

    return clean


# -----------------------------
# جلب الأخبار مع fallback
# -----------------------------
def fetch_news(query):
    if not NEWS_KEY or NEWS_KEY.startswith("ضع"):
        return []

    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url_everything = "https://newsapi.org/v2/everything"
    url_top = "https://newsapi.org/v2/top-headlines"

    headers = {
        "X-Api-Key": NEWS_KEY,
        "User-Agent": "Mozilla/5.0"
    }

    # المحاولة الأولى: everything
    params_everything = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
        "from": today_utc,
        "searchIn": "title,description"
    }

    try:
        r = requests.get(url_everything, headers=headers, params=params_everything, timeout=20)
        data = r.json()

        if data.get("status") == "ok":
            articles = normalize_articles(data.get("articles", []))

            today_articles = [
                a for a in articles
                if (a.get("publishedAt") or "")[:10] == today_utc
            ]

            if today_articles:
                return today_articles

            if articles:
                return articles[:15]
    except Exception:
        pass

    # المحاولة الثانية: top-headlines
    try:
        params_top = {
            "category": "general",
            "language": "en",
            "pageSize": 20
        }
        r = requests.get(url_top, headers=headers, params=params_top, timeout=20)
        data = r.json()

        if data.get("status") == "ok":
            articles = normalize_articles(data.get("articles", []))

            # تصفية بسيطة حسب الكلمات المفتاحية
            q_words = [w.strip().lower() for w in query.replace("(", "").replace(")", "").replace('"', "").split() if len(w.strip()) > 2]

            filtered = []
            for a in articles:
                hay = f"{a.get('title','')} {a.get('description','')}".lower()
                if any(word in hay for word in q_words[:8]):
                    filtered.append(a)

            if filtered:
                return filtered[:15]

            return articles[:10]
    except Exception:
        pass

    return []


# -----------------------------
# واجهة التبويب
# -----------------------------
TABS = st.tabs(["📰 أخبار اليوم"])

with TABS[0]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f"### 📰 أخبار اليوم فقط — {today_str}")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        if st.button("🔄 تحديث أخبار اليوم", use_container_width=True, type="primary"):
            with st.spinner("جارٍ تحميل أخبار اليوم..."):
                query = build_query()
                st.session_state["articles"] = fetch_news(query)
                st.session_state["last_query"] = query

    with col_btn2:
        if st.button("🧹 مسح النتائج", use_container_width=True):
            st.session_state["articles"] = []

    if "articles" not in st.session_state:
        st.session_state["articles"] = []

    arts = st.session_state["articles"]

    if st.session_state.get("last_query"):
        st.caption(f"الاستعلام المستخدم: {st.session_state['last_query']}")

    if not arts:
        st.warning("لا توجد نتائج حالياً. جرّب تغيير المناطق أو نوع الأخبار أو كتابة بحث مخصص.")
    else:
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("📰 أخبار اليوم", len(arts))

        with c2:
            st.metric(
                "🌐 مصادر",
                len(set(a.get("source", {}).get("name", "غير معروف") for a in arts))
            )

        with c3:
            urgent_count = sum(
                1 for a in arts
                if any(w in (a.get("title", "") or "").lower() for w in ["breaking", "attack", "strike", "missile", "war", "explosion"])
            )
            st.metric("🔴 عاجل", urgent_count)

        with c4:
            st.metric("📅 التاريخ", today_str)

        st.markdown("---")

        for i, art in enumerate(arts[:20], start=1):
            title = art.get("title", "")
            desc = art.get("description", "") or ""
            pub = (art.get("publishedAt", "") or "")[:16].replace("T", " ")
            source_name = art.get("source", {}).get("name", "مصدر غير معروف")

            show_title = title
            show_desc = desc

            if auto_translate and not GEMINI_KEY.startswith("ضع"):
                try:
                    show_title = translate_ar(title)
                    if desc:
                        show_desc = translate_ar(desc)
                except Exception:
                    show_title = title
                    show_desc = desc

            is_breaking = any(
                w in title.lower()
                for w in ["breaking", "attack", "strike", "missile", "war", "explosion"]
            )

            with st.container():
                img_col, text_col = st.columns([1, 3])

                with img_col:
                    if art.get("urlToImage"):
                        try:
                            st.image(art["urlToImage"], use_container_width=True)
                        except Exception:
                            pass

                with text_col:
                    if is_breaking:
                        st.error(f"🔴 عاجل | {source_name} | {pub}")
                    else:
                        st.info(f"📰 {source_name} | {pub}")

                    st.markdown(f"**{show_title}**")

                    if show_desc:
                        st.caption(show_desc)

                    st.markdown(f"[🔗 اقرأ كاملاً]({art.get('url', '#')})")

            st.divider()
