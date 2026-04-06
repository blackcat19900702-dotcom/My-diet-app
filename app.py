import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
# 增加高脂肉熱量權重 (雖然目標沒列，但攝取時會扣減熱量額度)
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "protein_high": 120, "veggie": 25, "fruit": 60, "fat": 45, "salt": 0}

# --- 2. 資料庫更新 ---
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60,
    "五穀米/混合米 (60g/份)": 60,
    "煮過白麵條 (75g/份)": 75,
    "自定義主食 (手動輸入名稱與重量)": "CUSTOM"
}

CUSTOM_CARB_DB = {"地瓜": 120, "烤地瓜": 150, "馬鈴薯": 80, "吐司": 280, "燕麥": 380, "玉米": 110}

# 加入新肉類部位
MEAT_DB = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "牛腱": "low", "里肌肉(豬)": "low", "豆腐": "low",
    "雞蛋": "mid", "鮭魚": "mid", "梅花豬": "mid", "梅花牛": "mid", "雞腿肉(帶皮)": "mid",
    "牛肋條": "high", "肋眼牛排": "high", "豬五花": "high"
}

GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

st.set_page_config(page_title="2710kcal 監控系統", layout="wide")

# --- 3. 儀表板 ---
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in KCAL_MAP.keys())
st.title("⚖️ 2710kcal 智慧飲食監控")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

cols = st.columns(7)
display_items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    # 如果是肉類，合併顯示已吃份數
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f}", delta=f"{current:.1f} 已吃")

# --- 4. 紀錄區 ---
st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

with tabs[0]: # 主食邏輯
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

    carb_out = st.checkbox("外食主食 (自動加 1.5 油脂)")
    if st.button("➕ 紀錄主食"):
        st.session_state.daily["carbs"] += servings_to_add
        if carb_out: st.session_state.daily["fat"] += 1.5
        st.rerun()

with tabs[2]: # 肉類紀錄
    m_p = st.selectbox("選擇部位 (含新部位：梅花牛、牛肋條、肋眼)", list(MEAT_DB.keys()))
    m_w = st.number_input("熟肉重量 (g)", min_value=0.0, step=5.0)
    meth = st.selectbox("烹調方式", ["水煮", "氣炸", "油炒", "油炸"])
    m_out = st.checkbox("外食肉類 (加 1.5 油脂)")
    
    if st.button("➕ 紀錄肉類"):
        serv = m_w / 35
        fat_type = MEAT_DB[m_p]
        if fat_type == "low": st.session_state.daily["protein_low"] += serv
        elif fat_type == "mid": st.session_state.daily["protein_mid"] += serv
        else: st.session_state.daily["protein_high"] += serv
        
        f = {"水煮":0.0, "氣炸":0.5, "油炒":1.0, "油炸":3.5}[meth]
        if m_out: f += 1.5
        st.session_state.daily["fat"] += f; st.rerun()

# (其餘分頁代碼與先前一致，節略以保持簡潔)
# ... [奶類、蔬菜、油鹽、飲水、Excel 結算邏輯] ...
