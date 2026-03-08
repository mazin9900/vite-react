import streamlit as st
import requests

# إعدادات الواجهة
st.set_page_config(page_title="مرصد أخبار عُمان والشرق الأوسط", layout="wide")
st.title("🛡️ وكيل الأخبار العسكرية والسياسية")

# المفتاح الخاص بك
MY_KEY = "2aff2eb940e54eb8bfb441c4ad07bbc1"

# البحث الافتراضي
query = st.text_input("أدخل موضوع البحث:", "Oman OR 'Middle East strikes'")

if st.button("تحديث الأخبار"):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={MY_KEY}&language=en"
    response = requests.get(url).json()
    
    if "articles" in response:
        articles = response['articles']
        for art in articles[:10]:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    if art.get('urlToImage'):
                        st.image(art['urlToImage'])
                with col2:
                    st.subheader(art['title'])
                    st.write(f"**المصدر:** {art['source']['name']}")
                    st.write(art['description'])
                    st.markdown(f"[إقرأ الخبر كاملاً]({art['url']})")
                st.divider()
    else:
        st.error("فشل في جلب البيانات")
```

---

## الخطوات الآن:

**1️⃣** اذهب لـ 👉 `github.com/mazin9900/vite-react`

**2️⃣** اضغط **Add file ← Create new file**

**3️⃣** سمّه `app.py` والصق الكود أعلاه

**4️⃣** اضغط **Commit changes** ✅

**5️⃣** كرر نفس الشيء وأنشئ ملف `requirements.txt` واكتب فيه:
```
streamlit
requests
