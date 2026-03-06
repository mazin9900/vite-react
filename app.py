import streamlit as st
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone

st.set_page_config(page_title="🛰️ وكيل الأخبار العسكري", page_icon="🛰️", layout="wide")

# =========================
# CSS
# =========================
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

div.stButton > button {
    border-radius: 14px !important;
    border: 1px solid #1e3a5f !important;
    background: linear-gradient(135deg, #0b1220, #13263f) !important;
    color: #e2e8f0 !important;
    font-weight: 700 !important;
    min-height: 48px !important;
}

.live-header-card{
    background: linear-gradient(135deg, #07101b, #0d1e30);
    border: 1px solid #1e3a5f;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 18px;
}
.live-header-title{
    color:#38bdf8;
    font-size:28px;
    font-weight:900;
    margin-bottom:6px;
}
.live-header-sub{
    color:#94a3b8;
    font-size:13px;
    line-height:1.9;
}
.selected-channel-box{
    background: linear-gradient(135deg, #0b1626, #10243d);
    border: 1px solid #2563eb;
    border-radius: 16px;
    padding: 16px;
    margin: 14px 0 16px 0;
}
.small-note{
    color:#64748b;
    font-size:12px;
    text-align:center;
    margin-top:8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Secrets
# =========================
NEWS_KEY = st.secrets.get("NEWS_KEY", "")
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")

# =========================
# State
# =========================
defaults = {
    "articles": [],
    "rss": [],
    "reddit": [],
    "tg_msgs": [],
    "channel": "🌍 الجزيرة مباشر",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================
# Helpers
# =========================
def clean_html(text):
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

@st.cache_data(ttl=600)
def fetch_news(query, news_key):
    if not news_key:
        return []

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": news_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "from": today,
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        if data.get("status") != "ok":
            return []
        return data.get("articles", [])[:20]
    except:
        return []

@st.cache_data(ttl=900)
def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:8]:
            items.append({
                "title": getattr(e, "title", ""),
                "link": getattr(e, "link", "#"),
                "summary": clean_html(getattr(e, "summary", "")),
            })
        return items
    except:
        return []

@st.cache_data(ttl=900)
def fetch_reddit(sub, q):
    try:
        url = f"https://www.reddit.com/r/{sub}/search.json"
        params = {
            "q": q or "war missile strike",
            "sort": "new",
            "limit": 10,
            "restrict_sr": 1,
        }
        headers = {"User-Agent": "Mozilla/5.0 StreamlitApp/1.0"}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        data = r.json()
        return [p["data"] for p in data.get("data", {}).get("children", [])]
    except:
        return []

@st.cache_data(ttl=900)
def fetch_telegram(channel_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(channel_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        msgs = []
        blocks = soup.select(".tgme_widget_message_text")
        for block in blocks[:8]:
            txt = block.get_text(" ", strip=True)
            if txt:
                msgs.append(txt[:500])
        return msgs
    except:
        return []

def ask_gemini(prompt):
    if not GEMINI_KEY:
        return "مفتاح Gemini غير موجود"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=35)
        data = r.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return "تعذر الحصول على نتيجة من Gemini"

        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip() if parts else "لا يوجد نص في الرد"
    except Exception as e:
        return f"خطأ: {e}"

def build_query(regions, news_type, custom_query):
    rm = {
        "عُمان": "Oman",
        "الخليج العربي": "Gulf Saudi UAE Kuwait Qatar Bahrain",
        "إيران": "Iran",
        "إسرائيل": "Israel",
        "أمريكا": "US military Middle East",
        "اليمن": "Yemen Houthi",
        "العراق": "Iraq",
        "لبنان": "Lebanon Hezbollah",
    }
    tm = {
        "عسكري": "military OR strike OR missile OR war",
        "سياسي": "politics OR diplomacy OR government",
        "صواريخ وضربات": "missile OR strike OR bombing OR drone",
        "دبلوماسي": "diplomacy OR talks OR negotiations",
        "الكل": "war OR conflict OR military OR politics",
    }

    if custom_query:
        return custom_query

    rq = " OR ".join([rm.get(r, r) for r in regions]) if regions else "Middle East"
    tq = tm.get(news_type, "war OR conflict")
    return f"({rq}) AND ({tq})"

# =========================
# Data Sources
# =========================
RSS_SOURCES = {
    "🇮🇱 Times of Israel": "https://www.timesofisrael.com/feed/",
    "🇮🇱 Jerusalem Post": "https://www.jpost.com/rss/rssfeedsheadlines.aspx",
    "🇺🇸 Reuters": "https://feeds.reuters.com/reuters/topNews",
    "🇺🇸 Defense News": "https://www.defensenews.com/rss/",
    "🌍 Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
}

TELEGRAM_CHANNELS = {
    "🔴 قناة الميادين": "https://t.me/s/AlMayadeenNews",
    "⚡ أخبار سريعة": "https://t.me/s/breakingnewsar",
    "🇾🇪 أخبار اليمن": "https://t.me/s/yemenmoments",
    "⚔️ Intel Slava Z": "https://t.me/s/intelslava",
    "📡 War Monitor": "https://t.me/s/WarMonitor3",
}

# =========================
# Header
# =========================
st.markdown("""
<div style='text-align:center;padding:15px;background:linear-gradient(135deg,#04090f,#0d1e30);border-radius:12px;margin-bottom:10px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>أخبار اليوم · Telegram · Reddit · RSS · قنوات مباشرة · تحليل ذكي</p>
</div>
""", unsafe_allow_html=True)

# =========================
# Sidebar
# =========================
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
    enable_ai = st.toggle("🤖 تفعيل التحليل الذكي", value=False)

# =========================
# Tabs
# =========================
tabs = st.tabs([
    "📰 أخبار اليوم",
    "📡 Telegram",
    "🟠 Reddit",
    "📰 RSS",
    "📺 قنوات مباشرة",
    "🤖 تحليل ذكي",
])

# =========================
# Tab 1
# =========================
with tabs[0]:
    st.markdown("### 📰 أخبار اليوم")
    if st.button("🔄 تحديث الأخبار", use_container_width=True, type="primary"):
        query = build_query(regions, news_type, custom_query)
        st.session_state["articles"] = fetch_news(query, NEWS_KEY)

    if not st.session_state["articles"]:
        st.info("اضغط تحديث الأخبار")
    else:
        arts = st.session_state["articles"]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("عدد الأخبار", len(arts))
        with c2:
            st.metric("عدد المصادر", len(set(a.get("source", {}).get("name", "") for a in arts if a.get("source"))))
        with c3:
            st.metric("تاريخ اليوم", datetime.now().strftime("%Y-%m-%d"))

        st.markdown("---")

        for art in arts:
            title = art.get("title", "")
            desc = art.get("description", "") or ""
            source = art.get("source", {}).get("name", "غير معروف")
            pub = (art.get("publishedAt", "") or "")[:16].replace("T", " ")

            with st.container(border=True):
                a, b = st.columns([1, 3])
                with a:
                    if art.get("urlToImage"):
                        try:
                            st.image(art["urlToImage"], use_container_width=True)
                        except:
                            pass
                with b:
                    st.markdown(f"**{title}**")
                    st.caption(f"{source} | {pub}")
                    if desc:
                        st.write(desc)
                    if art.get("url"):
                        st.markdown(f"[🔗 اقرأ الخبر]({art['url']})")

# =========================
# Tab 2
# =========================
with tabs[1]:
    st.markdown("### 📡 Telegram")
    sel_tg = st.selectbox("اختر القناة:", list(TELEGRAM_CHANNELS.keys()))

    if st.button("📡 تحميل المنشورات", use_container_width=True, type="primary"):
        st.session_state["tg_msgs"] = fetch_telegram(TELEGRAM_CHANNELS[sel_tg])

    if not st.session_state["tg_msgs"]:
        st.info("اضغط تحميل المنشورات")
    else:
        for i, msg in enumerate(st.session_state["tg_msgs"], 1):
            with st.container(border=True):
                st.markdown(f"**منشور {i}**")
                st.write(msg)

# =========================
# Tab 3
# =========================
with tabs[2]:
    st.markdown("### 🟠 Reddit")
    subreddits = {
        "r/worldnews": "worldnews",
        "r/MiddleEast": "MiddleEast",
        "r/CombatFootage": "CombatFootage",
        "r/geopolitics": "geopolitics",
    }
    sel_sub = st.selectbox("اختر المنتدى:", list(subreddits.keys()))
    reddit_q = st.text_input("كلمة بحث:", value="Iran Israel missile strike")

    if st.button("🟠 تحميل Reddit", use_container_width=True, type="primary"):
        st.session_state["reddit"] = fetch_reddit(subreddits[sel_sub], reddit_q)

    if not st.session_state["reddit"]:
        st.info("اضغط تحميل Reddit")
    else:
        for post in st.session_state["reddit"]:
            with st.container(border=True):
                st.markdown(f"**{post.get('title', '')}**")
                st.caption(f"👍 {post.get('score', 0)} | 💬 {post.get('num_comments', 0)}")
                permalink = post.get("permalink", "")
                if permalink:
                    st.markdown(f"[🔗 فتح على Reddit](https://reddit.com{permalink})")

# =========================
# Tab 4
# =========================
with tabs[3]:
    st.markdown("### 📰 RSS")
    selected_sources = st.multiselect(
        "اختر المصادر:",
        list(RSS_SOURCES.keys()),
        default=list(RSS_SOURCES.keys())[:3]
    )

    if st.button("📡 تحميل RSS", use_container_width=True, type="primary"):
        all_rss = []
        for src in selected_sources:
            for item in fetch_rss(RSS_SOURCES[src]):
                all_rss.append({
                    "source": src,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "link": item.get("link", "#"),
                })
        st.session_state["rss"] = all_rss

    if not st.session_state["rss"]:
        st.info("اضغط تحميل RSS")
    else:
        for item in st.session_state["rss"]:
            with st.container(border=True):
                st.markdown(f"**{item['title']}**")
                st.caption(item["source"])
                if item["summary"]:
                    st.write(item["summary"][:220] + "...")
                st.markdown(f"[🔗 المصدر]({item['link']})")

# =========================
# Tab 5
# =========================
with tabs[4]:
    st.markdown("""
    <div class="live-header-card">
        <div class="live-header-title">📺 القنوات الإخبارية المباشرة</div>
        <div class="live-header-sub">
            اختر القناة من الشبكة أدناه لعرضها داخل التطبيق.
        </div>
    </div>
    """, unsafe_allow_html=True)

    channels = {
        "🌍 الجزيرة مباشر": {
            "embed": "https://www.aljazeera.net/video/live",
            "link": "https://www.aljazeera.net/video/live",
            "desc": "البث الرسمي لقناة الجزيرة مباشر",
            "group": "عربي"
        },
        "📺 العربية مباشر": {
            "embed": "https://www.alarabiya.net/live-stream",
            "link": "https://www.alarabiya.net/live-stream",
            "desc": "البث الرسمي لقناة العربية",
            "group": "عربي"
        },
        "📡 روسيا اليوم عربي": {
            "embed": "https://arabic.rt.com/live/",
            "link": "https://arabic.rt.com/live/",
            "desc": "البث الرسمي لروسيا اليوم عربي",
            "group": "عربي"
        },
        "🇸🇦 سكاي نيوز عربية": {
            "embed": "https://www.skynewsarabia.com/livestream-%D8%A7%D9%84%D8%A8%D8%AB-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B4%D8%B1",
            "link": "https://www.skynewsarabia.com/livestream-%D8%A7%D9%84%D8%A8%D8%AB-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B4%D8%B1",
            "desc": "البث الرسمي لسكاي نيوز عربية",
            "group": "عربي"
        },
        "📺 قناة الميادين": {
            "embed": "https://www.almayadeen.net/live",
            "link": "https://www.almayadeen.net/live",
            "desc": "البث الرسمي لقناة الميادين",
            "group": "عربي"
        },
        "🇬🇧 BBC News": {
            "embed": "https://www.bbc.com/news",
            "link": "https://www.bbc.com/news",
            "desc": "الصفحة الرسمية لـ BBC News",
            "group": "دولي"
        },
    }

    arabic_channels = [n for n, d in channels.items() if d["group"] == "عربي"]
    intl_channels = [n for n, d in channels.items() if d["group"] == "دولي"]

    st.markdown("#### 📰 القنوات العربية")
    cols1 = st.columns(3)
    for i, name in enumerate(arabic_channels):
        with cols1[i % 3]:
            label = f"✅ {name}" if st.session_state["channel"] == name else name
            if st.button(label, use_container_width=True, key=f"ar_{i}"):
                st.session_state["channel"] = name

    st.markdown("#### 🌐 القنوات الدولية")
    cols2 = st.columns(3)
    for i, name in enumerate(intl_channels):
        with cols2[i % 3]:
            label = f"✅ {name}" if st.session_state["channel"] == name else name
            if st.button(label, use_container_width=True, key=f"in_{i}"):
                st.session_state["channel"] = name

    selected = channels[st.session_state["channel"]]
    c1, c2 = st.columns([4, 1])

    with c1:
        st.markdown(f"""
        <div class="selected-channel-box">
            <b>📺 {st.session_state["channel"]}</b><br>
            <span style="color:#94a3b8;font-size:13px">{selected["desc"]}</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.link_button("🔗 الرابط الرسمي", selected["link"], use_container_width=True)

    st.components.v1.iframe(selected["embed"], height=720, scrolling=True)
    st.markdown('<div class="small-note">إذا لم يظهر البث داخل الإطار، افتح الرابط الرسمي.</div>', unsafe_allow_html=True)

# =========================
# Tab 6
# =========================
with tabs[5]:
    st.markdown("### 🤖 التحليل الذكي")

    if not enable_ai:
        st.info("فعّل التحليل الذكي من الشريط الجانبي")
    elif not GEMINI_KEY:
        st.warning("أضف مفتاح Gemini داخل secrets.toml")
    else:
        question = st.text_input("اكتب سؤالك:", placeholder="ما أبرز التهديدات الحالية؟")

        if st.button("🤖 ابدأ التحليل", use_container_width=True, type="primary"):
            context = ""

            if st.session_state["articles"]:
                context += "\nأخبار اليوم:\n" + "\n".join([f"- {a.get('title', '')}" for a in st.session_state["articles"][:6]])

            if st.session_state["rss"]:
                context += "\nRSS:\n" + "\n".join([f"- {i.get('title', '')}" for i in st.session_state["rss"][:5]])

            if st.session_state["reddit"]:
                context += "\nReddit:\n" + "\n".join([f"- {p.get('title', '')}" for p in st.session_state["reddit"][:5]])

            if st.session_state["tg_msgs"]:
                context += "\nTelegram:\n" + "\n".join([f"- {m[:120]}" for m in st.session_state["tg_msgs"][:3]])

            prompt = f"""
أنت محلل أخبار عسكرية.
اعتمد على البيانات التالية:
{context}

السؤال:
{question or "قدّم ملخصًا عامًا عن الوضع الحالي"}

أجب بالعربية بشكل منظم ومباشر.
"""
            with st.spinner("جارٍ التحليل..."):
                result = ask_gemini(prompt)
                st.write(result)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#475569;font-size:11px'>🛰️ وكيل الأخبار العسكري - نسخة خفيفة وسريعة</div>",
    unsafe_allow_html=True
)
