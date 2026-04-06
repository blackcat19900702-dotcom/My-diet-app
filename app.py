import streamlit as st
from datetime import datetime

# --- 1. 核心配額與換算 ---
GOALS = {
    "carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0
}

# 輔助計算熱量 (用於 Excel 統計)
KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "fat": 45, "salt": 0
}

CONV = {"carbs_g": 60, "protein_g": 35, "veggie_g": 100, "fruit_g": 100, "milk_ml": 240}

# 肉類資料庫
MEAT_DATABASE = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", 
    "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", 
    "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"
}

GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧導航", layout="wide")

# --- 2. 儀表板 ---
st.title("⚖️ 2710kcal 智慧飲食監控")

# 計算總熱量
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())

st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / 2710 kcal")

cols = st.columns(6)
items = [
    ("🍞 主食", "carbs"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"),
    ("🥦 蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]

for i, (label, key) in enumerate(items):
    current = st.session_state.daily[key]
    rem = GOALS[key] - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已攝取")

# --- 3. 自動化紀錄區 ---
st.divider()
t1, t2, t3, t4 = st.tabs(["🍚 澱粉/奶類", "🥩 肉類(自動判別)", "🥬 蔬菜", "🥤 飲水與其他"])

with t1:
    c_w = st.number_input("熟主食重量 (g)", min_value=0.0, step=10.0)
    m_ml = st.number_input("奶類/優酪乳 (ml)", min_value=0.0, step=100.0)
    if st.button("➕ 紀錄澱粉與奶"):
        st.session_state.daily["carbs"] += (c_w / CONV["carbs_g"])
        st.session_state.daily["milk"] += (m_ml / CONV["milk_ml"])
        st.rerun()

with t2:
    m_part = st.selectbox("選擇肉類部位", list(MEAT_DATABASE.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    method = st.selectbox("烹調方式", ["水煮/清蒸", "乾煎/油炒", "油炸"])
    outside = st.checkbox("這餐是外食")
    
    if st.button("➕ 紀錄肉類"):
        fat_level = MEAT_DATABASE[m_part]
        servings = m_w / CONV["protein_g"]
        if fat_level == "low":
            st.session_state.daily["protein_low"] += servings
        else:
            st.session_state.daily["protein_mid"] += servings
            
        f_add = 1.0 if method == "乾煎/油炒" else (3.5 if method == "油炸" else 0.0)
        if outside: f_add += 1.5
        st.session_state.daily["fat"] += f_add
        st.rerun()

with t3:
    v_name = st.selectbox("選擇蔬菜", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("熟菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        st.session_state.daily["veggie"] += (v_w / CONV["veggie_g"])
        st.rerun()

with t4:
    f_w = st.number_input("水果重量 (g)", min_value=0.0)
    salt_g = st.number_input("鹽巴量 (g)", min_value=0.0)
    w_ml = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("➕ 紀錄其他"):
        st.session_state.daily["fruit"] += (f_w / CONV["fruit_g"])
        st.session_state.daily["salt"] += salt_g
        st.session_state.water += w_ml
        st.rerun()

# --- 4. Excel 結算區 ---
st.divider()
st.subheader("📋 Excel 結算複製貼上")

date_str = datetime.now().strftime("%Y/%m/%d")
# 依照你要求的順序排好
excel_data = [
    date_str, 
    str(round(total_kcal)),
    f"{round(st.session_state.daily['carbs'], 1)}",
    f"{round(st.session_state.daily['milk'], 1)}",
    f"{round(st.session_state.daily['protein_low'], 1)}",
    f"{round(st.session_state.daily['protein_mid'], 1)}",
    f"{round(st.session_state.daily['veggie'], 1)}",
    f"{round(st.session_state.daily['fruit'], 1)}",
    f"{round(st.session_state.daily['fat'], 1)}",
    f"{round(st.session_state.daily['salt'], 1)}",
    str(round(st.session_state.water))
]
excel_row = "\t".join(excel_data)

st.text("複製下方內容貼入 Excel：")
st.code(excel_row, language="text")

if st.button("🔄 開啟新的一天", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
