import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 (2710kcal) ---
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

KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, 
    "protein_mid": 75, "protein_high": 120, 
    "veggie": 25, "fruit": 60, "fat": 45, "salt": 0
}

# --- 2. 資料庫配置 ---
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60,
    "五穀米/混合米 (60g/份)": 60,
    "煮過白麵條 (75g/份)": 75,
    "Tommi 炭香燒肉米漢堡 (固定數據)": "TOMMI_BBQ",
    "Tommi 壽喜燒肉米漢堡 (固定數據)": "TOMMI_SUKI",
    "米漢堡 (手動輸入標示)": "BURGER",
    "其他主食/自定義": "CUSTOM"
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

# --- Tab 0: 主食 (含 Tommi 與外食邏輯) ---
with tabs[0]:
    c_sel = st.selectbox("請選擇主食", list(FIXED_CARBS_REF.keys()))
    to_add = {k: 0.0 for k in KCAL_MAP.keys()}
    
    if c_sel == "Tommi 炭香燒肉米漢堡 (固定數據)":
        num = st.number_input("數量", min_value=1, step=1)
        to_add["carbs"], to_add["protein_mid"], to_add["fat"] = 3.2*num, 1.3*num, 1.8*num
    elif c_sel == "Tommi 壽喜燒肉米漢堡 (固定數據)":
        num = st.number_input("數量", min_value=1, step=1)
        to_add["carbs"], to_add["protein_mid"], to_add["fat"] = 3.3*num, 1.5*num, 1.0*num
    elif FIXED_CARBS_REF[c_sel] == "BURGER":
        col1, col2, col3 = st.columns(3)
        with col1: b_c = st.number_input("碳水(g)", min_value=0.0)
        with col2: b_p = st.number_input("蛋白(g)", min_value=0.0)
        with col3: b_f = st.number_input("脂肪(g)", min_value=0.0)
        to_add["carbs"], to_add["protein_mid"], to_add["fat"] = b_c/15, b_p/7, b_f/5
    elif FIXED_CARBS_REF[c_sel] == "CUSTOM":
        c_n = st.text_input("主食名稱")
        c_w = st.number_input("重量(g)", min_value=0.0)
        to_add["carbs"] = c_w / 60
    else:
        c_w = st.number_input("重量(g)", min_value=0.0)
        to_add["carbs"] = c_w / FIXED_CARBS_REF[c_sel]

    if st.checkbox("外食主食 (加 1.5 份油脂)", key="c_out"): to_add["fat"] += 1.5
    
    if st.button("➕ 紀錄主食"):
        for k, v in to_add.items(): st.session_state.daily[k] += v
        st.rerun()

# --- Tab 1: 奶類 (LP33 預設 + 智慧歸類) ---
with tabs[1]:
    m_opt = st.radio("選擇類型", ["LP33 / AB 優酪乳 (預設)", "其他奶類/蛋白質飲品"], horizontal=True)
    if m_opt == "LP33 / AB 優酪乳 (預設)":
        m_ml = st.number_input("飲用量 (ml)", value=240.0, step=10.0, key="default_milk")
        if st.button("➕ 紀錄預設奶類"):
            st.session_state.daily["milk"] += (m_ml / 240); st.rerun()
    else:
        m_name = st.text_input("輸入飲品名稱 (如：豆漿、燕麥奶、鮮奶)")
        m_ml = st.number_input("飲用量 (ml)", value=240.0, step=10.0, key="custom_milk")
        if st.button("➕ 分析並紀錄"):
            if "豆漿" in m_name:
                st.session_state.daily["protein_low"] += (m_ml / 240)
                st.success(f"已將『{m_name}』歸類至 低脂蛋白質")
            elif "燕麥奶" in m_name:
                st.session_state.daily["carbs"] += (m_ml / 240) * 2
                st.success(f"已將『{m_name}』歸類至 主食")
            else:
                st.session_state.daily["milk"] += (m_ml / 240)
            st.rerun()

# --- Tab 2: 肉類 (含固定部位 + 其他蛋白質判斷) ---
with tabs[2]:
    p_sel = st.selectbox("選擇肉類/蛋白質", list(MEAT_DB.keys()) + ["其他肉類/蛋白質選項"])
    if p_sel == "其他肉類/蛋白質選項":
        p_name = st.text_input("輸入名稱 (如：黑豆、板豆腐、毛豆)")
        p_w = st.number_input("重量 (g)", value=35.0)
        if st.button("➕ 智慧紀錄蛋白質"):
            low_fat = ["黑豆", "毛豆", "板豆腐", "豆腐", "雞胸", "里肌"]
            mid_fat = ["傳統豆腐", "蛋", "鮭魚"]
            if any(k in p_name for k in low_fat): st.session_state.daily["protein_low"] += p_w/35
            elif any(k in p_name for k in mid_fat): st.session_state.daily["protein_mid"] += p_w/35
            else: st.session_state.daily["protein_high"] += p_w/35
            st.rerun()
    else:
        p_w = st.number_input("重量 (g)", value=35.0, key="fixed_p_w")
        meth = st.selectbox("烹調", ["水煮", "氣炸", "油炒", "油炸"])
        p_out = st.checkbox("外食肉類 (+1.5 油脂)")
        if st.button("➕ 紀錄固定肉類"):
            fat_t = MEAT_DB[p_sel]
            st.session_state.daily[f"protein_{fat_t}"] += p_w/35
            f_map = {"水煮":0, "氣炸":0.5, "油炒":1, "油炸":3.5}
            st.session_state.daily["fat"] += f_map[meth] + (1.5 if p_out else 0)
            st.rerun()

# --- Tab 3: 蔬菜 (綠色蔬菜統計) ---
with tabs[3]:
    v_n = st.selectbox("種類", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("重量 (g)", value=100.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        serv = v_w / 100
        st.session_state.daily["veggie"] += serv
        if v_n in GREEN_LIST: st.session_state.veggie_green += serv
        st.rerun()

# --- Tab 4: 其他 ---
with tabs[4]:
    col1, col2, col3 = st.columns(3)
    with col1:
        fa = st.number_input("手動油脂", step=0.5)
        if st.button("記油"): st.session_state.daily["fat"] += fa; st.rerun()
    with col2:
        fr = st.number_input("水果(g)", step=10.0)
        if st.button("記果"): st.session_state.daily["fruit"] += fr/100; st.rerun()
    with col3:
        sa = st.number_input("鹽巴(g)", step=0.5)
        if st.button("記鹽"): st.session_state.daily["salt"] += sa; st.rerun()

# --- Tab 5: 飲水 ---
with tabs[5]:
    w_val = st.number_input("水量 (ml)", value=250.0)
    if st.button("記水"): st.session_state.water += w_val; st.rerun()

# --- 6. 結算匯出 ---
st.divider()
res_row = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), 
           f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", 
           f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", 
           f"{st.session_state.daily['veggie']:.1f}", f"{(st.session_state.veggie_green / 4.0 * 100):.1f}%", 
           f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", 
           f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]
st.code("\t".join(res_row))

if st.button("🔄 重置今日數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
