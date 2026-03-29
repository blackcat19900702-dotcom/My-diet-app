import streamlit as st
from datetime import datetime
import requests

# --- 1. 設定區：請填入你最新部署的 Apps Script 網址 ---
script_url = "https://script.google.com/macros/s/AKfycbyJJwrjQaIbVao0R5tqtS7l2mKLHifrU8O4ylwwG4yrmuyJZPna_clLAZLeAUkwUcXJ7A/exec"

st.set_page_config(page_title="99KG 減重戰情室", layout="centered")

# --- 2. 初始化熱量數據 (確保刷新頁面不會消失) ---
if 'daily_total_kcal' not in st.session_state:
    st.session_state.daily_total_kcal = 0.0

st.title("🔥 減重數據全紀錄系統")
st.caption("從 99kg 到 80kg 的每一刻都值得紀錄")

# --- 3. 身體數據與日期 ---
st.header("📅 今日狀態")
record_date = st.date_input("紀錄日期", datetime.now())

col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("體重 (kg)", value=99.0, step=0.1)
    body_fat = st.number_input("體脂率 (%)", value=31.0, step=0.1)
    visceral = st.number_input("內臟脂肪", value=18.0, step=0.5)
with col2:
    waist = st.number_input("腰圍 (cm)", value=104.0, step=0.1)
    hip = st.number_input("臀圍 (cm)", value=90.0, step=0.1)
    sleep_info = st.selectbox("睡眠品質", ["很好", "普通", "沒睡飽", "失眠"])

# --- 4. 生活習慣 ---
st.header("💧 運動與飲水")
c1, c2 = st.columns(2)
with c1:
    water = st.number_input("飲水量 (ml)", value=2000, step=100)
with c2:
    steps = st.number_input("累積步數", value=5000, step=500)

# --- 5. 熱量計算器 (原本被我刪掉的功能，全數補回) ---
st.header("🍱 今日飲食熱量")
with st.container():
    st.write("請輸入克數，系統會自動換算：")
    f1, f2, f3 = st.columns(3)
    with f1:
        meat_g = st.number_input("肉類/蛋白質 (g)", value=0, step=10)
    with f2:
        veg_g = st.number_input("蔬菜類 (g)", value=0, step=10)
    with f3:
        carb_g = st.number_input("澱粉/碳水 (g)", value=0, step=10)
    
    if st.button("➕ 計算並加入總熱量"):
        # 熱量公式：肉類約 2.5 kcal/g, 蔬菜 0.3 kcal/g, 澱粉 4 kcal/g (可依實際食材調整)
        this_meal = (meat_g * 2.5) + (veg_g * 0.3) + (carb_g * 4.0)
        st.session_state.daily_total_kcal += this_meal
        st.success(f"此餐增加 {this_meal:.1} kcal，目前累計：{st.session_state.daily_total_kcal:.1} kcal")

# 顯示總熱量與手動歸零
st.metric("今日總攝取熱量", f"{st.session_state.daily_total_kcal:.1} kcal")
if st.button("🗑️ 清空今日熱量"):
    st.session_state.daily_total_kcal = 0.0
    st.rerun()

st.divider()

# --- 6. 核心功能：一鍵入庫到 Google Excel ---
st.header("🚀 數據同步")

# 準備要發送給 Google 的數據袋
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

if st.button("✅ 數據入庫到 Google 試算表", use_container_width=True):
    try:
        response = requests.get(script_url, params=payload, timeout=10)
        if response.status_code == 200:
            st.success(f"同步成功！Google 回報：{response.text}")
            st.balloons()
        else:
            st.error(f"連線失敗，狀態碼：{response.status_code}")
    except Exception as e:
        st.error(f"連線發生錯誤：{e}")
