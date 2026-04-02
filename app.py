import streamlit as st
import requests
from datetime import datetime

# --- 1. 營養師 2710 kcal 基準配額 ---
GOALS = {
    "carbs": 16.0,      "protein_low": 7.0, 
    "protein_mid": 3.5, "veggie": 4.0,      
    "veggie_green": 2.0,"fruit": 3.0,       
    "milk": 3.0,        "fat": 5.5,         
    "salt": 4.0,        "kcal": 2710.0
}

# 熟重換算率
CONV = {"carbs_g": 60, "protein_g": 35, "veggie_g": 100, "fruit_g": 100, "milk_ml": 240}

# 食材清單分類
low_meat = ["雞胸肉", "雞腿肉(去皮)", "和尚頭(牛)", "牛腱", "里肌肉(豬)", "鱈魚", "豆腐"]
mid_meat = ["雞蛋", "鮭魚", "嫩肩里肌(板腱)", "梅花豬", "豬絞肉", "雞腿肉(帶皮)"]
green_veggies = ["綠花椰", "菠菜", "地瓜葉", "空心菜"]
other_veggies = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

# 初始化
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}

st.set_page_config(page_title="2710kcal 飲食導航", layout="wide")

# --- 2. 儀表板：剩餘份數監控 ---
st.title("⚖️ 2710kcal 飲食配額監控")
cols = st.columns(6)
items = [
    ("🍞 主食", "carbs"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"),
    ("🥦 蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]

for i, (label, key) in enumerate(items):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{st.session_state.daily[key]:.1f} 已吃", delta_color="inverse")

# --- 3. 分類紀錄區 ---
st.divider()
t1, t2, t3, t4 = st.tabs(["🍚 澱粉/奶", "🥩 蛋白質", "🥬 蔬菜", "🧂 其他(水果/鹽/油)"])

with t1:
    c_w = st.number_input("熟主食重量 (g)", min_value=0.0, step=10.0)
    m_ml = st.number_input("奶類/優酪乳 (ml)", min_value=0.0, step=100.0)
    if st.button("➕ 加入紀錄", key="add_t1"):
        st.session_state.daily["carbs"] += (c_w / CONV["carbs_g"])
        st.session_state.daily["milk"] += (m_ml / CONV["milk_ml"])
        st.rerun()

with t2:
    m_part = st.selectbox("肉類部位", low_meat + mid_meat)
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    method = st.selectbox("烹調方式", ["水煮/清蒸", "乾煎/油炒", "油炸"])
    outside = st.checkbox("這餐是外食")
    if st.button("➕ 加入紀錄", key="add_t2"):
        if m_part in low_meat: st.session_state.daily["protein_low"] += (m_w / CONV["protein_g"])
        else: st.session_state.daily["protein_mid"] += (m_w / CONV["protein_g"])
        f_add = 1.0 if method == "乾煎/油炒" else (3.0 if method == "油炸" else 0.0)
        if outside: f_add += 1.5
        st.session_state.daily["fat"] += f_add
        st.rerun()

with t3:
    v_name = st.selectbox("蔬菜種類", green_veggies + other_veggies)
    v_w = st.number_input("熟菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 加入紀錄", key="add_t3"):
        servings = v_w / CONV["veggie_g"]
        st.session_state.daily["veggie"] += servings
        if v_name in green_veggies: st.session_state.daily["veggie_green"] += servings
        st.rerun()

with t4:
    f_w = st.number_input("水果 (g)", min_value=0.0)
    oil_g = st.number_input("額外油脂 (g)", min_value=0.0)
    salt_g = st.number_input("鹽巴 (g)", min_value=0.0)
    if st.button("➕ 加入紀錄", key="add_t4"):
        st.session_state.daily["fruit"] += (f_w / CONV["fruit_g"])
        st.session_state.daily["fat"] += (oil_g / 5)
        st.session_state.daily["salt"] += salt_g
        st.rerun()

# --- 4. 數據同步 ---
st.divider()
if st.button("🚀 完成今日紀錄並存入 Excel", use_container_width=True):
    payload = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "carbs": round(st.session_state.daily["carbs"], 1),
        "pro_low": round(st.session_state.daily["protein_low"], 1),
        "pro_mid": round(st.session_state.daily["protein_mid"], 1),
        "veg_total": round(st.session_state.daily["veggie"], 1),
        "veg_green": round(st.session_state.daily["veggie_green"], 1),
        "fruit": round(st.session_state.daily["fruit"], 1),
        "milk": round(st.session_state.daily["milk"], 1),
        "fat": round(st.session_state.daily["fat"], 1),
        "salt": round(st.session_state.daily["salt"], 1),
        "kcal": 2710 # 固定的基準目標
    }
    # 這裡放你的 requests.get(script_url, params=payload)
    st.success("指南數據已精準入庫！已清空今日紀錄。")
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
