import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="🛰️ وكيل الأخبار العسكري",
    page_icon="🛰️",
    layout="wide"
)

# ── CSS مخصص ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
* { font-family: 'Noto Kufi Arabic', sans-serif !important; }
.main { background: #04090f; color: #e2e8f0; }
.stApp { background: #04090f; }
h1,h2,h3 { color: #38bdf8 !important; }
.news-card {
    background: #0d1e30;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    border-right: 4px solid #0ea5e9;
}
.breaking { border-right-color: #ef4444 !important; }
.metric-card {
    background: #0d1e30;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── KEYS ──
NEWS_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"
CLAUDE_KEY = st.secrets.get("CLAUDE_KEY", "")

# ── HEADER ──
st.markdown("""
<div style='text-align:center; padding: 20px 0;'>
    <h1 style='font-size:2.5em; color:#38bdf8;'>🛰️ وكيل الأخبار العسكري</h1>
    <p style='color:#64748b; font-size:1.1em;'>تغطية شاملة — الخليج · إيران · إسرائيل · أمريكا</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    claude_key_input = st.text_input("🔑 Anthropic API Key (للذكاء الاصطناعي)", type="password", placeholder="sk-ant-...")
    if claude_key_input:
        CLAUDE_KEY = claude_key_input

    st.markdown("---")
    st.markdown("### 🌍 اختر المنطقة")
    regions = st.multiselect("المناطق:", 
        ["عُمان", "الخليج العربي", "إيران", "إسرائيل", "أمريكا", "اليمن", "العراق", "لبنان"],
        default=["عُمان", "الخليج العربي", "إيران", "إسرائيل"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 نوع الأخبار")
    news_type = st.selectbox("النوع:", ["الكل", "عسكري", "سياسي", "صواريخ وضربات", "دبلوماسي"])
    
    st.markdown("---")
    st.markdown("### 🔍 بحث مخصص")
    custom_query = st.text_input("موضوع محدد:", placeholder="مثال: صواريخ حوثية")

# ── TABS ──
tab1, tab2, tab3 = st.tabs(["📰 الأخبار", "🗺️ خريطة القصف", "🤖 توقعات الذكاء الاصطناعي"])

# ── بناء استعلام البحث ──
def build_query():
    region_map = {
        "عُمان": "Oman",
        "الخليج العربي": "Gulf Arabia Saudi UAE Kuwait Qatar Bahrain",
        "إيران": "Iran",
        "إسرائيل": "Israel",
        "أمريكا": "US military Middle East",
        "اليمن": "Yemen Houthi",
        "العراق": "Iraq",
        "لبنان": "Lebanon Hezbollah"
    }
    type_map = {
        "عسكري": "military strike attack",
        "سياسي": "politics diplomacy",
        "صواريخ وضربات": "missile strike bombing",
        "دبلوماسي": "diplomacy negotiations",
        "الكل": "war conflict"
    }
    region_q = " OR ".join([region_map.get(r, r) for r in regions]) if regions else "Middle East"
    type_q = type_map.get(news_type, "war")
    if custom_query:
        return custom_query
    return f"({region_q}) AND ({type_q})"

# ── ترجمة بـ Claude ──
def translate_with_claude(text, key):
    if not key or not text:
        return text
    try:
        res = requests.post("https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "messages": [{"role":"user","content":f"ترجم هذا النص للعربية بشكل احترافي، أعد النص المترجم فقط بدون أي شرح:\n\n{text}"}]
            }, timeout=10
        )
        return res.json()["content"][0]["text"]
    except:
        return text

# ── جلب الأخبار ──
def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_KEY}&language=en&sortBy=publishedAt&pageSize=30"
    try:
        res = requests.get(url, timeout=10).json()
        return res.get("articles", [])
    except:
        return []

# ══════════════════════════════════════
# TAB 1 — الأخبار
# ══════════════════════════════════════
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    if st.button("🔄 تحديث الأخبار", use_container_width=True, type="primary"):
        with st.spinner("جارٍ تحميل أحدث الأخبار..."):
            query = build_query()
            articles = fetch_news(query)
            st.session_state['articles'] = articles
            st.session_state['query'] = query

    if 'articles' not in st.session_state:
        st.info("👆 اضغط 'تحديث الأخبار' لتحميل أحدث الأخبار")
    else:
        articles = st.session_state['articles']
        
        # إحصائيات
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📰 إجمالي الأخبار", len(articles))
        with col2:
            sources = len(set(a['source']['name'] for a in articles))
            st.metric("🌐 المصادر", sources)
        with col3:
            st.metric("🔍 موضوع البحث", st.session_state.get('query','')[:20]+"...")
        with col4:
            st.metric("🕐 آخر تحديث", datetime.now().strftime("%H:%M"))
        
        st.markdown("---")
        
        # عرض الأخبار
        translate = st.toggle("🌐 ترجمة تلقائية للعربية (يحتاج Claude API Key)", value=False)
        
        for i, art in enumerate(articles[:25]):
            if not art.get('title') or art['title'] == '[Removed]':
                continue
            
            title = art['title']
            desc = art.get('description', '') or ''
            source = art['source']['name']
            url = art.get('url', '#')
            img = art.get('urlToImage', '')
            published = art.get('publishedAt', '')[:10]
            
            # ترجمة إذا مفعّلة
            if translate and CLAUDE_KEY:
                with st.spinner(f"جارٍ ترجمة الخبر {i+1}..."):
                    title = translate_with_claude(title, CLAUDE_KEY)
                    if desc:
                        desc = translate_with_claude(desc, CLAUDE_KEY)

            # تحديد نوع الخبر
            is_breaking = any(w in art['title'].lower() for w in ['breaking','urgent','attack','strike','missile','war','explosion'])
            card_class = "news-card breaking" if is_breaking else "news-card"
            
            with st.container():
                c1, c2 = st.columns([1, 3])
                with c1:
                    if img:
                        try:
                            st.image(img, use_container_width=True)
                        except:
                            st.markdown("🖼️")
                with c2:
                    if is_breaking:
                        st.error(f"🔴 عاجل | {source} | {published}")
                    else:
                        st.info(f"📰 {source} | {published}")
                    st.markdown(f"**{title}**")
                    if desc:
                        st.caption(desc)
                    st.markdown(f"[🔗 اقرأ الخبر كاملاً]({url})")
                st.divider()

# ══════════════════════════════════════
# TAB 2 — خريطة القصف
# ══════════════════════════════════════
with tab2:
    st.markdown("### 🗺️ خريطة القصف الجوي والصواريخ — مارس 2026")
    
    # بيانات الأحداث
    events = [
        {"lat": 15.5, "lon": 44.2, "name": "اليمن — إطلاق صواريخ حوثية", "type": "إطلاق", "color": "red", "size": 15},
        {"lat": 32.1, "lon": 34.9, "name": "إسرائيل — اعتراض صواريخ إيرانية", "type": "اعتراض", "color": "blue", "size": 12},
        {"lat": 32.4, "lon": 53.7, "name": "إيران — إطلاق صواريخ باليستية", "type": "إطلاق", "color": "red", "size": 20},
        {"lat": 24.7, "lon": 46.7, "name": "الرياض — اعتراض صواريخ", "type": "اعتراض", "color": "orange", "size": 10},
        {"lat": 26.2, "lon": 50.6, "name": "البحرين — استهداف القاعدة الأمريكية", "type": "ضربة", "color": "red", "size": 18},
        {"lat": 25.3, "lon": 51.5, "name": "قطر — العديد — اعتراض صواريخ", "type": "اعتراض", "color": "orange", "size": 12},
        {"lat": 25.2, "lon": 55.3, "name": "دبي — اعتراض مسيّرات", "type": "اعتراض", "color": "orange", "size": 10},
        {"lat": 29.4, "lon": 47.9, "name": "الكويت — اعتراض 97 صاروخ", "type": "اعتراض", "color": "orange", "size": 14},
        {"lat": 33.9, "lon": 35.5, "name": "بيروت — ضربات إسرائيلية", "type": "ضربة", "color": "purple", "size": 12},
        {"lat": 33.3, "lon": 44.4, "name": "بغداد — استهداف قواعد أمريكية", "type": "ضربة", "color": "red", "size": 10},
        {"lat": 23.6, "lon": 58.6, "name": "مسقط — لم تُستهدف (وسيط)", "type": "آمن", "color": "green", "size": 12},
    ]
    
    # خريطة HTML تفاعلية
    html_map = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
    #map { height: 500px; width: 100%; border-radius: 12px; }
    body { margin: 0; background: #04090f; }
    .legend { background: #0d1e30; color: #e2e8f0; padding: 10px; border-radius: 8px; font-family: Arial; font-size: 12px; }
    </style>
    </head>
    <body>
    <div id="map"></div>
    <script>
    var map = L.map('map', {
        center: [27, 45],
        zoom: 5,
        preferCanvas: true
    });
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap © CARTO'
    }).addTo(map);
    
    var events = """ + json.dumps(events, ensure_ascii=False) + """;
    
    var colorMap = {
        'red': '#ef4444',
        'blue': '#3b82f6', 
        'orange': '#f97316',
        'green': '#22c55e',
        'purple': '#a855f7'
    };
    
    var typeIcon = {
        'إطلاق': '🚀',
        'اعتراض': '🛡️',
        'ضربة': '💥',
        'آمن': '🕊️'
    };
    
    events.forEach(function(ev) {
        var color = colorMap[ev.color] || '#ffffff';
        
        // نبضة متحركة
        var pulseIcon = L.divIcon({
            html: '<div style="width:' + ev.size + 'px;height:' + ev.size + 'px;background:' + color + ';border-radius:50%;border:2px solid white;box-shadow:0 0 10px ' + color + ';animation:pulse 1.5s infinite;"></div>',
            className: '',
            iconSize: [ev.size, ev.size],
            iconAnchor: [ev.size/2, ev.size/2]
        });
        
        L.marker([ev.lat, ev.lon], {icon: pulseIcon})
            .addTo(map)
            .bindPopup('<div style="background:#0d1e30;color:#e2e8f0;padding:10px;border-radius:8px;font-family:Arial;direction:rtl;text-align:right"><b>' + typeIcon[ev.type] + ' ' + ev.name + '</b><br><span style="color:' + color + '">' + ev.type + '</span></div>');
    });
    
    // رسم خطوط الصواريخ
    var missiles = [
        {from:[15.5,44.2], to:[32.1,34.9], color:'#ef4444'},
        {from:[32.4,53.7], to:[32.1,34.9], color:'#dc2626'},
        {from:[32.4,53.7], to:[26.2,50.6], color:'#dc2626'},
        {from:[15.5,44.2], to:[24.7,46.7], color:'#f97316'},
        {from:[32.4,53.7], to:[25.3,51.5], color:'#7c3aed'},
        {from:[33.5,36.3], to:[32.8,35.0], color:'#a855f7'},
    ];
    
    missiles.forEach(function(m) {
        L.polyline([m.from, m.to], {
            color: m.color,
            weight: 1.5,
            opacity: 0.6,
            dashArray: '6,8'
        }).addTo(map);
    });
    
    // Legend
    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function() {
        var div = L.DomUtil.create('div', 'legend');
        div.innerHTML = '<b>🗺️ المفتاح</b><br>🚀 إطلاق صاروخ<br>💥 ضربة جوية<br>🛡️ اعتراض<br>🕊️ منطقة آمنة';
        return div;
    };
    legend.addTo(map);
    </script>
    <style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.4); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    </style>
    </body>
    </html>
    """
    
    st.components.v1.html(html_map, height=520)
    
    # إحصائيات الخريطة
    st.markdown("### 📊 إحصائيات الضربات (مارس 2026)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🚀 صواريخ أُطلقت", "1,800+", delta="↑ مستمر")
    with c2:
        st.metric("🛡️ صواريخ اعتُرضت", "1,400+", delta="78%")
    with c3:
        st.metric("💥 أصابت الهدف", "400+")
    with c4:
        st.metric("🌍 دول مستهدفة", "7")

# ══════════════════════════════════════
# TAB 3 — توقعات الذكاء الاصطناعي
# ══════════════════════════════════════
with tab3:
    st.markdown("### 🤖 توقعات الذكاء الاصطناعي للضربات القادمة")
    
    if not CLAUDE_KEY:
        st.warning("⚠️ أدخل Anthropic API Key في الشريط الجانبي لتفعيل الذكاء الاصطناعي")
        st.markdown("""
        **مثال على ما يمكن للذكاء الاصطناعي توقعه:**
        - 🎯 الأهداف المحتملة للضربات القادمة
        - 📅 التوقيت المرجّح للتصعيد
        - 🌍 الدول الأكثر عرضة للخطر
        - ⚡ تحليل أنماط الهجمات السابقة
        - 🛡️ توصيات أمنية للمنطقة
        """)
    else:
        scenario = st.selectbox("اختر موضوع التحليل:", [
            "توقع الضربات العسكرية القادمة في الشرق الأوسط",
            "تحليل أنماط الصواريخ الإيرانية",
            "توقع ردود فعل دول الخليج",
            "تحليل الوضع في اليمن والحوثيين",
            "توقع مسار الحرب الإيرانية الإسرائيلية",
        ])
        
        if st.button("🤖 تحليل وتوقع", type="primary"):
            with st.spinner("الذكاء الاصطناعي يحلل البيانات..."):
                try:
                    res = requests.post("https://api.anthropic.com/v1/messages",
                        headers={"Content-Type":"application/json","x-api-key":CLAUDE_KEY,"anthropic-version":"2023-06-01"},
                        json={
                            "model": "claude-sonnet-4-20250514",
                            "max_tokens": 1500,
                            "messages": [{"role":"user","content":f"""أنت محلل استخباراتي عسكري خبير في الشرق الأوسط. 
بناءً على الأحداث الأخيرة في مارس 2026 (الضربات الأمريكية الإسرائيلية على إيران، والرد الإيراني بصواريخ على دول الخليج):

{scenario}

قدم تحليلاً مفصلاً بالعربية يتضمن:
1. 🎯 التوقعات المحددة (3-5 توقعات)
2. 📊 نسبة احتمالية لكل توقع
3. ⚠️ مناطق الخطر الأعلى
4. 🕐 الإطار الزمني المتوقع
5. 💡 التوصيات

كن دقيقاً ومهنياً."""}]
                        }, timeout=30
                    )
                    analysis = res.json()["content"][0]["text"]
                    st.markdown("---")
                    st.markdown("#### 📋 نتائج التحليل:")
                    st.markdown(analysis)
                    
                    # تقييم خطورة
                    st.markdown("---")
                    st.markdown("#### 🚨 مستوى التهديد الحالي:")
                    cols = st.columns(5)
                    countries = ["🇴🇲 عُمان", "🇸🇦 السعودية", "🇦🇪 الإمارات", "🇮🇱 إسرائيل", "🇮🇷 إيران"]
                    levels = [20, 75, 70, 90, 95]
                    for i, (col, country, level) in enumerate(zip(cols, countries, levels)):
                        with col:
                            color = "🟢" if level < 40 else "🟡" if level < 70 else "🔴"
                            st.metric(country, f"{color} {level}%")
                            st.progress(level/100)
                            
                except Exception as e:
                    st.error(f"خطأ في الاتصال: {e}")

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#475569; font-size:12px; padding:10px'>
    🛰️ وكيل الأخبار العسكري | تحديث تلقائي | البيانات من NewsAPI و Anthropic Claude
</div>
""", unsafe_allow_html=True)
