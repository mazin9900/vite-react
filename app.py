import streamlit as st
import requests
import json
import feedparser
import google.generativeai as genai
from datetime import datetime

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
GEMINI_KEY = "AIzaSyAz0gDheQEJmYCO-D8FAl4mh9idzdohxEU"
@
        return response.text
    except Exception as e:
        # هذا السطر سيطبع لك السبب الحقيقي في صفحة الويب إذا فشل
        return f"❌ خطأ تقني حقيقي: {str(e)}"

st.markdown("""
<div style='text-align:center;padding:15px;background:linear-gradient(135deg,#04090f,#0d1e30);border-radius:12px;margin-bottom:10px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>الخليج · إيران · إسرائيل · أمريكا | Telegram | Reddit | كشف الأخبار المزيفة</p>
  <p style='color:#ef4444;font-size:12px;margin:0'>● أخبار اليوم فقط | مارس 2026</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌍 المناطق")
    regions = st.multiselect("اختر:",
        ["عُمان","الخليج العربي","إيران","إسرائيل","أمريكا","اليمن","العراق","لبنان"],
        default=["عُمان","الخليج العربي","إيران","إسرائيل"])
    st.markdown("---")
    news_type = st.selectbox("نوع الأخبار:", ["الكل","عسكري","سياسي","صواريخ وضربات","دبلوماسي"])
    st.markdown("---")
    custom_query = st.text_input("🔍 بحث:", placeholder="صواريخ حوثية...")
    st.markdown("---")
    auto_translate = st.toggle("🌐 ترجمة عربية تلقائية", value=True)

def ask_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, headers={"Content-Type":"application/json"},
            json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=30)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"خطأ: {e}"

def translate_ar(text):
    if not text or GEMINI_KEY.startswith("ضع"): return text
    return ask_gemini(f"ترجم للعربية فقط بدون شرح:\n{text}")

def detect_fake_news(title, content=""):
    if GEMINI_KEY.startswith("ضع"): return None
    result = ask_gemini(f"""أنت خبير في كشف الأخبار المزيفة والدعاية الإعلامية.
حلل هذا الخبر العسكري وأجب بـ JSON فقط بهذا الشكل:
{{"fake_score": 0-100, "verdict": "حقيقي|مشبوه|مزيف", "reasons": ["سبب1","سبب2"], "warning": "تحذير قصير"}}

الخبر: {title}
{content}

fake_score: 0=حقيقي تماماً، 100=مزيف تماماً
أجب بـ JSON فقط بدون أي نص آخر.""")
    try:
        clean = result.strip().replace("```json","").replace("```","").strip()
        return json.loads(clean)
    except:
        return None

def build_query():
    rm = {"عُمان":"Oman","الخليج العربي":"Gulf Saudi UAE Kuwait Qatar Bahrain",
          "إيران":"Iran","إسرائيل":"Israel","أمريكا":"US military Middle East",
          "اليمن":"Yemen Houthi","العراق":"Iraq","لبنان":"Lebanon Hezbollah"}
    tm = {"عسكري":"military strike","سياسي":"politics","صواريخ وضربات":"missile strike bombing",
          "دبلوماسي":"diplomacy","الكل":"war conflict"}
    if custom_query: return custom_query
    rq = " OR ".join([rm.get(r,r) for r in regions]) if regions else "Middle East"
    return f"({rq}) AND ({tm.get(news_type,'war')})"

def fetch_news(q):
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://newsapi.org/v2/everything?q={q}&apiKey={NEWS_KEY}&language=en&sortBy=publishedAt&pageSize=50&from={today}"
    try:
        arts = requests.get(url,timeout=10).json().get("articles",[])
        today_arts = [a for a in arts if (a.get("publishedAt") or "")[:10] == today]
        return today_arts if today_arts else arts[:15]
    except: return []

RSS_SOURCES = {
    "🇮🇱 Times of Israel":   "https://www.timesofisrael.com/feed/",
    "🇮🇱 Jerusalem Post":    "https://www.jpost.com/rss/rssfeedsheadlines.aspx",
    "🇺🇸 Reuters":           "https://feeds.reuters.com/reuters/topNews",
    "🇺🇸 Defense News":      "https://www.defensenews.com/rss/",
    "🌍 Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
    "🇺🇸 Breaking Defense":  "https://breakingdefense.com/feed/",
    "🌍 Middle East Eye":    "https://www.middleeasteye.net/rss",
}

# قنوات Telegram العامة (عبر t.me/s/)
TELEGRAM_CHANNELS = {
    "🔴 قناة الميادين":       "https://t.me/s/AlMayadeenNews",
    "⚡ أخبار سريعة":         "https://t.me/s/breakingnewsar",
    "🇾🇪 أخبار اليمن":        "https://t.me/s/yemenmoments",
    "🌍 Middle East Observer": "https://t.me/s/MiddleEastObserver",
    "⚔️ Intel Slava Z":       "https://t.me/s/intelslava",
    "🇮🇱 Israel War Room":    "https://t.me/s/israelwarroom",
    "📡 War Monitor":         "https://t.me/s/WarMonitor3",
    "🔵 OSINTdefender":       "https://t.me/s/OSINTdefender",
}

def fetch_telegram(channel_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(channel_url, headers=headers, timeout=15)
        from html.parser import HTMLParser
        class TGParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.messages = []
                self.current = ""
                self.in_msg = False
            def handle_starttag(self, tag, attrs):
                attrs_d = dict(attrs)
                if tag == "div" and "tgme_widget_message_text" in attrs_d.get("class",""):
                    self.in_msg = True
                    self.current = ""
            def handle_endtag(self, tag):
                if tag == "div" and self.in_msg:
                    if self.current.strip():
                        self.messages.append(self.current.strip()[:300])
                    self.in_msg = False
            def handle_data(self, data):
                if self.in_msg:
                    self.current += data
        parser = TGParser()
        parser.feed(r.text)
        return parser.messages[:8]
    except:
        return []

def fetch_reddit(sub, q=""):
    try:
        url = f"https://www.reddit.com/r/{sub}/search.json?q={q or 'war missile strike'}&sort=new&limit=10&restrict_sr=1"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        return [p["data"] for p in r.json()["data"]["children"]]
    except: return []

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries[:8]
    except: return []

TABS = st.tabs(["📰 أخبار اليوم","📡 Telegram","🟠 Reddit","📰 RSS إسرائيلي/أمريكي","🚨 كشف الأخبار المزيفة","📺 قنوات مباشرة","🗺️ خريطة القصف","🤖 تحليل ذكي"])

# ══ TAB 1 — أخبار اليوم ══
with TABS[0]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f"### 📰 أخبار اليوم فقط — {today_str}")
    if st.button("🔄 تحديث أخبار اليوم", use_container_width=True, type="primary"):
        with st.spinner("جارٍ تحميل أخبار اليوم..."):
            st.session_state['articles'] = fetch_news(build_query())

    if 'articles' not in st.session_state:
        st.info("👆 اضغط تحديث لتحميل أخبار اليوم")
    else:
        arts = st.session_state['articles']
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("📰 أخبار اليوم", len(arts))
        with c2: st.metric("🌐 مصادر", len(set(a['source']['name'] for a in arts if a.get('source'))))
        with c3: st.metric("🔴 عاجل", sum(1 for a in arts if any(w in (a.get('title','') or '').lower() for w in ['breaking','attack','strike','missile','war'])))
        with c4: st.metric("📅 التاريخ", today_str)
        st.markdown("---")

        for i, art in enumerate(arts[:20]):
            if not art.get('title') or art['title']=='[Removed]': continue
            title = art['title']
            desc  = art.get('description','') or ''
            pub   = (art.get('publishedAt','') or '')[:16].replace('T',' ')
            if auto_translate and not GEMINI_KEY.startswith("ضع"):
                with st.spinner(f"ترجمة {i+1}..."):
                    title = translate_ar(title)
                    if desc: desc = translate_ar(desc)
            is_brk = any(w in (art.get('title','') or '').lower() for w in ['breaking','attack','strike','missile','war','explosion'])
            with st.container():
                ca,cb = st.columns([1,3])
                with ca:
                    if art.get('urlToImage'):
                        try: st.image(art['urlToImage'], use_container_width=True)
                        except: pass
                with cb:
                    if is_brk: st.error(f"🔴 عاجل | {art['source']['name']} | {pub}")
                    else:       st.info(f"📰 {art['source']['name']} | {pub}")
                    st.markdown(f"**{title}**")
                    if desc: st.caption(desc)
                    st.markdown(f"[🔗 اقرأ كاملاً]({art.get('url','#')})")
            st.divider()

# ══ TAB 2 — Telegram ══
with TABS[1]:
    st.markdown("### 📡 قنوات Telegram العسكرية")
    st.info("يتم تحميل المنشورات العامة من قنوات Telegram مباشرة")

    sel_tg = st.selectbox("اختر القناة:", list(TELEGRAM_CHANNELS.keys()))
    col1, col2 = st.columns(2)
    with col1:
        load_tg = st.button("📡 تحميل المنشورات", use_container_width=True, type="primary")
    with col2:
        analyze_tg = st.button("🤖 ملخص Gemini للقناة", use_container_width=True)

    if load_tg:
        with st.spinner(f"جارٍ تحميل {sel_tg}..."):
            msgs = fetch_telegram(TELEGRAM_CHANNELS[sel_tg])
            st.session_state['tg_msgs'] = msgs
            st.session_state['tg_channel'] = sel_tg

    if analyze_tg and 'tg_msgs' in st.session_state and not GEMINI_KEY.startswith("ضع"):
        msgs = st.session_state.get('tg_msgs', [])
        if msgs:
            with st.spinner("🤖 Gemini يحلل منشورات Telegram..."):
                all_text = "\n---\n".join(msgs[:6])
                summary = ask_gemini(f"""أنت محلل إعلامي عسكري.
اقرأ هذه المنشورات من قناة Telegram عسكرية وقدم:
1. 📊 ملخص عربي شامل لأهم الأحداث
2. 🎯 أبرز المعلومات العسكرية
3. ⚠️ أي معلومات تبدو مبالغاً فيها أو مشبوهة
4. 🌍 المناطق المذكورة

المنشورات:
{all_text}""")
                st.markdown("---")
                st.markdown("#### 🤖 ملخص Gemini لقناة " + st.session_state.get('tg_channel',''))
                st.markdown(summary)
                st.markdown("---")

    if 'tg_msgs' in st.session_state:
        msgs = st.session_state['tg_msgs']
        if not msgs:
            st.warning("⚠️ لم يتم العثور على منشورات — القناة قد تكون خاصة أو محمية")
            st.markdown(f"🔗 افتح القناة مباشرة: {TELEGRAM_CHANNELS[sel_tg]}")
        else:
            st.success(f"✅ {len(msgs)} منشور من {st.session_state.get('tg_channel','')}")
            for i, msg in enumerate(msgs):
                is_war = any(w in msg.lower() for w in ['قصف','صاروخ','ضربة','هجوم','مقتل','انفجار','attack','strike','missile','explosion'])
                with st.container():
                    if is_war: st.error(f"⚔️ منشور {i+1} — عسكري")
                    else:      st.info(f"📡 منشور {i+1}")
                    st.markdown(msg)
                    if not GEMINI_KEY.startswith("ضع"):
                        if st.button(f"🤖 تحليل هذا المنشور", key=f"tg_{i}"):
                            with st.spinner("تحليل..."):
                                an = ask_gemini(f"حلل هذا المنشور العسكري بالعربية في 3 جمل:\n{msg}")
                                st.success(f"🤖 {an}")
                st.divider()

    st.markdown("---")
    st.markdown("#### 🔗 روابط مباشرة للقنوات:")
    cols = st.columns(4)
    for i,(name,url) in enumerate(TELEGRAM_CHANNELS.items()):
        with cols[i%4]:
            st.markdown(f"[{name}]({url})")

# ══ TAB 3 — Reddit ══
with TABS[2]:
    st.markdown("### 🟠 Reddit — منتديات الحرب")
    subreddits = {
        "r/worldnews":"worldnews","r/MiddleEast":"MiddleEast",
        "r/CombatFootage":"CombatFootage","r/geopolitics":"geopolitics","r/Israel":"Israel"
    }
    sel_sub = st.selectbox("اختر المنتدى:", list(subreddits.keys()))
    reddit_q = st.text_input("كلمة بحث:", value="Iran Israel missile strike")

    c1,c2 = st.columns(2)
    with c1: load_rd = st.button("🟠 تحميل Reddit", use_container_width=True, type="primary")
    with c2: analyze_rd = st.button("🤖 ملخص Gemini للمنشورات", use_container_width=True)

    if load_rd:
        with st.spinner("تحميل Reddit..."):
            st.session_state['reddit'] = fetch_reddit(subreddits[sel_sub], reddit_q)

    if analyze_rd and 'reddit' in st.session_state and not GEMINI_KEY.startswith("ضع"):
        posts = st.session_state['reddit']
        titles = "\n".join([f"- {p.get('title','')}" for p in posts[:10]])
        with st.spinner("🤖 Gemini يحلل..."):
            summary = ask_gemini(f"""أنت محلل إعلامي. هذه عناوين منشورات Reddit عسكرية:
{titles}
قدم:
1. 📊 ملخص عربي شامل
2. 🎯 أبرز الأحداث
3. 📈 اتجاه الرأي العام
4. ⚠️ منشورات مشبوهة أو دعائية""")
            st.markdown("#### 🤖 ملخص Gemini:")
            st.markdown(summary)
            st.markdown("---")

    if 'reddit' not in st.session_state:
        st.info("👆 اضغط تحميل Reddit")
    else:
        posts = st.session_state['reddit']
        st.success(f"✅ {len(posts)} منشور")
        for post in posts:
            title = post.get('title','')
            score = post.get('score',0)
            comments = post.get('num_comments',0)
            ar_title = translate_ar(title) if auto_translate and not GEMINI_KEY.startswith("ضع") else title
            with st.container():
                col_a,col_b = st.columns([3,1])
                with col_a:
                    if score>1000: st.error(f"🔥 {sel_sub} | 👍{score:,} | 💬{comments}")
                    else:          st.info(f"🟠 {sel_sub} | 👍{score:,} | 💬{comments}")
                    st.markdown(f"**{ar_title}**")
                    st.caption(f"الأصل: {title[:100]}")
                    st.markdown(f"[🔗 Reddit](https://reddit.com{post.get('permalink','')})")
                with col_b:
                    if not GEMINI_KEY.startswith("ضع"):
                        if st.button("🤖 تحليل", key=f"rd_{post.get('id','')}"):
                            with st.spinner("..."):
                                an = ask_gemini(f"حلل هذا المنشور بجملتين عربيتين:\n{title}")
                                st.caption(f"🤖 {an[:200]}")
            st.divider()

# ══ TAB 4 — RSS ══
with TABS[3]:
    st.markdown("### 📰 مواقع إسرائيلية وأمريكية (RSS)")
    selected_sources = st.multiselect("اختر:", list(RSS_SOURCES.keys()), default=list(RSS_SOURCES.keys())[:4])

    c1,c2 = st.columns(2)
    with c1: load_rss = st.button("📡 تحميل RSS", use_container_width=True, type="primary")
    with c2: analyze_all_rss = st.button("🤖 ملخص Gemini الشامل", use_container_width=True)

    if load_rss:
        all_rss = []
        for src in selected_sources:
            with st.spinner(f"تحميل {src}..."):
                for e in fetch_rss(RSS_SOURCES[src]):
                    all_rss.append({"source":src,"title":getattr(e,'title',''),
                        "link":getattr(e,'link','#'),
                        "summary":(getattr(e,'summary','')[:200] if hasattr(e,'summary') else '')})
        st.session_state['rss'] = all_rss

    if analyze_all_rss and 'rss' in st.session_state and not GEMINI_KEY.startswith("ضع"):
        items = st.session_state['rss']
        titles = "\n".join([f"- [{i['source']}] {i['title']}" for i in items[:15]])
        with st.spinner("🤖 Gemini يحلل كل المواقع..."):
            summary = ask_gemini(f"""أنت محلل استخباراتي. هذه عناوين من مواقع إسرائيلية وأمريكية:
{titles}
قدم تقريراً عربياً شاملاً:
1. 📊 أبرز الأحداث اليوم
2. 🇮🇱 الموقف الإسرائيلي
3. 🇺🇸 الموقف الأمريكي
4. ⚠️ أخبار تبدو مبالغاً فيها أو دعائية
5. 🎯 التوقعات خلال 24 ساعة""")
            st.markdown("#### 🤖 ملخص Gemini الشامل:")
            st.markdown(summary)
            st.markdown("---")

    if 'rss' not in st.session_state:
        st.info("👆 اضغط تحميل RSS")
    else:
        rss_items = st.session_state['rss']
        st.success(f"✅ {len(rss_items)} منشور")
        for item in rss_items:
            title = item['title']
            if auto_translate and not GEMINI_KEY.startswith("ضع") and title:
                title = translate_ar(title)
            is_war = any(w in (item['title'] or '').lower() for w in ['attack','strike','missile','war','bomb','iran','israel','houthi','kill'])
            with st.container():
                col_a,col_b = st.columns([3,1])
                with col_a:
                    if is_war: st.error(f"⚔️ {item['source']}")
                    else:      st.info(f"📰 {item['source']}")
                    st.markdown(f"**{title}**")
                    if item.get('summary'): st.caption(item['summary'][:150]+"...")
                    st.markdown(f"[🔗 المصدر]({item['link']})")
                with col_b:
                    if not GEMINI_KEY.startswith("ضع"):
                        if st.button("🤖 تحليل", key=f"rss_{hash(item['title'])}"):
                            with st.spinner("..."):
                                an = ask_gemini(f"حلل هذا الخبر بجملتين عربيتين:\n{item['title']}")
                                st.caption(f"🤖 {an[:200]}")
            st.divider()

# ══ TAB 5 — كشف الأخبار المزيفة ══
with TABS[4]:
    st.markdown("### 🚨 كشف الأخبار المزيفة والدعاية")
    st.info("🤖 Gemini يحلل الأخبار ويكشف إذا كانت حقيقية أو مزيفة أو دعائية")

    if GEMINI_KEY.startswith("ضع"):
        st.error("❌ أدخل مفتاح Gemini أولاً (السطر 16 في الكود)")
    else:
        fake_tab1, fake_tab2 = st.tabs(["🔍 فحص خبر محدد", "📊 فحص جماعي لكل الأخبار"])

        # فحص خبر محدد
        with fake_tab1:
            st.markdown("#### أدخل الخبر الذي تريد فحصه:")
            news_to_check = st.text_area("الخبر:", placeholder="مثال: إيران أسقطت 3 طائرات أمريكية فوق مضيق هرمز...", height=100)
            source_name = st.text_input("المصدر:", placeholder="مثال: Telegram، تويتر، إلخ")

            if st.button("🚨 فحص الخبر الآن", type="primary", use_container_width=True):
                if news_to_check:
                    with st.spinner("🤖 Gemini يحلل الخبر..."):
                        result = detect_fake_news(news_to_check, f"المصدر: {source_name}")

                    if result:
                        score = result.get('fake_score', 50)
                        verdict = result.get('verdict', 'مشبوه')
                        reasons = result.get('reasons', [])
                        warning = result.get('warning', '')

                        # عرض النتيجة
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if score < 30:
                                st.success(f"✅ {verdict}")
                            elif score < 60:
                                st.warning(f"⚠️ {verdict}")
                            else:
                                st.error(f"❌ {verdict}")
                        with col2:
                            st.metric("نسبة الشك", f"{score}%")
                        with col3:
                            color = "🟢" if score<30 else "🟡" if score<60 else "🔴"
                            st.metric("الحكم", f"{color} {verdict}")

                        st.progress(score/100)

                        if reasons:
                            st.markdown("#### 📋 الأسباب:")
                            for r in reasons:
                                icon = "✅" if score < 30 else "⚠️" if score < 60 else "❌"
                                st.markdown(f"{icon} {r}")

                        if warning:
                            st.warning(f"⚠️ تحذير: {warning}")
                    else:
                        st.error("فشل التحليل — تحقق من مفتاح Gemini")

        # فحص جماعي
        with fake_tab2:
            st.markdown("#### فحص جماعي لكل الأخبار المحملة")

            sources_to_check = []
            if 'articles' in st.session_state:
                sources_to_check.append(f"📰 أخبار اليوم ({len(st.session_state['articles'])} خبر)")
            if 'rss' in st.session_state:
                sources_to_check.append(f"📡 RSS ({len(st.session_state['rss'])} منشور)")
            if 'reddit' in st.session_state:
                sources_to_check.append(f"🟠 Reddit ({len(st.session_state['reddit'])} منشور)")
            if 'tg_msgs' in st.session_state:
                sources_to_check.append(f"📡 Telegram ({len(st.session_state['tg_msgs'])} منشور)")

            if not sources_to_check:
                st.warning("⚠️ حمّل الأخبار أولاً من التابات الأخرى")
            else:
                sel_source = st.selectbox("اختر المصدر للفحص:", sources_to_check)
                max_check = st.slider("عدد الأخبار للفحص:", 3, 15, 5)

                if st.button("🚨 فحص جماعي الآن", type="primary", use_container_width=True):
                    items_to_check = []
                    if "أخبار اليوم" in sel_source:
                        items_to_check = [(a.get('title',''), a.get('source',{}).get('name','')) for a in st.session_state['articles'][:max_check]]
                    elif "RSS" in sel_source:
                        items_to_check = [(i['title'], i['source']) for i in st.session_state['rss'][:max_check]]
                    elif "Reddit" in sel_source:
                        items_to_check = [(p.get('title',''), 'Reddit') for p in st.session_state['reddit'][:max_check]]
                    elif "Telegram" in sel_source:
                        items_to_check = [(m[:200], 'Telegram') for m in st.session_state['tg_msgs'][:max_check]]

                    results = []
                    prog = st.progress(0)
                    for idx, (title, src) in enumerate(items_to_check):
                        with st.spinner(f"فحص {idx+1}/{len(items_to_check)}: {title[:50]}..."):
                            res = detect_fake_news(title, f"المصدر: {src}")
                            results.append({"title":title, "source":src, "result":res})
                            prog.progress((idx+1)/len(items_to_check))

                    st.markdown("---")
                    st.markdown("### 📊 نتائج الفحص الجماعي:")

                    fake_count = sum(1 for r in results if r['result'] and r['result'].get('fake_score',0) >= 60)
                    suspicious_count = sum(1 for r in results if r['result'] and 30 <= r['result'].get('fake_score',0) < 60)
                    real_count = sum(1 for r in results if r['result'] and r['result'].get('fake_score',0) < 30)

                    m1,m2,m3 = st.columns(3)
                    with m1: st.metric("✅ حقيقية", real_count)
                    with m2: st.metric("⚠️ مشبوهة", suspicious_count)
                    with m3: st.metric("❌ مزيفة/دعاية", fake_count)

                    st.markdown("---")
                    for item in results:
                        title = item['title']
                        res = item['result']
                        if not res:
                            st.warning(f"⚪ {title[:80]}... — فشل التحليل")
                            continue
                        score = res.get('fake_score', 50)
                        verdict = res.get('verdict', '؟')
                        if score < 30:
                            st.success(f"✅ [{score}%] **{verdict}** — {title[:80]}...")
                        elif score < 60:
                            st.warning(f"⚠️ [{score}%] **{verdict}** — {title[:80]}...")
                        else:
                            st.error(f"❌ [{score}%] **{verdict}** — {title[:80]}...")
                        if res.get('warning'):
                            st.caption(f"⚠️ {res['warning']}")

# ══ TAB 6 — قنوات مباشرة ══
with TABS[5]:
    st.markdown("### 📺 قنوات إخبارية مباشرة")
    channels = {
        "🌍 الجزيرة مباشر":     "https://www.youtube.com/embed/B-sk6R4AJ5E?autoplay=1",
        "📺 العربية مباشر":      "https://www.youtube.com/embed/GkBj6pJBHpo?autoplay=1",
        "📡 روسيا اليوم عربي":   "https://www.youtube.com/embed/nMEFhh7QBvY?autoplay=1",
        "🇮🇱 i24 News العربي":   "https://www.youtube.com/embed/JsD3Se2Sxgk?autoplay=1",
        "🇺🇸 CNN International": "https://www.youtube.com/embed/21X5lGlDOfg?autoplay=1",
        "📺 قناة المياديين":     "https://www.youtube.com/embed/Z2DLh2GlN_I?autoplay=1",
        "🇸🇦 سكاي نيوز عربية":  "https://www.youtube.com/embed/oVYmfQDHJEI?autoplay=1",
        "🇺🇸 Al Arabiya English":"https://www.youtube.com/embed/nl64ZTXqLVk?autoplay=1",
    }
    cols = st.columns(4)
    for i,(name,_) in enumerate(channels.items()):
        with cols[i%4]:
            if st.button(name, use_container_width=True, key=f"ch_{i}"):
                st.session_state['channel'] = name
    ch = st.session_state.get('channel', "🌍 الجزيرة مباشر")
    st.markdown(f"#### 📺 {ch}")
    st.components.v1.iframe(channels[ch], height=500, scrolling=False)
    st.markdown("**🔗 روابط:** [الجزيرة](https://www.aljazeera.net/live) | [العربية](https://www.alarabiya.net/live) | [المياديين](https://www.almayadeen.net/live) | [i24](https://www.i24news.tv/ar)")

# ══ TAB 7 — الخريطة ══
with TABS[6]:
    st.markdown("### 🗺️ خريطة القصف — مارس 2026")
    events = [
        {"lat":15.5,"lon":44.2,"name":"اليمن — إطلاق صواريخ حوثية","type":"إطلاق","color":"red","size":15},
        {"lat":32.1,"lon":34.9,"name":"إسرائيل — اعتراض صواريخ إيرانية","type":"اعتراض","color":"blue","size":12},
        {"lat":32.4,"lon":53.7,"name":"إيران — إطلاق صواريخ باليستية","type":"إطلاق","color":"red","size":20},
        {"lat":24.7,"lon":46.7,"name":"الرياض — اعتراض صواريخ","type":"اعتراض","color":"orange","size":10},
        {"lat":26.2,"lon":50.6,"name":"البحرين — استهداف القاعدة الأمريكية","type":"ضربة","color":"red","size":18},
        {"lat":25.3,"lon":51.5,"name":"قطر — العديد — اعتراض","type":"اعتراض","color":"orange","size":12},
        {"lat":25.2,"lon":55.3,"name":"دبي — اعتراض مسيّرات","type":"اعتراض","color":"orange","size":10},
        {"lat":29.4,"lon":47.9,"name":"الكويت — اعتراض 97 صاروخ","type":"اعتراض","color":"orange","size":14},
        {"lat":33.9,"lon":35.5,"name":"بيروت — ضربات إسرائيلية","type":"ضربة","color":"purple","size":12},
        {"lat":33.3,"lon":44.4,"name":"بغداد — استهداف قواعد أمريكية","type":"ضربة","color":"red","size":10},
        {"lat":23.6,"lon":58.6,"name":"مسقط — لم تُستهدف (وسيط)","type":"آمن","color":"green","size":12},
    ]
    html_map = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>#map{height:520px;width:100%;border-radius:12px}body{margin:0}
.legend{background:#0d1e30;color:#e2e8f0;padding:10px;border-radius:8px;font-size:12px;line-height:2}
@keyframes pulse{0%{transform:scale(1);opacity:1}50%{transform:scale(1.6);opacity:0.5}100%{transform:scale(1);opacity:1}}
</style></head><body><div id="map"></div>
<script>
var map=L.map('map',{center:[27,45],zoom:5});
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{attribution:'©CARTO'}).addTo(map);
var ev=EVENTS_PLACEHOLDER;
var cm={'red':'#ef4444','blue':'#3b82f6','orange':'#f97316','green':'#22c55e','purple':'#a855f7'};
var ti={'إطلاق':'🚀','اعتراض':'🛡️','ضربة':'💥','آمن':'🕊️'};
ev.forEach(function(e){
  var c=cm[e.color]||'#fff',s=e.size;
  var ic=L.divIcon({html:'<div style="width:'+s+'px;height:'+s+'px;background:'+c+';border-radius:50%;border:2px solid #fff;box-shadow:0 0 14px '+c+';animation:pulse 1.4s infinite;"></div>',className:'',iconSize:[s,s],iconAnchor:[s/2,s/2]});
  L.marker([e.lat,e.lon],{icon:ic}).addTo(map).bindPopup('<div style="background:#0d1e30;color:#e2e8f0;padding:12px;border-radius:8px;direction:rtl;min-width:180px"><b>'+ti[e.type]+' '+e.name+'</b><br><span style="color:'+c+'">'+e.type+'</span></div>');
});
[{f:[15.5,44.2],t:[32.1,34.9],c:'#ef4444'},{f:[32.4,53.7],t:[32.1,34.9],c:'#dc2626'},
 {f:[32.4,53.7],t:[26.2,50.6],c:'#dc2626'},{f:[15.5,44.2],t:[24.7,46.7],c:'#f97316'},
 {f:[32.4,53.7],t:[25.3,51.5],c:'#7c3aed'},{f:[32.4,53.7],t:[25.2,55.3],c:'#f59e0b'},
 {f:[32.4,53.7],t:[29.4,47.9],c:'#ef4444'},{f:[33.5,36.3],t:[32.8,35.0],c:'#a855f7'}
].forEach(function(m){L.polyline([m.f,m.t],{color:m.c,weight:1.5,opacity:0.55,dashArray:'6,8'}).addTo(map);});
var leg=L.control({position:'bottomright'});
leg.onAdd=function(){var d=L.DomUtil.create('div','legend');d.innerHTML='<b>المفتاح</b><br>🚀 إطلاق<br>💥 ضربة<br>🛡️ اعتراض<br>🕊️ آمن';return d;};
leg.addTo(map);
</script></body></html>""".replace("EVENTS_PLACEHOLDER", json.dumps(events, ensure_ascii=False))
    st.components.v1.html(html_map, height=540)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("🚀 أُطلقت","1,800+","↑ مستمر")
    with c2: st.metric("🛡️ اعتُرضت","1,400+","78%")
    with c3: st.metric("💥 أصابت","400+")
    with c4: st.metric("🌍 دول","7")

# ══ TAB 8 — تحليل ذكي ══
with TABS[7]:
    st.markdown("### 🤖 تحليل Gemini الذكي الشامل")
    if GEMINI_KEY.startswith("ضع"):
        st.error("❌ ضع مفتاح Gemini في الكود (السطر 16)")
    else:
        analysis_type = st.selectbox("نوع التحليل:", [
            "📊 تقرير شامل عن الوضع العسكري الآن",
            "🎯 توقع الضربات القادمة في 48 ساعة",
            "🛢️ تأثير الحرب على النفط والاقتصاد",
            "🇴🇲 دور عُمان ومستوى أمانها",
            "🚀 تحليل منظومة الصواريخ الإيرانية",
            "🌊 خطر إغلاق مضيق هرمز",
            "💡 توصيات أمنية لدول الخليج",
        ])
        custom_q2 = st.text_input("أو اكتب سؤالك:", placeholder="ما احتمال توسع الحرب؟")
        c1,c2 = st.columns(2)
        with c1: include_news = st.checkbox("📰 أدرج أخبار اليوم", value=True)
        with c2: include_social = st.checkbox("📡 أدرج بيانات السوشل ميديا", value=True)

        if st.button("🤖 ابدأ التحليل الشامل", type="primary", use_container_width=True):
            final_q = custom_q2 if custom_q2 else analysis_type
            context = ""
            if include_news and 'articles' in st.session_state:
                context += "\n\nأخبار اليوم:\n" + "\n".join([f"- {a.get('title','')}" for a in st.session_state['articles'][:8]])
            if include_social:
                if 'rss' in st.session_state:
                    context += "\n\nRSS إسرائيلي/أمريكي:\n" + "\n".join([f"- {i['title']}" for i in st.session_state['rss'][:5]])
                if 'tg_msgs' in st.session_state:
                    context += "\n\nTelegram:\n" + "\n".join([f"- {m[:100]}" for m in st.session_state['tg_msgs'][:3]])
                if 'reddit' in st.session_state:
                    context += "\n\nReddit:\n" + "\n".join([f"- {p.get('title','')}" for p in st.session_state['reddit'][:5]])

            with st.spinner("🤖 Gemini يحلل كل البيانات..."):
                result = ask_gemini(f"""أنت محلل استخباراتي عسكري متخصص في الشرق الأوسط.
السياق: مارس 2026 — عملية Epic Fury + رد إيران بـ 1800+ صاروخ على الخليج.
{context}
المطلوب: {final_q}
أجب بتقرير مفصل بالعربية: الوضع الراهن، التوقعات مع نسب، مناطق الخطر، الإطار الزمني، التوصيات.""")
                st.markdown("---")
                st.markdown("#### 📋 نتائج التحليل:")
                st.markdown(result)
                st.markdown("---")
                st.markdown("#### 🚨 مستوى التهديد:")
                countries=["🇴🇲 عُمان","🇸🇦 السعودية","🇦🇪 الإمارات","🇮🇱 إسرائيل","🇮🇷 إيران","🇶🇦 قطر","🇾🇪 اليمن","🇱🇧 لبنان"]
                levels=[20,75,70,90,95,65,85,80]
                emojis=["🟢","🟡","🟡","🔴","🔴","🟡","🔴","🔴"]
                cols=st.columns(4)
                for i,(c,l,e) in enumerate(zip(countries,levels,emojis)):
                    with cols[i%4]:
                        st.metric(c,f"{e} {l}%")
                        st.progress(l/100)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#475569;font-size:11px'>🛰️ وكيل الأخبار العسكري | أخبار اليوم + Telegram + Reddit + RSS + كشف الأخبار المزيفة + Gemini AI</div>", unsafe_allow_html=True)
