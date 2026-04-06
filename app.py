import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
WATER_GOAL = 3000.0

GOALS = {
    "carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0
}

KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "fat": 45, "salt": 0
}

# --- 2. 主食詳細資料庫 ---
# 定義每一份 (1 exchange) 對應的熟重
CARBS_DATABASE = {
    "白米飯 (60g/份)": 60,
    "白米混合五穀米 (60g/份)": 60,
    "煮過白麵條 (75g/份)": 75,
    "自蒸地瓜 (55g/份)": 55,       # 水份保留
    "超商烤地瓜 (50g/份)": 50,     # 脫水濃縮
    "手動輸入份量比例": 1.0
}

MEAT_DATABASE = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", 
    "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", 
    "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"
}

GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧飲食導航", layout="wide")

# --- 3. 儀表板 ---
st.title("⚖️ 2710kcal 智慧飲食監控")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())
is_perfect = (BASE_KCAL - 50) <= total_kcal <= BASE_KCAL

st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

if is_perfect:
    st.success("🟢 綠燈：熱量控制精準")
else:
    st.error("🔴 紅燈：熱量偏差中")

cols = st.columns(7)
items = [
    ("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), 
    ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]

for i, (label, key) in enumerate(items):
    current = st.session_state.daily[key]
    rem = GOALS[key] - current
    cols[i].metric(label, f"剩 {rem:.1f}", delta=f"{current:.1f} 已吃")

# 狀態資訊
c1, c2 = st.columns(2)
with c1:
    water_rem = WATER_GOAL - st.session_state.water
    st.info(f"💧 飲水：已喝 {int(st.session_state.water)}ml / 剩 {max(0, int(water_rem))}ml")
with c2:
    st.info(f"🍃 深綠色蔬菜：已攝取 {st.session_state.veggie_green:.1f} 份")

# --- 4. 紀錄區 ---
st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

with tabs[0]: # 主食
    carb_type = st.selectbox("選擇主食種類", list(CARBS_DATABASE.keys()))
    if carb_type == "手動輸入份量比例":
        custom_unit = st.number_input("手動：一份是多少克？", min_value=1.0, value=60.0)
    else:
        custom_unit = CARBS_DATABASE[carb_type]
        
    c_w = st.number_input("本次攝取重量 (g)", min_value=0.0, step=1.0, key="carbs_input_val")
    carb_outside = st.checkbox("外食主食 (自動補 1.5 油脂)", key="carb_outside_flag")
    
    if st.button("➕ 紀錄主食", key="btn_rec_carbs"):
        servings = c_w / custom_unit
        st.session_state.daily["carbs"] += servings
        if carb_outside:
            st.session_state.daily["fat"] += 1.5
        st.rerun()

with tabs[1]: # 奶類
    m_ml = st.number_input("奶類/優酪乳 (ml)", min_value=0.0, step=100.0)
    if st.button("➕ 紀錄奶類"):
        st.session_state.daily["milk"] += (m_ml / 240)
        st.rerun()

with tabs[2]: # 肉類
    m_part = st.selectbox("選擇肉類部位", list(MEAT_DATABASE.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    method = st.selectbox("烹調方式", ["水煮/清蒸", "氣炸鍋", "乾煎/油炒", "油炸"])
    meat_outside = st.checkbox("外食肉類 (自動補 1.5 油脂)", key="meat_outside_flag")
    if st.button("➕ 紀錄肉類"):
        fat_level = MEAT_DATABASE[m_part]
        servings = m_w / 35
        if fat_level == "low": st.session_state.daily["protein_low"] += servings
        else: st.session_state.daily["protein_mid"] += servings
        f_add = 0.5 if method == "氣炸鍋" else (1.0 if method == "乾煎/油炒" else (3.5 if method == "油炸" else 0.0))
        if meat_outside: f_add += 1.5
        st.session_state.daily["fat"] += f_add
        st.rerun()

with tabs[3]: # 蔬菜
    v_name = st.selectbox("種類", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("熟菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        servings = v_w / 100
        st.session_state.daily["veggie"] += servings
        if v_name in GREEN_LIST:
            st.session_state.veggie_green += servings
        st.rerun()

with tabs[4]: # 其他
    col_f, col_fr, col_s = st.columns(3)
    with col_f:
        f_add_manual = st.number_input("額外油脂 (份)", min_value=0.0, step=0.5)
        if st.button("➕ 紀錄油脂"):
            st.session_state.daily["fat"] += f_add_manual
            st.rerun()
    with col_fr:
        fr_w = st.number_input("水果重量 (g)", min_value=0.0, step=10.0)
        if st.button("➕ 紀錄水果"):
            st.session_state.daily["fruit"] += (fr_w / 100)
            st.rerun()
    with col_s:
        s_g = st.number_input("台鹽鹽巴 (g)", min_value=0.0, step=0.5)
        if st.button("➕ 紀錄鹽分"):
            st.session_state.daily["salt"] += s_g
            st.rerun()

with tabs[5]: # 飲水
    w_input = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("➕ 紀錄飲水"):
        st.session_state.water += w_input
        st.rerun()

# --- 5. Excel 結算 ---
st.divider()
status_str = "綠燈" if is_perfect else "紅燈"
excel_row = "\t".join([
    datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), status_str,
    f"{round(st.session_state.daily['carbs'], 1)}", f"{round(st.session_state.daily['milk'], 1)}",
    f"{round(st.session_state.daily['protein_low'], 1)}", f"{round(st.session_state.daily['protein_mid'], 1)}",
    f"{round(st.session_state.daily['veggie'], 1)}", f"{round(st.session_state.veggie_green, 1)}", 
    f"{round(st.session_state.daily['fruit'], 1)}", f"{round(st.session_state.daily['fat'], 1)}", 
    f"{round(st.session_state.daily['salt'], 1)}", str(round(st.session_state.water))
])
st.subheader("📋 Excel 結算行 (直接複製貼上)")
st.code(excel_row, language="text")

if st.button("🔄 開啟新的一天", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.veggie_green = 0.0
    st.session_state.water = 0.0
    st.rerun()
