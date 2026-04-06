import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. 雲端連線核心 (完全適應原始 PEM 格式) ---
def init_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # 讀取 Secrets
        s = st.secrets["gcp_service_account"]
        
        # 建立 Credentials 字典
        # 不做 replace，不做 base64，直接把原始字串餵給 Google 庫
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": s["private_key"],
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        
        # 這裡請確保你的 Google Sheet 名字真的是 "MyDietLog"
        # 如果失敗，請檢查試算表是否有分享編輯權限給 client_email
        return client.open("MyDietLog").sheet1
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# --- 2. 營養參數設定 ---
GOALS = {
    "carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0
}
KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "fat": 45
}

# 初始化資料
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")
sheet_result = init_sheet()

# --- 3. UI 顯示邏輯 ---
st.title("🚀 2710kcal 飲食智慧監控")

# 總熱量計算
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())

# 側邊欄同步狀態
st.sidebar.header("☁️ 雲端狀態")
if not isinstance(sheet_result, str):
    st.sidebar.success("✅ 雲端已同步")
    if st.sidebar.button("💾 結算並存入 Google"):
        try:
            row = [
                datetime.now().strftime("%Y-%m-%d"), 
                round(total_kcal),
                "✅ 達標" if 2660 <= total_kcal <= 2710 else "🔴 未達標"
            ] + [round(st.session_state.daily[k], 1) for k in GOALS.keys()] + [round(st.session_state.water)]
            
            sheet_result.append_row(row)
            st.sidebar.balloons()
            st.sidebar.success("數據已成功寫入試算表！")
        except Exception as e:
            st.sidebar.error(f"寫入失敗: {e}")
else:
    st.sidebar.error(sheet_result)

# 顯示剩餘份數卡片
st.divider()
st.subheader(f"🔥 今日熱量: {total_kcal:.0f} / 2710 kcal")
m_cols = st.columns(4)
for i, key in enumerate(GOALS.keys()):
    rem = GOALS[key] - st.session_state.daily[key]
    m_cols[i % 4].metric(
        key.upper(), 
        f"剩 {rem:.1f}", 
        delta=f"已攝取 {st.session_state.daily[key]:.1f}",
        delta_color="inverse"
    )

# --- 4. 輸入區域 ---
st.divider()
tabs = st.tabs(["📝 進食紀錄", "🥤 飲水與重置"])

with tabs[0]:
    c1, c2 = st.columns(2)
    cw = c1.number_input("澱粉類重量 (g)", min_value=0.0, step=10.0, key="in_c")
    pw = c2.number_input("蛋白質/肉類重量 (g)", min_value=0.0, step=5.0, key="in_p")
    if st.button("➕ 儲存攝取量", use_container_width=True):
        st.session_state.daily["carbs"] += (cw / 60)
        st.session_state.daily["protein_low"] += (pw / 35)
        st.rerun()

with tabs[1]:
    win = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("🥤 喝水紀錄", use_container_width=True):
        st.session_state.water += win
        st.rerun()
        
    st.divider()
    if st.button("🔄 清空今天所有紀錄", use_container_width=True):
        st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
        st.session_state.water = 0.0
        st.rerun()
