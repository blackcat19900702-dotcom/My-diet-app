import streamlit as st
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="內脂終結者：Excel 自動同步版", page_icon="📈")

# --- 1. 核心資料庫 (牛肉/雞肉/醬料精準版) ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0, "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0, "🚫 不吃主食 / 自定義": 0.0
}
meat_parts = {
    "牛肉": ["和尚頭(極瘦)", "嫩肩里肌(板腱)", "梅花牛", "肋眼(沙朗)", "牛肋條", "牛小排", "牛腱"],
    "雞肉": ["雞胸肉", "雞腿肉", "雞翅"],
    "豬肉": ["里肌肉(瘦)", "五花肉(肥)", "梅花豬", "豬絞肉"],
    "其他蛋白質": ["鮭魚", "鱈魚", "雞蛋", "豆腐"]
}
base_kcal_map = {
    "和尚頭(極瘦)": 1.2, "嫩肩里肌(板腱)": 1.4, "梅花牛": 2.0, "肋眼(沙朗)": 2.9, "牛肋條": 3.3, "牛小排": 3.8, "牛腱": 1.2,
    "雞胸肉": 1.1, "雞翅": 2.1, "里肌肉(瘦)": 1.8, "五花肉(肥)": 3.6, "梅花豬": 2.3, "豬絞肉": 2.5,
    "鮭魚": 2.1, "鱈魚": 1.0, "雞蛋": 1.4, "豆腐": 0.8
}
db_veggie = {"櫛瓜": 0.17, "茄子": 0.25, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3}
db_sauce = {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "氣炸/烤": 1.15, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

# --- 2. 狀態管理 (累計今日熱量) ---
if 'daily_total_kcal' not in st.session_state:
    st.session_state.daily_total_kcal = 0.0

# --- 3. 身體數據與日期選擇 ---
st.error(f"📉 內臟脂肪 18 減標計畫 | 目標：體重 99kg 穩定下降")

with st.container(border=True):
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        record_date = st.date_input("🗓️ 記錄日期 (可手動修改日期)", datetime.now())
    with col_d2:
        if st.button("🔄 重置今日計算"):
            st.session_state.daily_total_kcal = 0.0
            st.rerun()

with st.expander("📊 每日指標 (填寫完後點擊下方同步連結)", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        weight = st.number_input("體重 (kg)", value=99.0, step=0.1)
        body_fat = st.number_input("體脂 (%)", value=31.0, step=0.1)
        sleep_status = st.text_input("睡眠狀況", value="有睡飽")
    with c2:
        visceral = st.number_input("內臟脂肪", value=18.0, step=0.5)
        waist = st.number_input("腰圍 (cm)", value=104.0, step=0.1)
        water = st.number_input("飲水 (ml)", value=2500, step=250)
    with c3:
        hip = st.number_input("臀圍 (cm)", value=90.0, step=0.1)
        steps = st.number_input("步數", value=5000, step=500)
        st.metric("🔥 累計攝取", f"{st.session_state.daily_total_kcal:.1f} kcal")

# --- 4. 飲食錄入 ---
st.title("⚖️ 精準飲食紀錄")
with st.container(border=True):
    carb_choice = st.selectbox("1. 選擇主食", list(dietitian_carbs.keys()))
    source = st.radio("2. 來源", ["🏠 自煮", "🥡 外食(+35%)"], horizontal=True)
    risk_mult = 1.35 if "外食" in source else 1.0
    
    cat = st.selectbox("3. 食材類別", ["🥩 肉類/蛋白質", "🥦 青菜/纖維", "🧂 醬料/其他"])
    
    f_final_name, base_k, m_factor = "", 0.0, 1.0
    
    if cat == "🥩 肉類/蛋白質":
        m_type = st.selectbox("種類", list(meat_parts.keys()), index=1)
        part = st.selectbox("部位", meat_parts[m_type])
        if part == "雞腿肉":
            skin = st.radio("處理", ["🍗 帶皮", "✂️ 去皮"], horizontal=True)
            base_k = 1.2 if "去皮" in skin else 1.9
            f_final_name = f"雞腿({skin})"
        else:
            base_k = base_kcal_map.get(part, 1.5)
            f_final_name = part
        m_factor = method_map[st.selectbox("料理方式", list(method_map.keys()))]
    elif cat == "🥦 青菜/纖維":
        f_final_name = st.selectbox("青菜", list(db_veggie.keys()) + ["自定義"])
        if f_final_name == "自定義": f_final_name = st.text
