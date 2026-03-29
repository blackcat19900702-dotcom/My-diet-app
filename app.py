import streamlit as st
from datetime import datetime
import requests

# --- 1. 設定區：請填入你最新部署的 Apps Script 網址 ---
script_url = "https://script.google.com/macros/s/AKfycbyJJwrjQaIbVao0R5tqtS7l2mKLHifrU8O4ylwwG4yrmuyJZPna_clLAZLeAUkwUcXJ7A/exec"

st.set_page_config(page_title="99KG 減重戰情室", layout="wide")

# 初始化 Session State
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'total_kcal' not in st.session_state:
    st.session_state.total_kcal = 0.0

st.title("🔥 99KG 減重計畫：全功能紀錄系統")

# --- 側邊欄：身體數據紀錄 ---
with st.sidebar:
    st.header("⚖️ 今日身體數據")
    record_date = st.date_input("紀錄日期", datetime.now())
    weight = st.number_input("體重 (kg)", value=99.0, step=0.1)
    body_fat = st.number_input("體脂率 (%)", value=31.0, step=0.1)
    visceral = st.number_input("內臟脂肪", value=18.0, step=0.5)
    st.divider()
    waist = st.number_input("腰圍 (cm)", value=104.0, step=0.1)
    hip = st.number_input("臀圍 (cm)", value=90.0, step=0.1)
    st.divider()
    water = st.number_input("飲水量 (ml)", value=2000, step=100)
    steps = st.number_input("累積步數", value=5000, step=500)
    sleep_info = st.selectbox("睡眠品質", ["很好", "普通", "沒睡飽", "失眠"])

# --- 主界面：熱量計算器 (原版完整功能) ---
st.header("🍱 飲食熱量計算")

col1, col2 = st.columns([2, 1])

with col1:
    food_type = st.selectbox("食物類別", ["肉類(豬/牛)", "肉類(雞/魚/海鮮)", "澱粉類", "蔬菜類", "水果/其他"])
    amount = st.number_input("輸入克數 (g)", value=0, step=10)
    
    if st.button("➕ 加入此餐紀錄"):
        # 回歸你原始的精確換算率
        kcal_map = {
            "肉類(豬/牛)": 2.5,
            "肉類(雞/魚/海鮮)": 1.5,
            "澱粉類": 1.4,
            "蔬菜類": 0.3,
            "水果/其他": 0.6
        }
        current_kcal = amount * kcal_map[food_type]
        st.session_state.total_kcal += current_kcal
        st.session_state.logs.append(f"{food_type}: {amount}g ({current_kcal:.1f} kcal)")
        st.success(f"已加入 {food_type} {amount}g")

with col2:
    st.subheader("📝 今日清單")
    for log in st.session_state.logs:
        st.text(log)
    st.metric("目前總熱量", f"{st.session_state.total_kcal:.1f} kcal")
    if st.button("🗑️ 全部清空"):
        st.session_state.logs = []
        st.session_state.total_kcal = 0.0
        st.rerun()

st.divider()

# --- 核心功能：一鍵同步到 Google Excel ---
st.header("🚀 數據同步至雲端")
st.info("確認數據無誤後，按下下方按鈕即可同步至 Google 試算表。")

# 整理傳送數據
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
    "kcal": round(st.session_state.total_kcal, 1)
}

if st.button("✅ 確認入庫 (不跳轉)", use_container_width=True):
    try:
        response = requests.get(script_url, params=payload, timeout=10)
        if response.status_code == 200:
            st.success(f"同步成功！Google 回報：{response.text}")
            st.balloons()
        else:
            st.error(f"連線失敗，請檢查 Apps Script 網址與部署設定。")
    except Exception as e:
        st.error(f"連線發生錯誤：{e}")
