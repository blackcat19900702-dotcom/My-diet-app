import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
WATER_GOAL = 3000.0
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
# 1份碳水(carbs) = 70kcal
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "veggie": 25, "fruit": 60, "fat": 45, "salt": 0}

# --- 2. 自動計算資料庫 (每 100g 的熱量) ---
# 系統會根據你輸入的關鍵字自動匹配
FOOD_KCAL_DB = {
    "白米": 140,      # 每 100g 熟重約 140kcal
    "五穀米": 145,
    "混合米": 140,
    "麵條": 150,      # 熟麵條
    "地瓜": 120,      # 蒸地瓜
    "烤地瓜": 150,    # 脫水後熱量密度增高
    "馬鈴薯": 80,
    "吐司": 280,
    "燕麥": 380,
}

# 肉類/蔬菜資料庫保持不變
MEAT_DB = {"雞胸肉": "low", "雞腿肉(去皮)": "low", "和尚頭(牛)": "low", "牛腱": "low", "里肌肉(豬)": "low", "鱈魚": "low", "豆腐": "low", "雞蛋": "mid", "鮭魚": "mid", "嫩肩里肌(板腱)": "mid", "梅花豬": "mid", "豬絞肉": "mid", "雞腿肉(帶皮)": "mid"}
GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 智慧飲食監控", layout="wide")

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
tabs = st.tabs(["🍚 主食(輸入名稱與重量)", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

with tabs[0]: # 主食：最直覺輸入
    st.write("### 🍞 紀錄你吃了什麼主食")
    c_name = st.text_input("1. 你吃了什麼？ (例如：白米、地瓜、麵條)", key="carb_name_input")
    c_weight = st.number_input("2. 你吃了幾克？ (g)", min_value=0.0, step=1.0, key="carb_weight_input")
    carb_out = st.checkbox("這餐是外食 (自動增加 1.5 份油脂)", key="carb_out_flag")
    
    if st.button("➕ 點擊紀錄並計算熱量", use_container_width=True):
        if c_name and c_weight > 0:
            # 自動匹配資料庫熱量，找不到就預設為 140kcal/100g
            matched_kcal = 140
            for key in FOOD_KCAL_DB:
                if key in c_name:
                    matched_kcal = FOOD_KCAL_DB[key]
                    break
            
            # 計算總熱量 = 重量 * (每克熱量)
            total_carb_kcal = c_weight * (matched_kcal / 100)
            # 換算成份數 (1 份碳水 = 70kcal)
            servings = total_carb_kcal / 70
            
            st.session_state.daily["carbs"] += servings
            if carb_out:
                st.session_state.daily["fat"] += 1.5
            st.success(f"紀錄成功！已自動根據 {c_name} 的熱量密度計算出 {servings:.1f} 份碳水。")
            st.rerun()

with tabs[1]: # 奶類
    m_ml = st.number_input("奶類紀錄 (ml)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄奶類"):
        st.session_state.daily["milk"] += (m_ml / 240); st.rerun()

with tabs[2]: # 肉類
    m_p = st.selectbox("肉類部位", list(MEAT_DB.keys()))
    m_w = st.number_input("肉重量 (g)", min_value=0.0, step=5.0)
    meth = st.selectbox("烹調方式", ["水煮", "氣炸", "油炒", "油炸"])
    m_out = st.checkbox("外食肉類 (加 1.5 油脂)")
    if st.button("➕ 紀錄肉類"):
        serv = m_w / 35
        if MEAT_DB[m_p] == "low": st.session_state.daily["protein_low"] += serv
        else: st.session_state.daily["protein_mid"] += serv
        f_map = {"水煮":0.0, "氣炸":0.5, "油炒":1.0, "油炸":3.5}
        f = f_map[meth]
        if m_out: f += 1.5
        st.session_state.daily["fat"] += f; st.rerun()

with tabs[3]: # 蔬菜
    v_n = st.selectbox("選擇蔬菜", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("蔬菜重量 (g)", min_value=0.0, step=50.0)
    if st.button("➕ 紀錄蔬菜"):
        s = v_w / 100
        st.session_state.daily["veggie"] += s
        if v_n in GREEN_LIST: st.session_state.veggie_green += s
        st.rerun()

with tabs[4]: # 其它
    c1, c2, c3 = st.columns(3)
    with c1:
        fa = st.number_input("手動增加油脂 (份)", min_value=0.0, step=0.5)
        if st.button("➕ 記油脂"): st.session_state.daily["fat"] += fa; st.rerun()
    with c2:
        fr = st.number_input("水果重量 (g)", min_value=0.0, step=10.0)
        if st.button("➕ 記水果"): st.session_state.daily["fruit"] += (fr/100); st.rerun()
    with c3:
        sa = st.number_input("鹽巴份量 (g)", min_value=0.0, step=0.5)
        if st.button("➕ 記鹽巴"): st.session_state.daily["salt"] += sa; st.rerun()

with tabs[5]: # 水
    w_val = st.number_input("本次飲水量 (ml)", min_value=0.0, step=50.0, value=250.0)
    if st.button("➕ 紀錄飲水"): st.session_state.water += w_val; st.rerun()

# --- 5. Excel 結算 ---
st.divider()
status = "🟢達標" if (BASE_KCAL-50 <= total_kcal <= BASE_KCAL) else "🔴未達標"
res = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), status, f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", f"{st.session_state.daily['veggie']:.1f}", f"{st.session_state.veggie_green:.1f}", f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]
st.code("\t".join(res))

if st.button("🔄 重置"):
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}; st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
