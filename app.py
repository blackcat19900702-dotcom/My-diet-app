import streamlit as st
from datetime import datetime

# --- 1. 營養參數與目標 (2710kcal 嚴格配置) ---
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

st.set_page_config(page_title="2710kcal 專業監控", layout="wide")

# --- 2. 數據顯示區 ---
total_kcal = sum(st.session_state.daily[k] * GOALS[k]["kcal"] for k in GOALS.keys())
st.title(f"🚀 今日總熱量: {total_kcal:.0f} / 2710 kcal")

# 份數餘額卡片
cols = st.columns(4)
for i, (key, data) in enumerate(GOALS.items()):
    cur = st.session_state.daily[key]
    rem = data["target"] - cur
    cols[i % 4].metric(data["name"], f"剩 {rem:.1f}", delta=f"已攝 {cur:.1f}")

# --- 3. 核心功能：自動判定輸入區 ---
st.divider()
st.subheader("📝 進食數據輸入")

c1, c2, c3 = st.columns(3)

with c1:
    in_carbs_g = st.number_input("熟澱粉重量 (g)", 0.0, step=10.0, help="60g=1份")
    in_veggie_g = st.number_input("熟蔬菜重量 (g)", 0.0, step=10.0, help="100g=1份")
    in_fruit = st.number_input("水果 (份數)", 0.0, step=0.5)

with c2:
    # 肉類自動判定邏輯
    in_pro_g = st.number_input("肉類總重量 (g)", 0.0, step=5.0, help="35g=1份")
    pro_type = st.radio("肉類油份判定", ["偏瘦 (全歸低脂)", "適中 (50/50)", "偏肥 (全歸中脂)"], horizontal=True)
    in_milk = st.number_input("奶類 (份數)", 0.0, step=0.5)

with c3:
    in_water = st.number_input("飲水量 (ml)", 0.0, step=50.0, value=250.0)
    in_fat = st.number_input("額外油脂 (份)", 0.0, step=0.5)
    in_salt = st.number_input("鹽分 (份)", 0.0, step=0.5)

if st.button("➕ 確認計算並存入暫存", use_container_width=True):
    # 1. 澱粉與蔬菜換算
    st.session_state.daily["carbs"] += (in_carbs_g / 60)
    st.session_state.daily["veggie"] += (in_veggie_g / 100)
    
    # 2. 肉類自動判定分配
    total_pro_servings = (in_pro_g / 35)
    if pro_type == "偏瘦 (全歸低脂)":
        st.session_state.daily["pro_low"] += total_pro_servings
    elif pro_type == "偏肥 (全歸中脂)":
        st.session_state.daily["pro_mid"] += total_pro_servings
    else: # 50/50 分配
        st.session_state.daily["pro_low"] += (total_pro_servings * 0.5)
        st.session_state.daily["pro_mid"] += (total_pro_servings * 0.5)
    
    # 3. 其他直接輸入項
    st.session_state.daily["fruit"] += in_fruit
    st.session_state.daily["milk"] += in_milk
    st.session_state.daily["fat"] += in_fat
    st.session_state.daily["salt"] += in_salt
    st.session_state.water += in_water
    st.rerun()

# --- 4. Excel 結算區 (維持原本的強健格式) ---
st.divider()
st.subheader("📋 Excel 一鍵貼上格式")
date_str = datetime.now().strftime("%Y/%m/%d")
# 順序：日期, 熱量, 澱粉, 奶類, 低脂, 中脂, 蔬菜, 水果, 油脂, 鹽分, 水
excel_data = [
    date_str, 
    str(round(total_kcal)),
    *[f"{round(st.session_state.daily[k], 1)}" for k in GOALS.keys()],
    str(round(st.session_state.water))
]
excel_row = "\t".join(excel_data)

st.code(excel_row, language="text")
st.caption("欄位順序已對齊：日期 | 熱量 | 澱粉 | 奶類 | 低脂肉 | 中脂肉 | 蔬菜 | 水果 | 油脂 | 鹽分 | 水")

if st.button("🔄 重置今日紀錄"):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
