import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# --- 1. 雲端連線核心 (Base64 穩定版) ---
def init_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # 讀取 Secrets
        s = st.secrets["gcp_service_account"]
        
        # 構建憑證字典
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        # 從 Base64 还原最原始的 Private Key
        info["private_key"] = base64.b64decode(s["private_key_base64"]).decode("utf-8")
        
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("MyDietLog").sheet1
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# --- 2. 營養參數與初始化 ---
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

# --- 3. 畫面顯示 ---
st.title("🚀 2710kcal 智慧監控")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP[k] for k in KCAL_MAP.keys() if k in KCAL_MAP)

# 側邊欄：同步狀態
st.sidebar.header("☁️ 雲端同步")
if not isinstance(sheet_result, str):
    st.sidebar.success("✅ 雲端已連線")
    if st.sidebar.button("💾 結算並存入 Google"):
        try:
            row = [
                datetime.now().strftime("%Y-%m-%d"), round(total_kcal),
                "✅ 達標" if 2660 <= total_kcal <= 2710 else "🔴 未達標",
                *[round(st.session_state.daily[k], 1) for k in GOALS.keys()],
                round(st.session_state.water)
            ]
            sheet_result.append_row(row)
            st.sidebar.balloons()
            st.sidebar.success("數據已存入 Google 試算表！")
        except Exception as e:
            st.sidebar.error(f"寫入失敗: {e}")
else:
    st.sidebar.error(sheet_result)

# 儀表板
c1, c2 = st.columns(2)
with c1:
    st.metric("總熱量", f"{total_kcal:.0f} / 2710 kcal")
with c2:
    st.metric("飲水", f"{st.session_state.water:.0f} / 3000 ml")

# 份數監控
st.divider()
m_cols = st.columns(4)
for i, (label, key) in enumerate(GOALS.items()):
    rem = GOALS[key] - st.session_state.daily[key]
    m_cols[i % 4].metric(label, f"剩 {rem:.1f}", delta=f"{st.session_state.daily[key]:.1f}")

# --- 4. 輸入區域 ---
tabs = st.tabs(["🍚 澱粉/奶類", "🥩 肉類/蔬果", "🥤 飲水"])
with tabs[0]:
    cw = st.number_input("澱粉重量 (g)", min_value=0.0, step=10.0)
    if st.button("➕ 儲存澱粉"):
        st.session_state.daily["carbs"] += (cw / 60); st.rerun()
with tabs[1]:
    mw = st.number_input("肉類重量 (g)", min_value=0.0, step=5.0)
    if st.button("➕ 儲存肉類"):
        st.session_state.daily["protein_low"] += (mw / 35); st.rerun()
with tabs[2]:
    win = st.number_input("飲水 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("🥤 喝水"):
        st.session_state.water += win; st.rerun()

if st.button("🔄 開啟新的一天", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0; st.rerun()
