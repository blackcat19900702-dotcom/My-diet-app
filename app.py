import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. 雲端後台連線設定 ---
def init_sheet():
    try:
        # 設定 Google API 存取範圍
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # 讀取本地金鑰檔案
        creds = Credentials.from_service_account_file("creds.json", scopes=scope)
        client = gspread.authorize(creds)
        # 開啟指定的試算表（請確保名稱一致）
        return client.open("MyDietLog").sheet1
    except Exception as e:
        return None

# 初始化試算表連線
sheet = init_sheet()

# --- 2. 營養參數與資料庫 ---
GOALS = {
    "carbs": 16.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "veggie_green": 2.0, "fruit": 3.0, 
    "milk": 3.0, "fat": 5.5, "salt": 4.0, 
    "target_kcal": 2710.0, "target_water": 3000.0
}

KCAL_MAP = {
    "carbs": 70, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "milk": 150, "fat": 45
}

# 熟重換算基準 (g/ml = 1份)
CONV = {"carbs_g": 60, "protein_g": 35, "veggie_g": 100, "fruit_g": 100, "milk_ml": 240}

# 肉類自動辨識資料庫
MEAT_DB = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", 
    "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", 
    "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"
}

# 蔬菜自動辨識資料庫 (True = 深綠色)
VEG_DB = {
    "綠花椰": True, "菠菜": True, "地瓜葉": True, "空心菜": True,
    "櫛瓜": False, "茄子": False, "高麗菜": False, "白花椰": False, 
    "娃娃菜": False, "絲瓜": False, "洋蔥": False, "雪白菇": False, "鴻禧菇": False
}

# 初始化 Session State
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧監控中心", layout="wide")

# --- 3. 頂部狀態列：熱量與飲水 ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP[k] for k in KCAL_MAP.keys() if k in KCAL_MAP)

st.title("⚖️ 2710kcal 智慧雲端監控系統")

# A. 熱量紅綠燈
status_col, water_col = st.columns(2)
with status_col:
    if 2660 <= total_kcal <= 2710:
        st.success(f"🟢 綠燈：目前 {total_kcal:.0f} kcal (完美區間)")
    elif total_kcal > 2710:
        st.error(f"🔴 紅燈：目前 {total_kcal:.0f} kcal (超標 {total_kcal - 2710:.0f} kcal)")
    else:
        st.warning(f"🟡 未達標：目前 {total_kcal:.0f} kcal (還差 {2660 - total_kcal:.0f} kcal)")

# B. 飲水進度
with water_col:
    w_pct = min(st.session_state.water / GOALS["target_water"], 1.0)
    st.info(f"💧 今日飲水：{st.session_state.water:.0f} / {GOALS['target_water']:.0f} ml")
    st.progress(w_pct)

# C. 深綠色蔬菜提醒
green_cur = st.session_state.daily["veggie_green"]
if green_cur < GOALS["veggie_green"]:
    st.write(f"🥦 **深綠色蔬菜**：還差 {GOALS['veggie_green'] - green_cur:.1f} 份 (約 {(GOALS['veggie_green'] - green_cur)*100:.0f}g)")
else:
    st.write("✅ **今日深綠色蔬菜已達標！**")

# --- 4. 側邊欄：雲端同步 ---
st.sidebar.header("☁️ 雲端同步中心")
if sheet:
    st.sidebar.success("✅ 雲端已連線")
    if st.sidebar.button("🚀 結算並同步至 Google"):
        try:
            status_text = "✅ 達標" if 2660 <= total_kcal <= 2710 else "🔴 未達標"
            now_date = datetime.now().strftime("%Y-%m-%d")
            # 依照 Google Sheets 欄位順序打包：日期, 熱量, 狀態, 澱粉, 低肉, 中肉, 蔬菜, 水果, 飲水, 鹽
            row = [
                now_date, round(total_kcal), status_text, 
                round(st.session_state.daily['carbs'], 1),
                round(st.session_state.daily['protein_low'], 1),
                round(st.session_state.daily['protein_mid'], 1),
                round(st.session_state.daily['veggie'], 1),
                round(st.session_state.daily['fruit'], 1),
                round(st.session_state.water),
                round(st.session_state.daily['salt'], 1)
            ]
            sheet.append_row(row)
            st.sidebar.balloons()
            st.sidebar.success("同步成功！")
        except Exception as e:
            st.sidebar.error(f"同步失敗：{e}")
else:
    st.sidebar.error("❌ 雲端連線失敗，請檢查 creds.json")

# --- 5. 核心儀表板 ---
st.divider()
cols = st.columns(6)
display_items = [
    ("🍞 主食", "carbs"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"),
    ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]
for i, (label, key) in enumerate(display_items):
    rem = GOALS[key] - st.session_state.daily[key]
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{st.session_state.daily[key]:.1f} 已吃", delta_color="normal" if rem >= 0 else "inverse")

# --- 6. 紀錄輸入區 ---
t1, t2, t3, t4, t5 = st.tabs(["🍚 澱粉/奶", "🥩 肉類", "🥬 蔬菜", "💧 飲水", "🍎 其他"])

with t1:
    c_w = st.number_input("熟主食重量 (g)", min_value=0.0, step=10.0, key="carbs_in")
    m_ml = st.number_input("奶類/優酪乳 (ml)", min_value=0.0, step=100.0, key="milk_in")
    if st.button("➕ 儲存澱粉/奶"):
        st.session_state.daily["carbs"] += (c_w / CONV["carbs_g"])
        st.session_state.daily["milk"] += (m_ml / CONV["milk_ml"])
        st.rerun()

with t2:
    m_name = st.selectbox("選擇肉類", list(MEAT_DB.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0, key="meat_in")
    method = st.selectbox("烹調", ["水煮/蒸", "油炒/煎", "炸"])
    is_out = st.checkbox("這餐外食")
    if st.button("➕ 儲存肉類"):
        servings = m_w / CONV["protein_g"]
        if MEAT_DB[m_name] == "low": st.session_state.daily["protein_low"] += servings
        else: st.session_state.daily["protein_mid"] += servings
        f_add = 1.0 if method == "油炒/煎" else (3.5 if method == "炸" else 0.0)
        if is_out: f_add += 1.5
        st.session_state.daily["fat"] += f_add
        st.rerun()

with t3:
    v_name = st.selectbox("蔬菜名稱", list(VEG_DB.keys()))
    v_w = st.number_input("熟菜重量 (g)", min_value=0.0, step=50.0, key="veg_in")
    if st.button("➕ 儲存蔬菜"):
        v_servings = v_w / CONV["veggie_g"]
        st.session_state.daily["veggie"] += v_servings
        if VEG_DB[v_name]: st.session_state.daily["veggie_green"] += v_servings
        st.rerun()

with t4:
    w_in = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("🥤 喝水紀錄"):
        st.session_state.water += w_in
        st.rerun()

with t5:
    f_w = st.number_input("水果重量 (g)", min_value=0.0, key="fruit_in")
    s_g = st.number_input("鹽巴量 (g)", min_value=0.0, key="salt_in")
    if st.button("➕ 儲存水果與鹽"):
        st.session_state.daily["fruit"] += (f_w / CONV["fruit_g"])
        st.session_state.daily["salt"] += s_g
        st.rerun()

if st.button("🔄 開啟新的一天", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
