import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# --- 1. 雲端後台連線設定 (增加防崩潰邏輯) ---
def init_sheet():
    # 檢查金鑰檔案是否存在，不存在就不連線，避免程式崩潰
    if not os.path.exists("creds.json"):
        return None
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("creds.json", scopes=scope)
        client = gspread.authorize(creds)
        # 請確保 Google 試算表名稱真的是 MyDietLog
        return client.open("MyDietLog").sheet1
    except Exception as e:
        # 如果連線失敗（如權限問題），回傳錯誤訊息給介面
        return str(e)

# 嘗試初始化
sheet_result = init_sheet()

# --- 2. 營養參數與資料庫 (維持不變) ---
GOALS = {
    "carbs": 16.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "veggie_green": 2.0, "fruit": 3.0, 
    "milk": 3.0, "fat": 5.5, "salt": 4.0, 
    "target_kcal": 2710.0, "target_water": 3000.0
}
KCAL_MAP = {"carbs": 70, "protein_low": 55, "protein_mid": 75, "veggie": 25, "fruit": 60, "milk": 150, "fat": 45}
CONV = {"carbs_g": 60, "protein_g": 35, "veggie_g": 100, "fruit_g": 100, "milk_ml": 240}

MEAT_DB = {"雞胸肉": "low", "雞腿肉(去皮)": "low", "牛腱": "low", "里肌肉(豬)": "low", "豆腐": "low", "雞蛋": "mid", "鮭魚": "mid", "梅花豬": "mid", "雞腿肉(帶皮)": "mid"}
VEG_DB = {"綠花椰": True, "菠菜": True, "地瓜葉": True, "空心菜": True, "高麗菜": False, "白花椰": False, "絲瓜": False, "雪白菇": False}

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")

# --- 3. 介面顯示 ---
st.title("⚖️ 2710kcal 智慧雲端監控系統")

# 側邊欄：同步功能與錯誤顯示
st.sidebar.header("☁️ 雲端同步中心")

if sheet_result is None:
    st.sidebar.warning("⚠️ 找不到 creds.json，目前為「離線模式」。")
    sheet = None
elif isinstance(sheet_result, str):
    st.sidebar.error(f"❌ 連線錯誤: {sheet_result}")
    sheet = None
else:
    st.sidebar.success("✅ 雲端已連線")
    sheet = sheet_result

# 同步按鈕邏輯
if st.sidebar.button("🚀 結算並同步至 Google"):
    if sheet:
        try:
            total_kcal = sum(st.session_state.daily[k] * KCAL_MAP[k] for k in KCAL_MAP.keys() if k in KCAL_MAP)
            status_text = "✅ 達標" if 2660 <= total_kcal <= 2710 else "🔴 未達標"
            row = [
                datetime.now().strftime("%Y-%m-%d"), round(total_kcal), status_text,
                round(st.session_state.daily['carbs'], 1), round(st.session_state.daily['protein_low'], 1),
                round(st.session_state.daily['protein_mid'], 1), round(st.session_state.daily['veggie'], 1),
                round(st.session_state.daily['fruit'], 1), round(st.session_state.water), round(st.session_state.daily['salt'], 1)
            ]
            sheet.append_row(row)
            st.sidebar.balloons()
        except Exception as e:
            st.sidebar.error(f"上傳失敗：{e}")
    else:
        st.sidebar.error("目前處於離線模式，無法上傳。")

# --- 4. 核心功能 (儀表板與輸入分頁) ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP[k] for k in KCAL_MAP.keys() if k in KCAL_MAP)
c1, c2 = st.columns(2)
with c1:
    if 2660 <= total_kcal <= 2710: st.success(f"🟢 綠燈：{total_kcal:.0f} kcal")
    elif total_kcal > 2710: st.error(f"🔴 紅燈：{total_kcal:.0f} kcal")
    else: st.warning(f"🟡 未達標：{total_kcal:.0f} kcal")
with c2:
    st.info(f"💧 飲水：{st.session_state.water:.0f} / 3000 ml")
    st.progress(min(st.session_state.water / 3000, 1.0))

st.divider()
cols = st.columns(6)
items = [("🍞 主食", "carbs"), ("🥩 低肉", "protein_low"), ("🍖 中肉", "protein_mid"), ("🥦 蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(items):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i].metric(label, f"剩 {rem:.1f}", delta=f"{st.session_state.daily[key]:.1f}")

# 分頁輸入 (簡化版邏輯)
t1, t2, t3, t4, t5 = st.tabs(["🍚 澱粉/奶", "🥩 肉類", "🥬 蔬菜", "💧 飲水", "🍎 其他"])
with t1:
    cw = st.number_input("熟主食(g)", 0.0, step=10.0)
    if st.button("➕ 存澱粉"): 
        st.session_state.daily["carbs"] += cw/60
        st.rerun()
with t2:
    m_name = st.selectbox("肉類", list(MEAT_DB.keys()))
    mw = st.number_input("熟肉(g)", 0.0, step=5.0)
    if st.button("➕ 存肉類"):
        serv = mw/35
        if MEAT_DB[m_name] == "low": st.session_state.daily["protein_low"] += serv
        else: st.session_state.daily["protein_mid"] += serv
        st.rerun()
with t3:
    vw = st.number_input("熟菜(g)", 0.0, step=50.0)
    if st.button("➕ 存蔬菜"):
        st.session_state.daily["veggie"] += vw/100
        st.rerun()
with t4:
    win = st.number_input("水量(ml)", 0.0, step=50.0, value=250.0)
    if st.button("🥤 紀錄喝水"):
        st.session_state.water += win
        st.rerun()
with t5:
    fw = st.number_input("水果(g)", 0.0)
    if st.button("➕ 存水果"):
        st.session_state.daily["fruit"] += fw/100
        st.rerun()

if st.button("🔄 清空重置", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
