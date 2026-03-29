import streamlit as st
from datetime import datetime
import requests

# --- 1. 設定區：請貼入你剛才部署得到的網址 ---
script_url = "https://script.google.com/macros/s/你的專屬ID/exec"

st.set_page_config(page_title="健康紀錄助手", layout="centered")

# --- 2. 初始化數據存儲 ---
if 'daily_total_kcal' not in st.session_state:
    st.session_state.daily_total_kcal = 0.0

st.title("🥗 99kg 減重計畫：數據入庫系統")

# --- 3. 數據輸入區 ---
with st.expander("📅 基礎數據與目標", expanded=True):
    record_date = st.date_input("選擇紀錄日期", datetime.now())
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("今日體重 (kg)", value=99.0, step=0.1)
        body_fat = st.number_input("體脂率 (%)", value=31.0, step=0.1)
        visceral = st.number_input("內臟脂肪", value=18.0, step=0.5)
    with col2:
        waist = st.number_input("腰圍 (cm)", value=104.0, step=0.1)
        hip = st.number_input("臀圍 (cm)", value=90.0, step=0.1)
        sleep_info = st.selectbox("睡眠狀況", ["很好", "普通", "沒睡飽", "失眠"])

with st.expander("🏃 生活習慣紀錄"):
    water = st.number_input("飲水量 (ml)", value=2000, step=100)
    steps = st.number_input("今日步數", value=5000, step=500)

with st.expander("🍱 熱量計算器"):
    meat_g = st.number_input("肉類 (克)", value=0, step=10)
    veg_g = st.number_input("蔬菜 (克)", value=0, step=10)
    if st.button("➕ 加入今日總計"):
        # 簡單計算公式範例 (可依需求調整)
        added_kcal = (meat_g * 2.5) + (veg_g * 0.3)
        st.session_state.daily_total_kcal += added_kcal
        st.success(f"已加入 {added_kcal} kcal，今日總計: {st.session_state.daily_total_kcal} kcal")

st.divider()

# --- 4. 核心功能：一鍵同步到 Google Sheets ---
st.subheader(f"📊 今日總熱量：{st.session_state.daily_total_kcal} kcal")

# 整理要傳送的數據袋 (Payload)
payload = {
    "date": record_date.strftime('%Y-%m-%d'),  # 確保是乾淨日期字串
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

if st.button("🚀 數據直接入庫 (不跳轉)", use_container_width=True):
    try:
        # 使用 GET 請求傳送數據
        response = requests.get(script_url, params=payload, timeout=10)
        
        if response.status_code == 200:
            st.success(f"成功同步！Google 回報：{response.text}")
            st.balloons()  # 噴發氣球慶祝成功
            # 成功後可視需求重置熱量
            # st.session_state.daily_total_kcal = 0 
        else:
            st.error(f"連線失敗，狀態碼：{response.status_code}")
    except Exception as e:
        st.error(f"連線發生錯誤：{e}")
