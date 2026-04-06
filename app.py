import streamlit as st
from datetime import datetime

# 1. 嚴格欄位定義 (對齊你的 Excel 欄位順序)
# 順序：澱粉, 奶類, 低脂肉, 中脂肉, 蔬菜, 水果, 油脂, 鹽分
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

# 2. 數據計算與顯示
total_kcal = sum(st.session_state.daily[k] * GOALS[k]["kcal"] for k in GOALS.keys())
st.title(f"🔥 今日總計: {total_kcal:.0f} / 2710 kcal")

# 3. 完整輸入區 (補齊所有漏掉的欄位)
st.subheader("📝 進食紀錄 (輸入重量自動換算份數)")
c1, c2, c3 = st.columns(3)
with c1:
    in_carbs_g = st.number_input("熟澱粉 (g) [60g=1份]", 0.0, step=10.0)
    in_veggie_g = st.number_input("熟蔬菜 (g) [100g=1份]", 0.0, step=10.0)
with c2:
    in_protein_g = st.number_input("肉類 (g) [35g=1份]", 0.0, step=5.0)
    in_fruit_n = st.number_input("水果 (份)", 0.0, step=0.5)
with c3:
    in_milk_n = st.number_input("奶類 (份)", 0.0, step=0.5)
    in_water_ml = st.number_input("飲水 (ml)", 0.0, step=50.0, value=250.0)

# 其他手動微調 (油脂與鹽分)
st.write("---")
c4, c5 = st.columns(2)
in_fat_n = c4.number_input("油脂 (份)", 0.0, step=0.5)
in_salt_n = c5.number_input("鹽分 (份)", 0.0, step=0.5)

if st.button("➕ 存入今日紀錄", use_container_width=True):
    st.session_state.daily["carbs"] += (in_carbs_g / 60)
    st.session_state.daily["veggie"] += (in_veggie_g / 100)
    st.session_state.daily["pro_low"] += (in_protein_g / 35)
    st.session_state.daily["fruit"] += in_fruit_n
    st.session_state.daily["milk"] += in_milk_n
    st.session_state.daily["fat"] += in_fat_n
    st.session_state.daily["salt"] += in_salt_n
    st.session_state.water += in_water_ml
    st.rerun()

# 4. Excel 匯出 (嚴格對齊日期、熱量、八大項、水)
st.divider()
st.subheader("📋 Excel 結算 (全選複製貼上)")
date_str = datetime.now().strftime("%Y/%m/%d")
excel_values = [
    date_str, 
    str(round(total_kcal)),
    *[f"{round(st.session_state.daily[k], 1)}" for k in GOALS.keys()],
    str(round(st.session_state.water))
]
excel_row = "\t".join(excel_values)
st.code(excel_row, language="text")

# 5. 重置功能
if st.button("🔄 清除數據 (開啟新的一天)", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
