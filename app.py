import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="🛰️ وكيل الأخبار العسكري",
    page_icon="🛰️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; }
.stApp { background: #04090f; }
h1,h2,h3 { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

NEWS_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"

st.markdown("""
<div style='text-align:center; padding: 20px 0;'>
    <h1 style='font-size:2.5em; color:#38bdf8;'>🛰️ وكيل الأخبار العسكري</h1>
    <p style='color:#64748b; font-size:1.1em;'>تغطية شاملة — الخليج · إيران · إسرائيل · أمريكا</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    GEMINI_KEY = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIza...")
    st.markdown("[احصل على مفتاح مجاني 👉](https://aistudio.google.com)")
    st.markdown("---")
    st.markdown("### 🌍 اختر المنطقة")
    regions = st.multiselect("المناطق:",
        ["عُمان", "الخليج العربي", "إيران", "إسرائيل", "أمريكا", "اليمن", "العراق", "لبنان"],
        default=["عُمان", "الخليج العربي", "إيران", "إسرائيل"]
    )
    st.markdown("---")
    news_type = st.selectbox("نوع الأخبار:", ["الكل", "عسكري", "سياسي", "صواريخ وضربات", "دبلوماسي"])
    st.markdown("---")
    custom_query = st.text_input("🔍 بحث مخصص:", placeholder="مثال: صواريخ حوثية")

def ask_gemini(prompt, key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        res = requests.post(url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"خطأ في الاتصال بـ Gemini: {e}"

def translate_gemini(text, key):
    if not key or not text:
        return text
    return ask_gemini(f"ترجم هذا النص للعربية، أعد النص المترجم فقط:\n\n{text}", key)

def build_query():
    region_map = {
        "عُمان": "Oman", "الخليج العربي": "Gulf Saudi UAE Kuwait Qatar Bahrain",
        "إيران": "Iran", "إسرائيل": "Israel", "أمريكا": "US military Middle East",
        "اليمن": "Yemen Houthi", "العراق": "Iraq", "لبنان": "Lebanon Hezbollah"
    }
    type_map = {
        "عسكري": "military strike", "سياسي": "politics diplomacy",
        "صواريخ وضربات": "missile strike bombing", "دبلوماسي": "diplomacy",
        "الكل": "war conflict"
    }
    if custom_query:
        return custom_query
    region_q = " OR ".join([region_map.get(r, r) for r in regions]) if regions else "Middle East"
    type_q = type_map.get(news_type, "war")
    return f"({region_q}) AND ({type_q})"

def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_KEY}&language=en&sortBy=publishedAt&pageSize=30"
    try:
        return requests.get(url, timeout=10).json().get("articles", [])
    except:
        return []

tab1, tab2, tab3 = st.tabs(["📰 الأخبار", "🗺️ خريطة القصف", "🤖 توقعات الذكاء الاصطناعي"])

# ══ TAB 1 — الأخبار ══
with tab1:
    if st.button("🔄 تحديث الأخبار", use_container_width=True, type="primary"):
        with st.spinner("جارٍ تحميل أحدث الأخبار..."):
            q = build_query()
            arts = fetch_news(q)
            st.session_state['articles'] = arts
            st.session_state['query'] = q

    if 'articles' not in st.session_state:
        st.info("👆 اضغط 'تحديث الأخبار' لتحميل أحدث الأخبار")
    else:
        articles = st.session_state['articles']
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("📰 الأخبار", len(articles))
        with c2: st.metric("🌐 المصادر", len(set(a['source']['name'] for a in articles if a.get('source'))))
        with c3: st.metric("🔴 عاجل", sum(1 for a in articles if any(w in (a.get('title','') or '').lower() for w in ['breaking','attack','strike','missile','war'])))
        with c4: st.metric("🕐 التحديث", datetime.now().strftime("%H:%M"))

        st.markdown("---")
        translate = st.toggle("🌐 ترجمة تلقائية للعربية بـ Gemini", value=False)
        if translate and not GEMINI_KEY:
            st.warning("⚠️ أدخل Gemini API Key في الشريط الجانبي للترجمة")

        for i, art in enumerate(articles[:25]):
            if not art.get('title') or art['title'] == '[Removed]':
                continue
            title = art['title']
            desc = art.get('description', '') or ''
            source = art['source']['name']
            url_link = art.get('url', '#')
            img = art.get('urlToImage', '')
            published = (art.get('publishedAt', '') or '')[:10]

            if translate and GEMINI_KEY:
                with st.spinner(f"ترجمة {i+1}..."):
                    title = translate_gemini(title, GEMINI_KEY)
                    if desc: desc = translate_gemini(desc, GEMINI_KEY)

            is_breaking = any(w in (art.get('title','') or '').lower() for w in ['breaking','urgent','attack','strike','missile','war','explosion'])

            with st.container():
                c1, c2 = st.columns([1, 3])
                with c1:
                    if img:
                        try: st.image(img, use_container_width=True)
                        except: pass
                with c2:
                    if is_breaking:
                        st.error(f"🔴 عاجل | {source} | {published}")
                    else:
                        st.info(f"📰 {source} | {published}")
                    st.markdown(f"**{title}**")
                    if desc: st.caption(desc)
                    st.markdown(f"[🔗 اقرأ الخبر كاملاً]({url_link})")
                st.divider()

# ══ TAB 2 — الخريطة ══
with tab2:
    st.markdown("### 🗺️ خريطة القصف الجوي والصواريخ — مارس 2026")

    events = [
        {"lat":15.5,"lon":44.2,"name":"اليمن — إطلاق صواريخ حوثية","type":"إطلاق","color":"red","size":15},
        {"lat":32.1,"lon":34.9,"name":"إسرائيل — اعتراض صواريخ إيرانية","type":"اعتراض","color":"blue","size":12},
        {"lat":32.4,"lon":53.7,"name":"إيران — إطلاق صواريخ باليستية","type":"إطلاق","color":"red","size":20},
        {"lat":24.7,"lon":46.7,"name":"الرياض — اعتراض صواريخ","type":"اعتراض","color":"orange","size":10},
        {"lat":26.2,"lon":50.6,"name":"البحرين — استهداف القاعدة الأمريكية","type":"ضربة","color":"red","size":18},
        {"lat":25.3,"lon":51.5,"name":"قطر — العديد — اعتراض صواريخ","type":"اعتراض","color":"orange","size":12},
        {"lat":25.2,"lon":55.3,"name":"دبي — اعتراض مسيّرات","type":"اعتراض","color":"orange","size":10},
        {"lat":29.4,"lon":47.9,"name":"الكويت — اعتراض 97 صاروخ","type":"اعتراض","color":"orange","size":14},
        {"lat":33.9,"lon":35.5,"name":"بيروت — ضربات إسرائيلية","type":"ضربة","color":"purple","size":12},
        {"lat":33.3,"lon":44.4,"name":"بغداد — استهداف قواعد أمريكية","type":"ضربة","color":"red","size":10},
        {"lat":23.6,"lon":58.6,"name":"مسقط — لم تُستهدف (وسيط)","type":"آمن","color":"green","size":12},
    ]

    html_map = """<!DOCTYPE html><html><head><meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
    #map{height:500px;width:100%;border-radius:12px}
    body{margin:0}
    .legend{background:#0d1e30;color:#e2e8f0;padding:10px;border-radius:8px;font-size:12px;line-height:1.8}
    @keyframes pulse{0%{transform:scale(1);opacity:1}50%{transform:scale(1.5);opacity:0.6}100%{transform:scale(1);opacity:1}}
    </style></head><body>
    <div id="map"></div>
    <script>
    var map=L.map('map',{center:[27,45],zoom:5});
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{attribution:'© CARTO'}).addTo(map);
    var events=""" + json.dumps(events, ensure_ascii=False) + """;
    var cm={'red':'#ef4444','blue':'#3b82f6','orange':'#f97316','green':'#22c55e','purple':'#a855f7'};
    var ti={'إطلاق':'🚀','اعتراض':'🛡️','ضربة':'💥','آمن':'🕊️'};
    events.forEach(function(ev){
        var c=cm[ev.color]||'#fff',s=ev.size;
        var icon=L.divIcon({html:'<div style="width:'+s+'px;height:'+s+'px;background:'+c+';border-radius:50%;border:2px solid white;box-shadow:0 0 12px '+c+';animation:pulse 1.5s infinite;"></div>',className:'',iconSize:[s,s],iconAnchor:[s/2,s/2]});
        L.marker([ev.lat,ev.lon],{icon:icon}).addTo(map).bindPopup('<div style="background:#0d1e30;color:#e2e8f0;padding:10px;border-radius:8px;direction:rtl;text-align:right"><b>'+ti[ev.type]+' '+ev.name+'</b><br><span style="color:'+c+'">'+ev.type+'</span></div>');
    });
    [{from:[15.5,44.2],to:[32.1,34.9],c:'#ef4444'},{from:[32.4,53.7],to:[32.1,34.9],c:'#dc2626'},
     {from:[32.4,53.7],to:[26.2,50.6],c:'#dc2626'},{from:[15.5,44.2],to:[24.7,46.7],c:'#f97316'},
     {from:[32.4,53.7],to:[25.3,51.5],c:'#7c3aed'},{from:[32.4,53.7],to:[25.2,55.3],c:'#f59e0b'},
     {from:[32.4,53.7],to:[29.4,47.9],c:'#ef4444'},{from:[33.5,36.3],to:[32.8,35.0],c:'#a855f7'}
    ].forEach(function(m){L.polyline([m.from,m.to],{color:m.c,weight:1.5,opacity:0.6,dashArray:'6,8'}).addTo(map);});
    var leg=L.control({position:'bottomright'});
    leg.onAdd=function(){var d=L.DomUtil.create('div','legend');d.innerHTML='<b>🗺️ المفتاح</b><br>🚀 إطلاق<br>💥 ضربة<br>🛡️ اعتراض<br>🕊️ آمن';return d;};
    leg.addTo(map);
    </script></body></html>"""

    st.components.v1.html(html_map, height=520)

    st.markdown("### 📊 إحصائيات — مارس 2026")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("🚀 صواريخ أُطلقت","1,800+",delta="↑ مستمر")
    with c2: st.metric("🛡️ اعتُرضت","1,400+",delta="78%")
    with c3: st.metric("💥 أصابت الهدف","400+")
    with c4: st.metric("🌍 دول مستهدفة","7")

# ══ TAB 3 — Gemini AI ══
with tab3:
    st.markdown("### 🤖 توقعات Gemini AI للضربات القادمة")

    if not GEMINI_KEY:
        st.warning("⚠️ أدخل Gemini API Key في الشريط الجانبي")
        st.markdown("AIzaSyDuOADJ6YDyqBjOYFC2x-0ql1hgb0kIWaQ )")
    else:
        scenario = st.selectbox("اختر موضوع التحليل:", [
            "توقع الضربات العسكرية القادمة في الشرق الأوسط",
            "تحليل أنماط الصواريخ الإيرانية",
            "توقع ردود فعل دول الخليج",
            "تحليل الوضع في اليمن والحوثيين",
            "توقع مسار الحرب الإيرانية الإسرائيلية",
            "تأثير الحرب على أمن عُمان",
            "توقع موقف أمريكا في الأيام القادمة",
        ])
        custom_s = st.text_input("أو اكتب سؤالك الخاص:", placeholder="مثال: هل ستُغلق مضيق هرمز؟")

        if st.button("🤖 تحليل وتوقع", type="primary", use_container_width=True):
            final_q = custom_s if custom_s else scenario
            with st.spinner("🤖 Gemini AI يحلل البيانات..."):
                prompt = f"""أنت محلل استخباراتي عسكري خبير في الشرق الأوسط.
بناءً على أحداث مارس 2026:
- الضربات الأمريكية الإسرائيلية على إيران (عملية Epic Fury)
- الرد الإيراني بـ 1800+ صاروخ على دول الخليج
- اعتراض قطر لطائرتين إيرانيتين
- استهداف أرامكو السعودية وسفارات أمريكية

السؤال: {final_q}

قدم تحليلاً مفصلاً بالعربية يشمل:
1. 🎯 التوقعات المحددة (3-5 توقعات مع نسبة احتمالية %)
2. ⚠️ مناطق الخطر الأعلى
3. 🕐 الإطار الزمني المتوقع
4. 💡 التوصيات الأمنية
5. 🌍 الدول الأكثر تأثراً"""

                analysis = ask_gemini(prompt, GEMINI_KEY)
                st.markdown("---")
                st.markdown("#### 📋 نتائج التحليل:")
                st.markdown(analysis)
                st.markdown("---")
                st.markdown("#### 🚨 مستوى التهديد الحالي:")
                countries = ["🇴🇲 عُمان","🇸🇦 السعودية","🇦🇪 الإمارات","🇮🇱 إسرائيل","🇮🇷 إيران","🇶🇦 قطر"]
                levels = [20,75,70,90,95,65]
                emojis = ["🟢","🟡","🟡","🔴","🔴","🟡"]
                cols = st.columns(6)
                for col,country,level,em in zip(cols,countries,levels,emojis):
                    with col:
                        st.metric(country, f"{em} {level}%")
                        st.progress(level/100)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#475569;font-size:12px'>🛰️ وكيل الأخبار العسكري | NewsAPI + Google Gemini AI</div>", unsafe_allow_html=True)
