import streamlit as st
from datetime import datetime

# --- 1. 嚴格定義欄位與目標 (2710kcal 配置) ---
# 欄位順序：澱粉, 奶類, 低脂肉, 中脂肉, 蔬菜, 水果, 油脂, 鹽分
GOALS = {
    "carbs": {"name": "澱粉", "target": 16.0, "kcal": 70},
    "milk": {"name": "奶類", "target": 3.0, "kcal": 150},
    "pro_low": {"name": "低脂肉", "target": 7.0, "kcal": 55},
    "pro_mid": {"name": "中脂肉", "target": 3.5, "kcal": 75},
    "veggie": {"name": "蔬菜", "target": 4.0, "kcal": 25},
    "fruit": {"name": "水果", "target": 3.0, "kcal": 60},
    "fat": {"name": "油脂", "target": 5.5, "kcal": 45},
    "salt": {"name": "鹽分", "target": 4.0, "kcal": 0}
}

# 初始化資料
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 專業監控", layout="wide")

# --- 2. 主畫面與數據計算 ---
st.title("⚖️ 2710kcal 飲食精確監控系統")

# 計算總熱量
total_kcal = sum(st.session_state.daily[k] * GOALS[k]["kcal"] for k in GOALS.keys())

# 份數餘額顯示 (恢復原本的 Metric 卡片)
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / 2710 kcal")
cols = st.columns(4)
for i, (key, data) in enumerate(GOALS.items()):
    current = st.session_state.daily[key]
    rem = data["target"] - current
    cols[i % 4].metric(
        f"{data['name']}", 
        f"剩 {rem:.1f}", 
        delta=f"已攝 {current:.1f}",
        delta_color="inverse" if current > data["target"] else "normal"
    )

# --- 3. 快速輸入區 (保留換算公式) ---
st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    cw = st.number_input("熟澱粉重量 (g)", 0.0, step=10.0, help="60g = 1份")
with c2:
    pw = st.number_input("肉類重量 (g)", 0.0, step=5.0, help="35g = 1份")
with c3:
    win = st.number_input("飲水量 (ml)", 0.0, step=50.0, value=250.0)

if st.button("➕ 存入暫存紀錄", use_container_width=True):
    st.session_state.daily["carbs"] += (cw / 60)
    st.session_state.daily["pro_low"] += (pw / 35)
    st.session_state.water += win
    st.rerun()

# --- 4. EXCEL 匯出專區 (欄位完全對齊) ---
st.divider()
st.subheader("📋 Excel 結算複製 (手動同步)")
st.write("吃完一整天後，複製下方內容貼上 Excel：")

# 建立 Excel 格式字串：日期 | 熱量 | 澱粉 | 奶 | 低肉 | 中肉 | 菜 | 果 | 油 | 鹽 | 水
date_str = datetime.now().strftime("%Y/%m/%d")
excel_values = [
    date_str,
    str(round(total_kcal)),
    *[f"{round(st.session_state.daily[k], 1)}" for k in GOALS.keys()],
    str(round(st.session_state.water))
]
excel_row = "\t".join(excel_values)

st.code(excel_row, language="text")
st.caption("欄位順序：日期、熱量、澱粉、奶類、低脂肉、中脂肉、蔬菜、水果、油脂、鹽分、飲水")

# --- 5. 其他功能 ---
if st.button("🔄 開啟新的一天 (清空紀錄)", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
