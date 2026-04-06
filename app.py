import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def init_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        s = st.secrets["gcp_service_account"]
        
        # 關鍵修正：將單行字串中的 \n 符號還原為真正的換行符
        fixed_key = s["private_key"].replace("\\n", "\n")
        
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": fixed_key,
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

# 下方的 UI 代碼保持不變...
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")
sheet_result = init_sheet()

st.title("🚀 2710kcal 智慧紀錄")

if not isinstance(sheet_result, str):
    st.sidebar.success("✅ 雲端已同步")
    if st.sidebar.button("💾 存入 Google"):
        try:
            row = [datetime.now().strftime("%Y-%m-%d")] + [st.session_state.daily[k] for k in GOALS.keys()]
            sheet_result.append_row(row)
            st.sidebar.balloons()
        except Exception as e:
            st.sidebar.error(f"寫入失敗: {e}")
else:
    st.sidebar.error(sheet_result)

cols = st.columns(4)
for i, key in enumerate(GOALS.keys()):
    cols[i % 4].metric(key.upper(), f"{st.session_state.daily[key]:.1f}")

cw = st.number_input("澱粉量 (g)", 0.0, step=10.0)
if st.button("➕ 儲存"):
    st.session_state.daily["carbs"] += (cw/60)
    st.rerun()
