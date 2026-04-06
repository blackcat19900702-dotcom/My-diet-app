import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "veggie": 25, "fruit": 60, "fat": 45, "salt": 0}

# --- 2. 主食與熱量資料庫 ---
# 預設固定種類及其基準 (每 1 份碳水的重量)
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60,
    "五穀米/混合米 (60g/份)": 60,
    "煮過白麵條 (75g/份)": 75,
    "自定義主食 (手動輸入名稱與重量)": "CUSTOM"
}

# 自定義主食的熱量密度資料庫 (每 100g 熟重之熱量)
CUSTOM_DB = {"地瓜": 120, "烤地瓜": 150, "馬鈴薯": 80, "吐司": 280, "燕麥": 380, "玉米": 110}

MEAT_DB = {"雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low", "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"}
GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 監控系統", layout="wide")

# --- 3. 儀表板 ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())
st.title("⚖️ 2710kcal 智慧飲食監控")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

cols = st.columns(7)
items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(items):
    current = st.session_state.daily[key]
    rem = GOALS[key] - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

# --- 4. 紀錄區 ---
st.divider()
tabs = st.tabs(["🍚 主食紀錄", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

with tabs[0]: # 主食邏輯修正
    st.write("### 🍞 主食輸入")
    carb_selection = st.selectbox("請選擇主食種類", list(FIXED_CARBS_REF.keys()))
    
    # 判斷：如果是預設種類
    if FIXED_CARBS_REF[carb_selection] != "CUSTOM":
        c_weight = st.number_input(f"你吃了多少克 {carb_selection}？ (g)", min_value=0.0, step=1.0)
        servings_to_add = c_weight / FIXED_CARBS_REF[carb_selection]
    
    # 判斷：如果是自定義
    else:
        c_name = st.text_input("1. 你吃了什麼東西？ (例如：地瓜、吐司)")
        c_weight = st.number_input("2. 你吃了幾克？ (g)", min_value=0.0, step=1.0)
        
        # 自動換算熱量 (預設 140kcal/100g)
        kcal_density = 140
        for key in CUSTOM_DB:
            if key in c_name:
                kcal_density = CUSTOM_DB[key]
                break
        # 熱量換算份數: (重量 * (密度/100)) / 70kcal
        servings_to_add = (c_weight * (kcal_density / 100)) / 70

    carb_out = st.checkbox("外食主食 (自動加 1.5 油脂)")
    
    if st.button("➕ 紀錄主食", use_container_width=True):
        st.session_state.daily["carbs"] += servings_to_add
        if carb_out: st.session_state.daily["fat"] += 1.5
        st.rerun()

# --- 其它部分保持穩定 (奶類、肉類、蔬菜、飲水) ---
with tabs[1]:
    m_ml = st.number_input("奶類量 (ml)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄奶類"): st.session_state.daily["milk"] += (m_ml / 240); st.rerun()

with tabs[2]:
    m_p = st.selectbox("肉類部位", list(MEAT_DB.keys()))
    m_w = st.number_input("肉重量 (g)", min_value=0.0, step=5.0)
    meth = st.selectbox("烹調方式", ["水煮", "氣炸", "油炒", "油炸"])
    m_out = st.checkbox("外食肉類 (加 1.5 油脂)")
    if st.button("➕ 紀錄肉類"):
        serv = m_w / 35
        if MEAT_DB[m_p] == "low": st.session_state.daily["protein_low"] += serv
        else: st.session_state.daily["protein_mid"] += serv
        f = {"水煮":0.0, "氣炸":0.5, "油炒":1.0, "油炸":3.5}[meth]
        if m_out: f += 1.5
        st.session_state.daily["fat"] += f; st.rerun()

with tabs[3]:
    v_n = st.selectbox("選擇蔬菜", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("蔬菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        s = v_w / 100
        st.session_state.daily["veggie"] += s
        if v_n in GREEN_LIST: st.session_state.veggie_green += s
        st.rerun()

with tabs[4]:
    c1, c2, c3 = st.columns(3)
    with c1:
        fa = st.number_input("手動油脂 (份)", min_value=0.0, step=0.5)
        if st.button("➕ 記油脂"): st.session_state.daily["fat"] += fa; st.rerun()
    with c2:
        fr = st.number_input("水果重量 (g)", min_value=0.0, step=10.0)
        if st.button("➕ 記水果"): st.session_state.daily["fruit"] += (fr/100); st.rerun()
    with c3:
        sa = st.number_input("鹽巴 (g)", min_value=0.0, step=0.5)
        if st.button("➕ 記鹽巴"): st.session_state.daily["salt"] += sa; st.rerun()

with tabs[5]:
    w_val = st.number_input("飲水 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("➕ 紀錄水"): st.session_state.water += w_val; st.rerun()

# --- 5. Excel 結算 ---
st.divider()
status = "🟢達標" if (BASE_KCAL-50 <= total_kcal <= BASE_KCAL) else "🔴未達標"
res = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), status, f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", f"{st.session_state.daily['veggie']:.1f}", f"{st.session_state.veggie_green:.1f}", f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]
st.code("\t".join(res))

if st.button("🔄 重置"):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}; st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
