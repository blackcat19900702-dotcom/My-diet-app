import streamlit as st

# --- 1. 核心配額與換算 ---
GOALS = {
    "carbs": 16.0, "protein_low": 7.0, "protein_mid": 3.5, 
    "veggie": 4.0, "veggie_green": 2.0, "fruit": 3.0, 
    "milk": 3.0, "fat": 5.5, "salt": 4.0,
    "target_kcal": 2710.0,
    "target_water": 3000.0  # 預設飲水目標 3000ml
}

KCAL_MAP = {
    "carbs": 70, "protein_low": 55, "protein_mid": 75,
    "veggie": 25, "fruit": 60, "milk": 150, "fat": 45
}

CONV = {"carbs_g": 60, "protein_g": 35, "veggie_g": 100, "fruit_g": 100, "milk_ml": 240}

MEAT_DATABASE = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", 
    "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", 
    "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"
}

VEGGIE_DATABASE = {
    "綠花椰": True, "菠菜": True, "地瓜葉": True, "空心菜": True,
    "櫛瓜": False, "茄子": False, "高麗菜": False, "白花椰": False, 
    "娃娃菜": False, "絲瓜": False, "洋蔥": False, "雪白菇": False, "鴻禧菇": False
}

# 初始化
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧導航", layout="wide")

# --- 2. 頂部狀態列：熱量燈號、深綠色、飲水量 ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP[k] for k in KCAL_MAP.keys() if k in KCAL_MAP)

st.title("⚖️ 2710kcal 智慧飲食與飲水監控")

c1, c2 = st.columns(2)

with c1:
    # A. 熱量紅綠燈
    if 2660 <= total_kcal <= 2710:
        st.success(f"🟢 綠燈：目前總熱量 {total_kcal:.0f} kcal (完美區間！)")
    elif total_kcal > 2710:
        st.error(f"🔴 紅燈：目前總熱量 {total_kcal:.0f} kcal (超標 {total_kcal - 2710:.0f} kcal)")
    else:
        st.warning(f"🟡 未達標：目前總熱量 {total_kcal:.0f} kcal (距綠燈還差 {2660 - total_kcal:.0f} kcal)")

with c2:
    # B. 飲水進度條
    water_pct = min(st.session_state.water / GOALS["target_water"], 1.0)
    st.info(f"💧 今日飲水：{st.session_state.water:.0f} / {GOALS['target_water']:.0f} ml")
    st.progress(water_pct)

# C. 深綠色蔬菜提醒
green_cur = st.session_state.daily["veggie_green"]
green_target = GOALS["veggie_green"]
if green_cur < green_target:
    st.write(f"🥦 **深綠色蔬菜**：還差 {green_target - green_cur:.1f} 份")
else:
    st.write("✅ **深綠色蔬菜已達標！**")

# --- 3. 儀表板：配額監控 ---
st.divider()
cols = st.columns(6)
items = [
    ("🍞 主食", "carbs"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"),
    ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]

for i, (label, key) in enumerate(items):
    current = st.session_state.daily[key]
    rem = GOALS[key] - current
    color = "normal" if rem >= 0 else "inverse"
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃", delta_color=color)

# --- 4. 紀錄輸入區 ---
t1, t2, t3, t4, t5 = st.tabs(["🍚 澱粉/奶類", "🥩 肉類", "🥬 蔬菜", "💧 飲水", "🧂 其他"])

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
    method = st.selectbox("烹調方式", ["水煮/清蒸", "乾煎/油炒", "油炸"])
    outside = st.checkbox("這餐是外食")
    if st.button("➕ 紀錄肉類"):
        fat_level = MEAT_DATABASE[m_part]
        servings = m_w / CONV["protein_g"]
        if fat_level == "low": st.session_state.daily["protein_low"] += servings
        else: st.session_state.daily["protein_mid"] += servings
        f_add = 1.0 if method == "乾煎/油炒" else (3.5 if method == "油炸" else 0.0)
        if outside: f_add += 1.5
        st.session_state.daily["fat"] += f_add
        st.rerun()

with t3:
    v_name = st.selectbox("選擇蔬菜名稱", list(VEGGIE_DATABASE.keys()))
    v_w = st.number_input("熟菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        servings = v_w / CONV["veggie_g"]
        st.session_state.daily["veggie"] += servings
        if VEGGIE_DATABASE[v_name]: st.session_state.daily["veggie_green"] += servings
        st.rerun()

with t4:
    st.subheader("💧 飲水紀錄")
    w_in = st.number_input("輸入水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("🥤 喝水入庫"):
        st.session_state.water += w_in
        st.rerun()
    st.caption("建議攝取量：每日體重 x 35-40ml")

with t5:
    f_w = st.number_input("水果重量 (g)", min_value=0.0)
    salt_g = st.number_input("台鹽鹽巴量 (g)", min_value=0.0)
    if st.button("➕ 紀錄水果與鹽"):
        st.session_state.daily["fruit"] += (f_w / CONV["fruit_g"])
        st.session_state.daily["salt"] += salt_g
        st.rerun()

st.divider()
if st.button("🔄 開啟新的一天", use_container_width=True):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.water = 0.0
    st.rerun()
