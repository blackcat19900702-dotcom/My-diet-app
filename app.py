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

CONV = {"carbs_g": 60, "protein_g": 35, "veggie_g": 100, "fruit_g": 100, "milk_ml": 240}

MEAT_DATABASE = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", 
    "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", 
    "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"
}

GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧導航", layout="wide")

# --- 2. 儀表板與紅綠燈 ---
st.title("⚖️ 2710kcal 智慧飲食監控")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())
is_perfect = (BASE_KCAL - 50) <= total_kcal <= BASE_KCAL

st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

if is_perfect:
    st.success("🟢 綠燈：達標")
else:
    st.error("🔴 紅燈：偏差過大")

cols = st.columns(7)
items = [
    ("🍞 主食", "carbs"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"),
    ("🥦 蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]

for i, (label, key) in enumerate(items):
    current = st.session_state.daily[key]
    rem = GOALS[key] - current
    cols[i].metric(label, f"剩 {rem:.1f}", delta=f"{current:.1f} 已吃")

water_rem = WATER_GOAL - st.session_state.water
cols[6].metric("💧 飲水", f"剩 {max(0, int(water_rem))}ml", delta=f"{int(st.session_state.water)}ml")

# --- 3. 紀錄區 ---
st.divider()
t1, t2, t3, t4 = st.tabs(["🍚 澱粉/奶類", "🥩 肉類(自動判別)", "🥬 蔬菜", "🥤 飲水/油脂/其他"])

with t1:
    c_w = st.number_input("熟主食重量 (g)", min_value=0.0, step=10.0)
    m_ml = st.number_input("奶類/優酪乳 (ml)", min_value=0.0, step=100.0)
    if st.button("➕ 紀錄澱粉與奶"):
        st.session_state.daily["carbs"] += (c_w / CONV["carbs_g"])
        st.session_state.daily["milk"] += (m_ml / CONV["milk_ml"])
        st.rerun()

with t2:
    m_part = st.selectbox("選擇肉類部位", list(MEAT_DATABASE.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    method = st.selectbox("烹調方式", ["水煮/清蒸", "氣炸鍋", "乾煎/油炒", "油炸"])
    outside = st.checkbox("這餐是外食")
    if st.button("➕ 紀錄肉類"):
        fat_level = MEAT_DATABASE[m_part]
        servings = m_w / CONV["protein_g"]
        if fat_level == "low": st.session_state.daily["protein_low"] += servings
        else: st.session_state.daily["protein_mid"] += servings
        
        f_add = 0.5 if method == "氣炸鍋" else (1.0 if method == "乾煎/油炒" else (3.5 if method == "油炸" else 0.0))
        if outside: f_add += 1.5
        st.session_state.daily["fat"] += f_add
        st.rerun()

with t3:
    v_w = st.number_input("熟菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        st.session_state.daily["veggie"] += (v_w / CONV["veggie_g"])
        st.rerun()

with t4:
    # 這裡補上油脂輸入與飲水
    f_add_manual = st.number_input("手動新增油脂 (份)", min_value=0.0, step=0.5, help="堅果或額外添加的油")
    f_w = st.number_input("水果重量 (g)", min_value=0.0)
    salt_g = st.number_input("台鹽鹽巴量 (g)", min_value=0.0)
    w_ml = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    
    if st.button("➕ 紀錄其餘項目"):
        st.session_state.daily["fat"] += f_add_manual
        st.session_state.daily["fruit"] += (f_w / CONV["fruit_g"])
        st.session_state.daily["salt"] += salt_g
        st.session_state.water += w_ml
        st.rerun()

# --- 4. Excel 結算 ---
st.divider()
status_str = "綠燈" if is_perfect else "紅燈"
excel_data = [
    datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), status_str,
    f"{round(st.session_state.daily['carbs'], 1)}", f"{round(st.session_state.daily['milk'], 1)}",
    f"{round(st.session_state.daily['protein_low'], 1)}", f"{round(st.session_state.daily['protein_mid'], 1)}",
    f"{round(st.session_state.daily['veggie'], 1)}", f"{round(st.session_state.daily['fruit'], 1)}",
    f"{round(st.session_state.daily['fat'], 1)}", f"{round(st.session_state.daily['salt'], 1)}",
    str(round(st.session_state.water))
]
st.code("\t".join(excel_data), language="text")

if st.button("🔄 開啟新的一天", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
