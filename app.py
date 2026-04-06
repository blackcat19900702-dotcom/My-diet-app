import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
# 1份熱量基準
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "protein_high": 120, "veggie": 25, "fruit": 60, "fat": 45, "salt": 0}

# --- 2. 資料庫 ---
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60,
    "五穀米/混合米 (60g/份)": 60,
    "煮過白麵條 (75g/份)": 75,
    "自定義主食 (手動輸入名稱與重量)": "CUSTOM"
}
CUSTOM_CARB_DB = {"地瓜": 120, "烤地瓜": 150, "馬鈴薯": 80, "吐司": 280, "燕麥": 380, "玉米": 110}

MEAT_DB = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "牛腱": "low", "里肌肉(豬)": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "梅花豬": "mid", "梅花牛": "mid", "雞腿肉(帶皮)": "mid",
    "牛肋條": "high", "肋眼牛排": "high", "豬五花": "high"
}
GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

# 初始化 session_state
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧飲食監控", layout="wide")

# --- 3. 儀表板 ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in KCAL_MAP.keys())
st.title("⚖️ 2710kcal 智慧飲食監控")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

cols = st.columns(7)
display_items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

# --- 4. 紀錄區 ---
st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

with tabs[0]: # 主食
    carb_selection = st.selectbox("請選擇主食種類", list(FIXED_CARBS_REF.keys()))
    if FIXED_CARBS_REF[carb_selection] != "CUSTOM":
        c_weight = st.number_input(f"你吃了多少克 {carb_selection}？ (g)", min_value=0.0, step=1.0)
        servings_to_add = c_weight / FIXED_CARBS_REF[carb_selection]
    else:
        c_name = st.text_input("1. 你吃了什麼東西？ (例如：地瓜、吐司)")
        c_weight = st.number_input("2. 你吃了幾克？ (g)", min_value=0.0, step=1.0)
        kcal_density = 140
        for key in CUSTOM_CARB_DB:
            if key in c_name: kcal_density = CUSTOM_CARB_DB[key]; break
        servings_to_add = (c_weight * (kcal_density / 100)) / 70
    carb_out = st.checkbox("外食主食 (自動加 1.5 油脂)", key="carb_out")
    if st.button("➕ 紀錄主食", use_container_width=True):
        st.session_state.daily["carbs"] += servings_to_add
        if carb_out: st.session_state.daily["fat"] += 1.5
        st.rerun()

with tabs[1]: # 奶類
    m_ml = st.number_input("奶類量 (ml)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄奶類", use_container_width=True):
        st.session_state.daily["milk"] += (m_ml / 240)
        st.rerun()

with tabs[2]: # 肉類
    m_p = st.selectbox("選擇部位 (含梅花牛、牛肋、肋眼)", list(MEAT_DB.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    meth = st.selectbox("烹調方式", ["水煮", "氣炸", "油炒", "油炸"])
    m_out = st.checkbox("外食肉類 (加 1.5 油脂)", key="meat_out")
    if st.button("➕ 紀錄肉類", use_container_width=True):
        serv = m_w / 35
        fat_type = MEAT_DB[m_p]
        if fat_type == "low": st.session_state.daily["protein_low"] += serv
        elif fat_type == "mid": st.session_state.daily["protein_mid"] += serv
        else: st.session_state.daily["protein_high"] += serv
        f_map = {"水煮":0.0, "氣炸":0.5, "油炒":1.0, "油炸":3.5}
        f = f_map[meth]
        if m_out: f += 1.5
        st.session_state.daily["fat"] += f
        st.rerun()

with tabs[3]: # 蔬菜
    v_n = st.selectbox("選擇蔬菜", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("蔬菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜", use_container_width=True):
        s = v_w / 100
        st.session_state.daily["veggie"] += s
        if v_n in GREEN_LIST: st.session_state.veggie_green += s
        st.rerun()

with tabs[4]: # 其他
    c1, c2, c3 = st.columns(3)
    with c1:
        fa = st.number_input("油脂 (份)", min_value=0.0, step=0.5)
        if st.button("➕ 記油脂"): st.session_state.daily["fat"] += fa; st.rerun()
    with c2:
        fr = st.number_input("水果重 (g)", min_value=0.0, step=10.0)
        if st.button("➕ 記水果"): st.session_state.daily["fruit"] += (fr/100); st.rerun()
    with c3:
        sa = st.number_input("鹽巴 (g)", min_value=0.0, step=0.5)
        if st.button("➕ 記鹽"): st.session_state.daily["salt"] += sa; st.rerun()

with tabs[5]: # 飲水
    w_val = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("➕ 紀錄水", use_container_width=True):
        st.session_state.water += w_val
        st.rerun()

# --- 5. Excel 結算 ---
st.divider()
status = "🟢達標" if (BASE_KCAL-50 <= total_kcal <= BASE_KCAL) else "🔴未達標"
res = [
    datetime.now().strftime("%Y/%m/%d"), 
    str(round(total_kcal)), 
    status, 
    f"{st.session_state.daily['carbs']:.1f}", 
    f"{st.session_state.daily['milk']:.1f}", 
    f"{st.session_state.daily['protein_low']:.1f}", 
    f"{st.session_state.daily['protein_mid']:.1f}", 
    f"{st.session_state.daily['veggie']:.1f}", 
    f"{st.session_state.veggie_green:.1f}", 
    f"{st.session_state.daily['fruit']:.1f}", 
    f"{st.session_state.daily['fat']:.1f}", 
    f"{st.session_state.daily['salt']:.1f}", 
    str(round(st.session_state.water))
]
st.subheader("📋 Excel 匯出 (請複製下方文字)")
st.code("\t".join(res))

if st.button("🔄 重置今日所有數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0
    st.session_state.water = 0.0
    st.rerun()
