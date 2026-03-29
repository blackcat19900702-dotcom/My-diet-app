import streamlit as st
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="內脂終結者：克數精準版", page_icon="⚖️")

# --- 1. 核心資料庫 (數值皆為每克 kcal) ---
# 主食類 (改為每克計)
db_carbs = {
    "🍚 白米飯": 1.4,      # 240g 約 336kcal
    "🌾 五穀米": 1.33,
    "🍜 白麵條(煮熟)": 1.15,
    "🌽 玉米/地瓜": 1.2
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
db_sauce = {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6, "辣椒醬": 1.5}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "氣炸/烤": 1.15, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

if 'daily_total_kcal' not in st.session_state:
    st.session_state.daily_total_kcal = 0.0

# --- 2. 身體數據與日期 ---
st.error(f"📉 內臟脂肪 18 減標計畫 | 當前體重: 99kg")

with st.expander("📊 每日指標 (同步至 Excel)", expanded=False):
    record_date = st.date_input("🗓️ 記錄日期", datetime.now())
    c1, c2, c3 = st.columns(3)
    with c1:
        weight = st.number_input("體重 (kg)", value=99.0)
        body_fat = st.number_input("體脂 (%)", value=31.0)
        sleep_status = st.text_input("睡眠狀況", value="有睡飽")
    with c2:
        visceral = st.number_input("內臟脂肪", value=18.0)
        waist = st.number_input("腰圍 (cm)", value=104.0)
        water = st.number_input("飲水 (ml)", value=2500)
    with c3:
        hip = st.number_input("臀圍 (cm)", value=90.0)
        steps = st.number_input("步數 ", value=5000)
        if st.button("🔄 清空今日熱量"):
            st.session_state.daily_total_kcal = 0.0
            st.rerun()

# --- 3. 精準飲食錄入 (克數核心區) ---
st.title("⚖️ 食材克數精準紀錄")

# 這裡設計成三個並排的區塊，方便快速切換
tab1, tab2, tab3, tab4 = st.tabs(["🍚 主食", "🥩 肉類", "🥦 蔬菜", "🧂 醬料"])

with tab1:
    c_name = st.selectbox("選擇澱粉來源", list(db_carbs.keys()))
    c_weight = st.number_input(f"{c_name} 的重量 (g)", min_value=0.0, step=1.0, key="c_w")
    c_kcal = db_carbs[c_name] * c_weight
    st.info(f"💡 預計熱量: {c_kcal:.1f} kcal")
    if st.button("➕ 加入主食熱量"):
        st.session_state.daily_total_kcal += c_kcal
        st.success(f"已加入 {c_name} {c_weight}g")

with tab2:
    m_type = st.selectbox("肉類種類", list(meat_parts.keys()))
    part = st.selectbox("部位", meat_parts[m_type])
    
    # 雞腿特別處理
    base_k = base_kcal_map.get(part, 1.5)
    if part == "雞腿肉":
        skin = st.radio("處理", ["去皮", "帶皮"], horizontal=True)
        base_k = 1.2 if skin == "去皮" else 1.9

    method = st.selectbox("料理方式", list(method_map.keys()))
    source = st.radio("來源", ["自煮", "外食(+35%油)"], horizontal=True, key="m_s")
    
    m_weight = st.number_input(f"{part} 的重量 (g)", min_value=0.0, step=1.0, key="m_w")
    
    risk_mult = 1.35 if "外食" in source else 1.0
    m_kcal = base_k * method_map[method] * m_weight * risk_mult
    st.info(f"💡 預計熱量: {m_kcal:.1f} kcal")
    
    if st.button("➕ 加入肉類熱量"):
        st.session_state.daily_total_kcal += m_kcal
        st.success(f"已加入 {part} {m_weight}g")

with tab3:
    v_name = st.selectbox("蔬菜種類", list(db_veggie.keys()))
    v_method = st.selectbox("蔬菜料理方式", list(method_map.keys()))
    v_weight = st.number_input(f"{v_name} 的重量 (g)", min_value=0.0, step=1.0, key="v_w")
    v_kcal = db_veggie[v_name] * method_map[v_method] * v_weight
    st.info(f"💡 預計熱量: {v_kcal:.1f} kcal")
    if st.button("➕ 加入蔬菜熱量"):
        st.session_state.daily_total_kcal += v_kcal

with tab4:
    s_name = st.selectbox("醬料/其他", list(db_sauce.keys()) + ["自定義"])
    s_weight = st.number_input("重量/份量 (g/ml)", min_value=0.0, step=1.0, key="s_w")
    base_s = db_sauce.get(s_name, 0.5)
    s_kcal = base_s * s_weight
    if st.button("➕ 加入醬料熱量"):
        st.session_state.daily_total_kcal += s_kcal

# --- 4. 總結與同步 ---
st.divider()
st.metric("🔥 今日總攝取熱量", f"{st.session_state.daily_total_kcal:.1f} kcal")

form_url = "https://docs.google.com/forms/d/e/1FAIpQLScBXA_T1mVeTkgia3MAaK-8mZ08CXLdx9g23TC25STF4vcH_g/viewform?"
params = {
    "entry.1008699507": record_date.strftime('%Y-%m-%d'),
    "entry.803335590": weight,
    "entry.2125421230": body_fat,
    "entry.1406870177": visceral,
    "entry.1589673803": waist,
    "entry.80267593": hip,
    "entry.634834497": sleep_status,
    "entry.91499640": water,
    "entry.1103411530": steps,
    "entry.1880995283": f"{st.session_state.daily_total_kcal:.1f}"
}
export_link = form_url + urllib.parse.urlencode(params)

st.link_button("🚀 同步今日數據至 Excel", export_link, use_container_width=True)
