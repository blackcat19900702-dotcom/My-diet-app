import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import re

# --- 1. 強大連線初始化 (自動修復所有格式問題) ---
def init_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        s = st.secrets["gcp_service_account"]
        
        # 取得原始 Key
        raw_key = s["private_key"]
        
        # 【自動修復邏輯】: 
        # 1. 處理被誤轉義的斜線 \\n -> \n
        # 2. 處理多餘的空格
        # 3. 確保 BEGIN/END 標籤完整
        processed_key = raw_key.replace("\\n", "\n").strip()
        if "-----BEGIN PRIVATE KEY-----" not in processed_key:
            processed_key = "-----BEGIN PRIVATE KEY-----\n" + processed_key + "\n-----END PRIVATE KEY-----"

        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": processed_key,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("MyDietLog").sheet1
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# --- 2. 營養參數與 Session State ---
GOALS = {
    "carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0
}
KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "fat": 45
}

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")
sheet_result = init_sheet()

# --- 3. UI 介面 ---
st.title("🚀 2710kcal 飲食紀錄系統")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())

# 側邊欄狀態
if not isinstance(sheet_result, str):
    st.sidebar.success("✅ 雲端同步中")
    if st.sidebar.button("💾 存入 Google 試算表"):
        try:
            row = [datetime.now().strftime("%Y-%m-%d"), round(total_kcal)] + \
                  [round(st.session_state.daily[k], 1) for k in GOALS.keys()] + \
                  [round(st.session_state.water)]
            sheet_result.append_row(row)
            st.sidebar.balloons()
        except Exception as e:
            st.sidebar.error(f"寫入失敗: {e}")
else:
    st.sidebar.error(sheet_result)

# 份數餘額
st.divider()
st.subheader(f"🔥 目前總熱量: {total_kcal:.0f} / 2710 kcal")
cols = st.columns(4)
for i, key in enumerate(GOALS.keys()):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i % 4].metric(key.upper(), f"剩 {rem:.1f}", delta=f"攝取 {st.session_state.daily[key]:.1f}")

# 輸入紀錄
st.divider()
c1, c2, c3 = st.columns(3)
cw = c1.number_input("熟澱粉重 (g)", 0.0, step=10.0, key="in_carbs")
pw = c2.number_input("肉重量 (g)", 0.0, step=5.0, key="in_protein")
ww = c3.number_input("飲水量 (ml)", 0.0, step=50.0, value=250.0, key="in_water")

if st.button("➕ 儲存紀錄", use_container_width=True):
    st.session_state.daily["carbs"] += (cw/60)
    st.session_state.daily["protein_low"] += (pw/35)
    st.session_state.water += ww
    st.rerun()

if st.button("🔄 重置今日", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
