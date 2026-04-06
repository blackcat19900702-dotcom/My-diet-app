import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
GOALS = {
    "carbs": 16.0, 
    "milk": 3.0, 
    "protein_low": 7.0, 
    "protein_mid": 3.5, 
    "veggie": 4.0, 
    "fruit": 3.0, 
    "fat": 5.5, 
    "salt": 4.0
}

# 每份熱量基準
KCAL_MAP = {
    "carbs": 70, 
    "milk": 150, 
    "protein_low": 55, 
    "protein_mid": 75, 
    "protein_high": 120, 
    "veggie": 25, 
    "fruit": 60, 
    "fat": 45, 
    "salt": 0
}

# --- 2. 基礎資料庫 ---
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60,
    "五穀米/混合米 (60g/份)": 60,
    "煮過白麵條 (75g/份)": 75,
    "Tommi 炭香燒肉米漢堡 (固定數據)": "TOMMI_BBQ",
    "Tommi 壽喜燒肉米漢堡 (固定數據)": "TOMMI_SUKI",
    "米漢堡 (手動輸入包裝營養標示)": "BURGER",
    "自定義主食 (手動輸入名稱與重量)": "CUSTOM"
}

CUSTOM_CARB_DB = {
    "地瓜": 120, "烤地瓜": 150, "馬鈴薯": 80, "吐司": 280, "燕麥": 380, "玉米": 110
}

MEAT_DB = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "牛腱": "low", "里肌肉(豬)": "low", "豆腐": "low",
    "鱈魚": "low", "雞蛋": "mid", "鮭魚": "mid", "梅花豬": "mid", "梅花牛": "mid", 
    "雞腿肉(帶皮)": "mid", "豬絞肉": "mid", "牛肋條": "high", "肋眼牛排": "high", "豬五花": "high"
}

GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

# --- 3. 初始化 Session State ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

# --- 4. 網頁配置與儀表板 ---
st.set_page_config(page_title="2710kcal 專業飲食監控系統", layout="wide")

total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in KCAL_MAP.keys())

st.title("⚖️ 2710kcal 智慧飲食監控")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

