import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# --- 連線初始化 ---
def init_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        s = st.secrets["gcp_service_account"]
        
        # 徹底移除 Base64 可能含有的空白字元並解碼
        raw_key = base64.b64decode(s["private_key_base64"].strip()).decode("utf-8")
        
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": raw_key,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"],
            "universe_domain": s.get("universe_domain", "googleapis.com")
        }
        
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("MyDietLog").sheet1
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# --- 設定與 Session State ---
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "veggie": 25, "fruit": 60, "fat": 45}

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")
sheet_result = init_sheet()

# --- UI 顯示 ---
st.title("🚀 2710kcal 智慧紀錄")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())

# 側邊欄
st.sidebar.header("📊 雲端狀態")
if not isinstance(sheet_result, str):
    st.sidebar.success("✅ 雲端已同步")
    if st.sidebar.button("💾 存入 Google"):
        try:
            row = [datetime.now().strftime("%Y-%m-%d"), round(total_kcal)] + [st.session_state.daily[k] for k in GOALS.keys()] + [st.session_state.water]
            sheet_result.append_row(row)
            st.sidebar.balloons()
        except Exception as e:
            st.sidebar.error(f"存檔失敗: {e}")
else:
    st.sidebar.error(sheet_result)

# 份數卡片
st.divider()
cols = st.columns(4)
for i, key in enumerate(GOALS.keys()):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i % 4].metric(key.upper(), f"剩 {rem:.1f}", delta=f"{st.session_state.daily[key]:.1f}")

# 輸入 Tab
t1, t2 = st.tabs(["🥙 進食", "⚙️ 設定"])
with t1:
    c1, c2 = st.columns(2)
    cw = c1.number_input("澱粉重 (g)", 0.0, step=10.0, key="c_in")
    pw = c2.number_input("肉量 (g)", 0.0, step=5.0, key="p_in")
    if st.button("➕ 儲存"):
        st.session_state.daily["carbs"] += (cw/60)
        st.session_state.daily["protein_low"] += (pw/35)
        st.rerun()

with t2:
    if st.button("🔄 清空今天資料"):
        st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
        st.session_state.water = 0.0; st.rerun()
