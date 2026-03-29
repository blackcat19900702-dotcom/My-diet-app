import streamlit as st
import requests
from datetime import datetime

# --- 設定網頁標題 ---
st.set_page_config(page_title="內脂終結者：自動同步版", page_icon="🔥", layout="centered")

# --- 1. 核心資料庫 (每克 kcal) ---
# 主食類
db_carbs = {"🍚 白米飯": 1.4, "🌾 五穀米": 1.33, "🍜 白麵條": 1.15, "🌽 玉米/地瓜": 1.2}

# 肉類與蛋白質
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

# 蔬菜類 (已整合你要求新增的所有種類)
db_veggie = {
    "櫛瓜": 0.17, "茄子": 0.25, "青菜": 0.2, "高麗菜": 0.25, "白花椰": 0.25, 
    "綠花椰": 0.28, "娃娃菜": 0.2, "菠菜": 0.22, "地瓜葉": 0.28, "空心菜": 0.2, 
    "絲瓜": 0.17, "洋蔥": 0.4, "雪白菇": 0.25, "鴻禧菇": 0.25
}

# 醬料與料理方式
db_sauce = {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6, "辣椒醬": 1.5}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "氣炸/烤": 1.15, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

# 狀態管理
if 'daily_total_kcal' not in st.session_state:
    st.session_state.daily_total_kcal = 0.0

# --- 2. 身體指標與日期 ---
st.error(f"📉 減重戰鬥日：{datetime.now().strftime('%Y-%m-%d')} | 目標：內脂 18 降標")

with st.expander("📊 每日身體數據 (Excel 欄位)", expanded=True):
    record_date = st.date_input("🗓️ 記錄日期 (可手動修改)", datetime.now())
    c1, c2, c3 = st.columns(3)
    with c1:
        weight = st.number_input("體重 (kg)", value=99.0, step=0.1)
        body_fat = st.number_input("體脂 (%)", value=31.0, step=0.1)
        sleep_info = st.text_input("睡眠狀況", value="有睡飽")
    with c2:
        visceral = st.number_input("內臟脂肪", value=18.0, step=0.5)
        waist = st.number_input("腰圍 (cm)", value=104.0, step=0.1)
        water = st.number_input("飲水 (ml)", value=2500, step=250)
    with c3:
        hip = st.number_input("臀圍 (cm)", value=90.0, step=0.1)
        steps = st.number_input("今日步數", value=5000, step=500)
        if st.button("🔄 重置今日計算"):
            st.session_state.daily_total_kcal = 0.0
            st.rerun()

# --- 3. 精準克數錄入區 ---
st.title("⚖️ 食材克數精準紀錄")
tabs = st.tabs(["🍚 主食", "🥩 肉類", "🥦 蔬菜", "🧂 醬料"])

with tabs[0]:
    c_name = st.selectbox("來源", list(db_carbs.keys()))
    c_w = st.number_input(f"{c_name} 克數(g)", min_value=0.0, step=1.0)
    if st.button("➕ 加入主食"):
        st.session_state.daily_total_kcal += (c_w * db_carbs[c_name])
        st.toast(f"已計入 {c_name}")

with tabs[1]:
    m_type = st.selectbox("種類", list(meat_parts.keys()), index=1)
    part = st.selectbox("部位", meat_parts[m_type])
    base_k = base_kcal_map.get(part, 1.5)
    if part == "雞腿肉":
        skin = st.radio("處理", ["去皮", "帶皮"], horizontal=True)
        base_k = 1.2 if skin == "去皮" else 1.9
    method = st.selectbox("料理方式", list(method_map.keys()))
    source = st.radio("來源", ["自煮", "外食(+35%油)"], horizontal=True)
    m_w = st.number_input(f"{part} 克數(g)", min_value=0.0, step=1.0)
    if st.button("➕ 加入肉類"):
        kcal = base_k * method_map[method] * m_w * (1.35 if "外食" in source else 1.0)
        st.session_state.daily_total_kcal += kcal
        st.toast(f"已計入 {part}")

with tabs[2]:
    v_name = st.selectbox("蔬菜", list(db_veggie.keys()))
    v_method = st.selectbox("料理 ", list(method_map.keys()), key="v_method")
    v_w = st.number_input(f"{v_name} 克數(g) ", min_value=0.0, step=1.0, key="v_weight")
    if st.button("➕ 加入蔬菜"):
        st.session_state.daily_total_kcal += (v_w * db_veggie[v_name] * method_map[v_method])
        st.toast(f"已計入 {v_name}")

with tabs[3]:
    s_name = st.selectbox("醬料", list(db_sauce.keys()) + ["自定義"])
    s_w = st.number_input("份量(g/ml)", min_value=0.0, step=1.0)
    if st.button("➕ 加入醬料"):
        st.session_state.daily_total_kcal += (s_w * db_sauce.get(s_name, 0.5))

# --- 4. 數據同步 (與 Google Sheets 對接) ---
st.divider()
st.subheader(f"🔥 今日累計攝取：{st.session_state.daily_total_kcal:.1f} kcal")

# 這裡請貼入你剛才測試成功的那串 /exec 網址
script_url = "https://script.google.com/macros/s/AKfycbyJJwrjQaIbVao0R5tqtS7l2mKLHifrU8O4ylwwG4yrmuyJZPna_clLAZLeAUkwUcXJ7A/exec"

if st.button("🚀 數據直接入庫 (不跳轉)", use_container_width=True):
    payload = {
        "date": record_date.strftime('%Y-%m-%d'),
        "weight": weight, 
        "body_fat": body_fat, 
        "visceral": visceral,
        "waist": waist, 
        "hip": hip, 
        "sleep": sleep_info,
        "water": water, 
        "steps": steps, 
        "kcal": round(st.session_state.daily_total_kcal, 1)
    }
    try:
        response = requests.get(script_url, params=payload, timeout=10)
        if response.status_code == 200:
            st.success(f"✅ Excel 錄入成功！Google 回報：{response.text}")
            st.balloons()
        else:
            st.error(f"❌ 同步失敗，代碼：{response.status_code}")
    except Exception as e:
        st.error(f"❌ 連線異常：{e}")
