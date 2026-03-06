import streamlit as st
import requests
import json
import feedparser
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
GEMINI_KEY = "ضع-مفتاح-Gemini-هنا"   # ← غيّر هذا

st.markdown("""
<div style='text-align:center;padding:15px;background:linear-gradient(135deg,#04090f,#0d1e30);border-radius:12px;margin-bottom:10px;border:1px solid #1e3a5f'>
  <h1 style='color:#38bdf8;margin:0'>🛰️ وكيل الأخبار العسكري</h1>
  <p style='color:#64748b;margin:4px 0'>الخليج · إيران · إسرائيل · أمريكا | سوشل ميديا | تحليل ذكي</p>
  <p style='color:#ef4444;font-size:12px;margin:0'>● بث مباشر | مارس 2026</p>
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
    url = f"https://newsapi.org/v2/everything?q={q}&apiKey={NEWS_KEY}&language=en&sortBy=publishedAt&pageSize=30"
    try: return requests.get(url,timeout=10).json().get("articles",[])
    except: return []

RSS_SOURCES = {
    "🇮🇱 Times of Israel":    "https://www.timesofisrael.com/feed/",
    "🇮🇱 Jerusalem Post":     "https://www.jpost.com/rss/rssfeedsheadlines.aspx",
    "🇺🇸 Reuters":            "https://feeds.reuters.com/reuters/topNews",
    "🇺🇸 Defense News":       "https://www.defensenews.com/rss/",
    "🌍 Al Jazeera English":  "https://www.aljazeera.com/xml/rss/all.xml",
    "🇺🇸 Breaking Defense":   "https://breakingdefense.com/feed/",
    "🌍 Middle East Eye":     "https://www.middleeasteye.net/rss",
}

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries[:8]
    except: return []

def fetch_reddit(sub, q=""):
    try:
        url = f"https://www.reddit.com/r/{sub}/search.json?q={q or 'war missile strike'}&sort=new&limit=10&restrict_sr=1"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        return [p["data"] for p in r.json()["data"]["children"]]
    except: return []

TABS = st.tabs(["📰 الأخبار","📡 سوشل ميديا","📺 قنوات مباشرة","🗺️ خريطة القصف","🤖 تحليل ذكي"])

# TAB 1
with TABS[0]:
    if st.button("🔄 تحديث الأخبار", use_container_width=True, type="primary"):
        with st.spinner("جارٍ تحميل الأخبار..."):
            st.session_state['articles'] = fetch_news(build_query())

    if 'articles' not in st.session_state:
        st.info("👆 اضغط تحديث الأخبار")
    else:
        arts = st.session_state['articles']
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("📰 الأخبار", len(arts))
        with c2: st.metric("🌐 مصادر", len(set(a['source']['name'] for a in arts if a.get('source'))))
        with c3: st.metric("🔴 عاجل", sum(1 for a in arts if any(w in (a.get('title','') or '').lower() for w in ['breaking','attack','strike','missile','war'])))
        with c4: st.metric("🕐 تحديث", datetime.now().strftime("%H:%M"))
        st.markdown("---")
        for i, art in enumerate(arts[:20]):
            if not art.get('title') or art['title']=='[Removed]': continue
            title = art['title']
            desc  = art.get('description','') or ''
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
                    if is_brk: st.error(f"🔴 عاجل | {art['source']['name']} | {(art.get('publishedAt','') or '')[:10]}")
                    else:       st.info(f"📰 {art['source']['name']} | {(art.get('publishedAt','') or '')[:10]}")
                    st.markdown(f"**{title}**")
                    if desc: st.caption(desc)
                    st.markdown(f"[🔗 اقرأ كاملاً]({art.get('url','#')})")
            st.divider()

# TAB 2
with TABS[1]:
    st.markdown("### 📡 مراقبة السوشل ميديا والمواقع الإخبارية")
    sub_tab1, sub_tab2 = st.tabs(["📰 مواقع إسرائيلية وأمريكية (RSS)", "🟠 Reddit"])

    with sub_tab1:
        selected_sources = st.multiselect("اختر المصادر:", list(RSS_SOURCES.keys()), default=list(RSS_SOURCES.keys())[:3])
        if st.button("📡 تحديث RSS", use_container_width=True):
            all_rss = []
            for src in selected_sources:
                with st.spinner(f"تحميل {src}..."):
                    for e in fetch_rss(RSS_SOURCES[src]):
                        all_rss.append({"source":src,"title":getattr(e,'title',''),"link":getattr(e,'link','#'),
                            "summary":(getattr(e,'summary','')[:200] if hasattr(e,'summary') else '')})
            st.session_state['rss'] = all_rss

        if 'rss' not in st.session_state:
            st.info("👆 اضغط تحديث RSS")
        else:
            rss_items = st.session_state['rss']
            st.success(f"✅ {len(rss_items)} منشور")
            analyze_rss = st.button("🤖 تحليل Gemini لكل المنشورات", type="primary")
            for item in rss_items:
                title = item['title']
                if auto_translate and not GEMINI_KEY.startswith("ضع") and title:
                    title = translate_ar(title)
                is_war = any(w in (item['title'] or '').lower() for w in ['attack','strike','missile','war','bomb','iran','israel','houthi'])
                with st.container():
                    col_a,col_b = st.columns([3,1])
                    with col_a:
                        if is_war: st.error(f"⚔️ {item['source']}")
                        else:      st.info(f"📰 {item['source']}")
                        st.markdown(f"**{title}**")
                        if item['summary']: st.caption(item['summary'][:150]+"...")
                        st.markdown(f"[🔗 المصدر]({item['link']})")
                    with col_b:
                        if analyze_rss and not GEMINI_KEY.startswith("ضع") and item['title']:
                            with st.spinner("تحليل..."):
                                an = ask_gemini(f"حلل هذا الخبر بجملتين عربيتين فقط:\n{item['title']}")
                                st.caption(f"🤖 {an[:150]}")
                st.divider()

    with sub_tab2:
        subreddits = {"r/worldnews":"worldnews","r/MiddleEast":"MiddleEast","r/CombatFootage":"CombatFootage","r/geopolitics":"geopolitics","r/Israel":"Israel"}
        sel_sub = st.selectbox("اختر المنتدى:", list(subreddits.keys()))
        reddit_q = st.text_input("كلمة بحث:", value="Iran Israel missile strike")
        if st.button("🟠 تحميل Reddit", use_container_width=True):
            with st.spinner("تحميل Reddit..."):
                st.session_state['reddit'] = fetch_reddit(subreddits[sel_sub], reddit_q)

        if 'reddit' not in st.session_state:
            st.info("👆 اضغط تحميل Reddit")
        else:
            posts = st.session_state['reddit']
            st.success(f"✅ {len(posts)} منشور")
            analyze_reddit = st.button("🤖 تحليل Gemini", type="primary", key="an_reddit")
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
                        if analyze_reddit and not GEMINI_KEY.startswith("ضع"):
                            with st.spinner("تحليل..."):
                                an = ask_gemini(f"حلل هذا المنشور بجملتين عربيتين:\n{title}")
                                st.caption(f"🤖 {an[:150]}")
                st.divider()

# TAB 3
with TABS[2]:
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
    st.markdown("---")
    st.markdown("**🔗 روابط مباشرة:** [الجزيرة](https://www.aljazeera.net/live) | [العربية](https://www.alarabiya.net/live) | [المياديين](https://www.almayadeen.net/live) | [i24](https://www.i24news.tv/ar)")

# TAB 4
with TABS[3]:
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
        {"lat":24.5,"lon":54.4,"name":"أبوظبي — اعتراض مسيّرات","type":"اعتراض","color":"orange","size":9},
        {"lat":21.5,"lon":39.2,"name":"جدة — اعتراض صاروخ","type":"اعتراض","color":"orange","size":9},
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
var ev=""" + json.dumps(events,ensure_ascii=False) + """;
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
</script></body></html>"""
    st.components.v1.html(html_map, height=540)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("🚀 أُطلقت","1,800+","↑ مستمر")
    with c2: st.metric("🛡️ اعتُرضت","1,400+","78%")
    with c3: st.metric("💥 أصابت","400+")
    with c4: st.metric("🌍 دول","7")

# TAB 5
with TABS[4]:
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
        col1,col2 = st.columns(2)
        with col1: include_news = st.checkbox("📰 أدرج آخر الأخبار", value=True)
        with col2: include_social = st.checkbox("📡 أدرج بيانات RSS", value=True)

        if st.button("🤖 ابدأ التحليل الشامل", type="primary", use_container_width=True):
            final_q = custom_q2 if custom_q2 else analysis_type
            context = ""
            if include_news and 'articles' in st.session_state:
                context += "\n\nآخر الأخبار:\n" + "\n".join([f"- {a.get('title','')}" for a in st.session_state['articles'][:10]])
            if include_social and 'rss' in st.session_state:
                context += "\n\nمنشورات الإعلام:\n" + "\n".join([f"- {i['title']}" for i in st.session_state['rss'][:5]])

            with st.spinner("🤖 Gemini يحلل..."):
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
st.markdown("<div style='text-align:center;color:#475569;font-size:11px'>🛰️ وكيل الأخبار العسكري | NewsAPI + RSS + Reddit + Gemini AI</div>", unsafe_allow_html=True)
