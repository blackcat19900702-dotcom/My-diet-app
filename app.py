import streamlit as st
from datetime import datetime

# 營養參數
GOALS = ["澱粉", "奶類", "低脂蛋豆魚肉", "中脂蛋豆魚肉", "蔬菜", "水果", "油脂", "鹽分"]
KCAL_MAP = [70, 150, 55, 75, 25, 60, 45, 0]

if 'daily' not in st.session_state:
    st.session_state.daily = [0.0] * len(GOALS)
    st.session_state.water = 0.0

st.title("⚖️ 飲食轉換器 (Excel 專用)")

# 1. 輸入區
col1, col2, col3 = st.columns(3)
cw = col1.number_input("澱粉重 (g)", 0.0, step=10.0)
pw = col2.number_input("肉重量 (g)", 0.0, step=5.0)
ww = col3.number_input("飲水 (ml)", 0.0, step=50.0, value=250.0)

if st.button("➕ 計算並累加", use_container_width=True):
    st.session_state.daily[0] += (cw/60)  # 澱粉換算
    st.session_state.daily[2] += (pw/35)  # 肉類換算
    st.session_state.water += ww
    st.rerun()

# 2. 目前進度顯示
total_kcal = sum(v * KCAL_MAP[i] for i, v in enumerate(st.session_state.daily))
st.subheader(f"🔥 今日累計: {total_kcal:.0f} kcal")

# 3. 生成 Excel 文字
st.divider()
st.subheader("📋 Excel 貼上專區")

# 格式：日期 | 總熱量 | 澱粉 | 奶 | 低肉 | 中肉 | 菜 | 果 | 油 | 鹽 | 水
date_str = datetime.now().strftime("%Y/%m/%d")
excel_row = f"{date_str}\t{round(total_kcal)}\t" + \
            "\t".join([f"{round(v, 1)}" for v in st.session_state.daily]) + \
            f"\t{round(st.session_state.water)}"

st.text("點擊下方框內文字全選複製，然後在 Excel 貼上：")
st.code(excel_row, language="text")

if st.button("🔄 重置今日所有數據"):
    st.session_state.daily = [0.0] * len(GOALS)
    st.session_state.water = 0.0
    st.rerun()