cols = st.columns(7)
display_items = [
    ("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), 
    ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")
]

for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    goal = GOALS.get(key, 0)
    rem = goal - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

# --- 5. 紀錄輸入區 ---
st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

# --- Tab 0: 主食紀錄 (含 Tommi 分析邏輯) ---
with tabs[0]:
    st.write("### 🍞 主食輸入")
    carb_selection = st.selectbox("請選擇主食種類", list(FIXED_CARBS_REF.keys()), key="carb_sel")
    
    to_add = {k: 0.0 for k in KCAL_MAP.keys()}

    if carb_selection == "Tommi 炭香燒肉米漢堡 (固定數據)":
        st.info("📊 Tommi 炭香燒肉 (160g): 碳水 3.2份 / 中脂肉 1.3份 / 油脂 1.8份")
        num = st.number_input("數量 (個)", min_value=1, step=1, value=1)
        to_add["carbs"] = 3.2 * num
        to_add["protein_mid"] = 1.3 * num
        to_add["fat"] = 1.8 * num

    elif carb_selection == "Tommi 壽喜燒肉米漢堡 (固定數據)":
        st.info("📊 Tommi 壽喜燒肉 (160g): 碳水 3.3份 / 中脂肉 1.5份 / 油脂 1.0份")
        num = st.number_input("數量 (個)", min_value=1, step=1, value=1)
        to_add["carbs"] = 3.3 * num
        to_add["protein_mid"] = 1.5 * num
        to_add["fat"] = 1.0 * num

    elif FIXED_CARBS_REF[carb_selection] == "BURGER":
        st.warning("請輸入包裝標示數值：")
        col1, col2, col3 = st.columns(3)
        with col1: b_carbs = st.number_input("碳水 (g)", min_value=0.0, step=0.1)
        with col2: b_prot = st.number_input("蛋白 (g)", min_value=0.0, step=0.1)
        with col3: b_fat = st.number_input("脂肪 (g)", min_value=0.0, step=0.1)
        to_add["carbs"] = b_carbs / 15
        to_add["protein_mid"] = b_prot / 7
        to_add["fat"] = b_fat / 5

    elif FIXED_CARBS_REF[carb_selection] == "CUSTOM":
        c_name = st.text_input("主食名稱", key="c_custom_n")
        c_weight = st.number_input("重量 (g)", min_value=0.0, step=1.0)
        kcal_density = 140
        for key in CUSTOM_CARB_DB:
            if key in c_name: kcal_density = CUSTOM_CARB_DB[key]; break
        to_add["carbs"] = (c_weight * (kcal_density / 100)) / 70

    else: # 飯、麵
        c_weight = st.number_input(f"重量 (g)", min_value=0.0, step=1.0)
        to_add["carbs"] = c_weight / FIXED_CARBS_REF[carb_selection]

    carb_out = st.checkbox("外食加成 (額外加 1.5 份油脂)", key="c_out")
    
    if st.button("➕ 紀錄主食", use_container_width=True):
        for k in to_add:
            st.session_state.daily[k] += to_add[k]
        if carb_out:
            st.session_state.daily["fat"] += 1.5
        st.rerun()

# --- Tab 1: 奶類紀錄 ---
with tabs[1]:
    m_ml = st.number_input("飲用量 (ml)", min_value=0.0, step=50.0, key="m_ml")
    if st.button("➕ 紀錄奶類", use_container_width=True):
        st.session_state.daily["milk"] += (m_ml / 240); st.rerun()

# --- Tab 2: 肉類紀錄 ---
with tabs[2]:
    m_p = st.selectbox("部位", list(MEAT_DB.keys()), key="m_part")
    m_w = st.number_input("熟重 (g)", min_value=0.0, step=5.0, key="m_weight")
    meth = st.selectbox("烹調法", ["水煮", "氣炸", "油炒", "油炸"], key="m_method")
    m_out = st.checkbox("外食加成 (+1.5 油脂)", key="m_out")
    if st.button("➕ 紀錄肉類", use_container_width=True):
        serv = m_w / 35
        fat_type = MEAT_DB[m_p]
        if fat_type == "low": st.session_state.daily["protein_low"] += serv
        elif fat_type == "mid": st.session_state.daily["protein_mid"] += serv
        else: st.session_state.daily["protein_high"] += serv
        f_map = {"水煮": 0.0, "氣炸": 0.5, "油炒": 1.0, "油炸": 3.5}
        f_serv = f_map[meth]
        if m_out: f_serv += 1.5
        st.session_state.daily["fat"] += f_serv; st.rerun()

# --- Tab 3: 蔬菜紀錄 ---
with tabs[3]:
    v_n = st.selectbox("種類", GREEN_LIST + OTHER_VEG_LIST, key="v_name")
    v_w = st.number_input("重量 (g)", min_value=0.0, step=50.0, key="v_weight")
    if st.button("➕ 紀錄蔬菜", use_container_width=True):
        s = v_w / 100
        st.session_state.daily["veggie"] += s
        if v_n in GREEN_LIST: st.session_state.veggie_green += s
        st.rerun()

# --- Tab 4: 其他紀錄 ---
with tabs[4]:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        fa = st.number_input("手動油脂 (份)", min_value=0.0, step=0.5, key="extra_fat")
        if st.button("➕ 記油脂"): st.session_state.daily["fat"] += fa; st.rerun()
    with col_b:
        fr = st.number_input("水果重 (g)", min_value=0.0, step=10.0, key="fruit_w")
        if st.button("➕ 記水果"): st.session_state.daily["fruit"] += (fr/100); st.rerun()
    with col_c:
        sa = st.number_input("鹽巴 (g)", min_value=0.0, step=0.5, key="salt_w")
        if st.button("➕ 記鹽"): st.session_state.daily["salt"] += sa; st.rerun()

# --- Tab 5: 飲水紀錄 ---
with tabs[5]:
    w_val = st.number_input("水量 (ml)", min_value=0.0, step=50.0, value=250.0, key="water_in")
    if st.button("➕ 紀錄水", use_container_width=True): st.session_state.water += w_val; st.rerun()

# --- 6. 結算匯出 ---
st.divider()
status = "🟢達標" if (BASE_KCAL - 50 <= total_kcal <= BASE_KCAL) else "🔴未達標"
res_row = [
    datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), status, 
    f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", 
    f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", 
    f"{st.session_state.daily['veggie']:.1f}", f"{st.session_state.veggie_green:.1f}", 
    f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", 
    f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))
]
st.subheader("📋 Excel 匯出")
st.code("\t".join(res_row))

if st.button("🔄 重置今日數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
