import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
WATER_GOAL = 3000.0
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "veggie": 25, "fruit": 60, "fat": 45, "salt": 0}

# --- 2. 主食基準資料庫 (依據你提供的數據) ---
# 這裡定義的是：你輸入多少克，會被算作「4份」(一碗) 的基準
CARBS_REF = {
    "白米飯 (基準 240g)": 240.0,
    "五穀米/混合米 (基準 240g)": 240.0,
    "煮過白麵條 (基準 300g)": 300.0,
    "自蒸地瓜 (基準 220g)": 220.0, # 55g*4
    "超商烤地瓜 (基準 200g)": 200.0, # 50g*4
    "其他主食 (手動輸入重量)": 240.0
}

MEAT_DATABASE = {"雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low", "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"}
GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧飲食導航", layout="wide")

# --- 3. 儀表板 ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in GOALS.keys())
is_perfect = (BASE_KCAL - 50) <= total_kcal <= BASE_KCAL

st.title("⚖️ 2710kcal 智慧飲食監控")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

if is_perfect:
    st.success("🟢 綠燈：熱量控制精準")
else:
    st.error("🔴 紅燈：熱量偏差過大")

cols = st.columns(7)
items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(items):
    current = st.session_state.daily[key]
    rem = GOALS[key] - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

# --- 4. 紀錄區 ---
st.divider()
tabs = st.tabs(["🍚 主食(輸入克數)", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

with tabs[0]: # 主食：純克數輸入
    carb_choice = st.selectbox("請選擇主食類型", list(CARBS_REF.keys()))
    c_weight = st.number_input("請輸入攝取重量 (g)", min_value=0.0, step=10.0, key="carbs_weight")
    carb_out = st.checkbox("這餐是外食 (自動加 1.5 油脂)", key="carb_out_check")
    
    if st.button("➕ 紀錄主食重量"):
        # 計算份數：(輸入重量 / 基準重量) * 4 份
        # 例如：輸入 240g / 基準 240g * 4 = 4份
        # 例如：麵條輸入 150g / 基準 300g * 4 = 2份
        calculated_servings = (c_weight / CARBS_REF[carb_choice]) * 4
        st.session_state.daily["carbs"] += calculated_servings
        if carb_out:
            st.session_state.daily["fat"] += 1.5
        st.rerun()

with tabs[1]: # 奶類
    m_ml = st.number_input("奶類量 (ml)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄奶類"):
        st.session_state.daily["milk"] += (m_ml / 240)
        st.rerun()

with tabs[2]: # 肉類
    m_p = st.selectbox("部位", list(MEAT_DATABASE.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    meth = st.selectbox("烹調方式", ["水煮", "氣炸", "油炒", "油炸"])
    m_out = st.checkbox("外食肉 (加 1.5 油脂)")
    if st.button("➕ 紀錄肉類"):
        serv = m_w / 35
        if MEAT_DATABASE[m_p] == "low": st.session_state.daily["protein_low"] += serv
        else: st.session_state.daily["protein_mid"] += serv
        f = 0.5 if meth == "氣炸" else (1.0 if meth == "油炒" else (3.5 if meth == "油炸" else 0.0))
        if m_out: f += 1.5
        st.session_state.daily["fat"] += f
        st.rerun()

with tabs[3]: # 蔬菜
    v_n = st.selectbox("蔬菜種類", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("蔬菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        s = v_w / 100
        st.session_state.daily["veggie"] += s
        if v_n in GREEN_LIST: st.session_state.veggie_green += s
        st.rerun()

with tabs[4]: # 油鹽水果
    c1, c2, c3 = st.columns(3)
    with c1:
        fa = st.number_input("手動油脂 (份)", min_value=0.0, step=0.5)
        if st.button("➕ 記油"): st.session_state.daily["fat"] += fa; st.rerun()
    with c2:
        fr = st.number_input("水果重量 (g)", min_value=0.0, step=50.0)
        if st.button("➕ 記水果"): st.session_state.daily["fruit"] += (fr/100); st.rerun()
    with c3:
        sa = st.number_input("鹽巴 (g)", min_value=0.0, step=0.5)
        if st.button("➕ 記鹽"): st.session_state.daily["salt"] += sa; st.rerun()

with tabs[5]: # 水
    w_val = st.number_input("飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("➕ 紀錄水"): st.session_state.water += w_val; st.rerun()

# --- 5. Excel 結算 ---
st.divider()
status = "🟢綠燈" if is_perfect else "🔴紅燈"
res = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), status, f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", f"{st.session_state.daily['veggie']:.1f}", f"{st.session_state.veggie_green:.1f}", f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]
st.subheader("📋 直接複製到 Excel")
st.code("\t".join(res))

if st.button("🔄 重置今天"):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}; st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
