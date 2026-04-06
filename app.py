import streamlit as st
from datetime import datetime

# --- 1. 營養參數與目標 ---
GOALS = {
    "carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0
}
KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "fat": 45
}

# 初始化資料
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 本地紀錄器", layout="wide")

# --- 2. 主畫面 ---
st.title("🥗 2710kcal 飲食紀錄 (Excel 友善版)")

# 計算總熱量
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())

# 份數餘額顯示
st.subheader(f"🔥 今日熱量: {total_kcal:.0f} / 2710 kcal")
cols = st.columns(4)
for i, key in enumerate(GOALS.keys()):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i % 4].metric(key.upper(), f"剩 {rem:.1f}", delta=f"攝取 {st.session_state.daily[key]:.1f}")

# --- 3. 輸入區域 ---
st.divider()
c1, c2, c3 = st.columns(3)
cw = c1.number_input("熟澱粉重 (g)", 0.0, step=10.0)
pw = c2.number_input("肉類重量 (g)", 0.0, step=5.0)
ww = c3.number_input("飲水量 (ml)", 0.0, step=50.0, value=250.0)

if st.button("➕ 增加紀錄", use_container_width=True):
    st.session_state.daily["carbs"] += (cw/60)
    st.session_state.daily["protein_low"] += (pw/35)
    st.session_state.water += ww
    st.rerun()

# --- 4. Excel 複製功能 (重點) ---
st.divider()
st.subheader("📋 每日結算匯出")
st.write("輸入完畢後，點擊下方按鈕產出文字，直接貼上 Excel 即可分欄：")

# 準備 Excel 格式字串 (日期 + 熱量 + 各項數值 + 水)
date_str = datetime.now().strftime("%Y/%m/%d")
# 使用 \t (Tab鍵) 分隔，Excel 貼上時會自動拆分儲存格
excel_row = f"{date_str}\t{round(total_kcal)}\t" + \
            "\t".join([f"{round(st.session_state.daily[k], 1)}" for k in GOALS.keys()]) + \
            f"\t{round(st.session_state.water)}"

if st.button("生成 Excel 貼上文字"):
    st.code(excel_row, language="text")
    st.success("請「全選並複製」上面的深色區塊文字，然後到 Excel 貼上即可！")

# 重置按鈕
if st.button("🔄 重置今日數據", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
