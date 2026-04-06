import streamlit as st
from datetime import datetime

# --- 1. 營養目標設定 (2710kcal) ---
GOALS = {
    "carbs":   {"name": "澱粉", "target": 16.0, "kcal": 70},
    "milk":    {"name": "奶類", "target": 3.0, "kcal": 150},
    "pro_low": {"name": "低脂肉", "target": 7.0, "kcal": 55},
    "pro_mid": {"name": "中脂肉", "target": 3.5, "kcal": 75},
    "veggie":  {"name": "蔬菜", "target": 4.0, "kcal": 25},
    "fruit":   {"name": "水果", "target": 3.0, "kcal": 60},
    "fat":     {"name": "油脂", "target": 5.5, "kcal": 45},
    "salt":    {"name": "鹽分", "target": 4.0, "kcal": 0}
}

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 飲食紀錄", layout="wide")

# --- 2. 顯示目前的數值 ---
total_kcal = sum(st.session_state.daily[k] * GOALS[k]["kcal"] for k in GOALS.keys())
st.title(f"🔥 今日總熱量: {total_kcal:.0f} / 2710 kcal")

cols = st.columns(4)
for i, (key, data) in enumerate(GOALS.items()):
    cur = st.session_state.daily[key]
    rem = data["target"] - cur
    cols[i % 4].metric(data["name"], f"剩 {rem:.1f}", delta=f"攝取 {cur:.1f}")

# --- 3. 自動判斷輸入區 ---
st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    in_carbs_g = st.number_input("熟澱粉重量 (g) [60g=1份]", 0.0, step=10.0)
    in_veggie_g = st.number_input("熟蔬菜重量 (g) [100g=1份]", 0.0, step=10.0)
    in_fruit = st.number_input("水果份數", 0.0, step=0.5)

with c2:
    in_pro_g = st.number_input("肉類總重量 (g) [35g=1份]", 0.0, step=5.0)
    pro_type = st.radio("肉類油份判定", ["偏瘦 (全低脂)", "各半 (50/50)", "偏肥 (全中脂)"], horizontal=True)
    in_milk = st.number_input("奶類份數", 0.0, step=0.5)

with c3:
    in_water = st.number_input("飲水量 (ml)", 0.0, step=50.0, value=250.0)
    in_fat = st.number_input("油脂 (份)", 0.0, step=0.5)
    in_salt = st.number_input("鹽分 (份)", 0.0, step=0.5)

if st.button("➕ 存入紀錄", use_container_width=True):
    # 澱粉與蔬菜自動換算
    st.session_state.daily["carbs"] += (in_carbs_g / 60)
    st.session_state.daily["veggie"] += (in_veggie_g / 100)
    
    # 肉類自動判定邏輯
    servings = (in_pro_g / 35)
    if pro_type == "偏瘦 (全低脂)":
        st.session_state.daily["pro_low"] += servings
    elif pro_type == "偏肥 (全中脂)":
        st.session_state.daily["pro_mid"] += servings
    else:
        st.session_state.daily["pro_low"] += (servings * 0.5)
        st.session_state.daily["pro_mid"] += (servings * 0.5)
    
    st.session_state.daily["fruit"] += in_fruit
    st.session_state.daily["milk"] += in_milk
    st.session_state.daily["fat"] += in_fat
    st.session_state.daily["salt"] += in_salt
    st.session_state.water += in_water
    st.rerun()

# --- 4. Excel 匯出字串 ---
st.divider()
st.subheader("📋 Excel 貼上文字")
date_str = datetime.now().strftime("%Y/%m/%d")
excel_values = [
    date_str, 
    str(round(total_kcal)),
    *[f"{round(st.session_state.daily[k], 1)}" for k in GOALS.keys()],
    str(round(st.session_state.water))
]
excel_row = "\t".join(excel_values)
st.code(excel_row, language="text")

# --- 5. 重置功能 ---
if st.button("🔄 重置今日數據", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
