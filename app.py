import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. 初始化連線 ---
def init_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # 直接獲取 Secrets 內容，不做任何 string 操作
        info = dict(st.secrets["gcp_service_account"])
        
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        # 確保你的試算表名稱正確
        return client.open("MyDietLog").sheet1
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# --- 2. 參數設定 ---
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "veggie": 25, "fruit": 60, "fat": 45}

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")
sheet_result = init_sheet()

# --- 3. 主介面 ---
st.title("🚀 2710kcal 飲食智慧監控")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())

# 側邊欄：同步與狀態
st.sidebar.header("☁️ 雲端狀態")
if not isinstance(sheet_result, str):
    st.sidebar.success("✅ 雲端已同步")
    if st.sidebar.button("💾 存入 Google"):
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

# 顯示剩餘份數
st.divider()
st.subheader("📊 今日份數餘額")
cols = st.columns(4)
for i, key in enumerate(GOALS.keys()):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i % 4].metric(key.upper(), f"剩 {rem:.1f}", delta=f"已攝取 {st.session_state.daily[key]:.1f}")

# 輸入區
st.divider()
c1, c2 = st.columns(2)
cw = c1.number_input("澱粉重量 (g)", 0.0, step=10.0, key="in_c")
pw = c2.number_input("肉類重量 (g)", 0.0, step=5.0, key="in_p")

if st.button("➕ 儲存攝取紀錄", use_container_width=True):
    st.session_state.daily["carbs"] += (cw/60)
    st.session_state.daily["protein_low"] += (pw/35)
    st.rerun()

if st.button("🔄 清空當前紀錄 (重新開始)", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
