import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
GOALS = {
    "carbs": 16.0, "milk": 3.0, "protein_low": 7.0, 
    "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, 
    "fat": 5.5, "salt": 4.0
}

KCAL_MAP = {
    "carbs": 70, "milk": 150, "protein_low": 55, 
    "protein_mid": 75, "protein_high": 120, 
    "veggie": 25, "fruit": 60, "fat": 45, "salt": 0
}

# --- 2. 判斷邏輯資料庫 ---
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60, "五穀米 (60g/份)": 60, "煮過白麵條 (75g/份)": 75,
    "Tommi 炭香燒肉米漢堡": "TOMMI_BBQ", "Tommi 壽喜燒肉米漢堡": "TOMMI_SUKI",
    "其他主食/自定義": "CUSTOM"
}

# --- 3. 初始化 ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0
    st.session_state.water = 0.0

# --- 4. 儀表板 ---
st.set_page_config(page_title="2710kcal 智慧監控", layout="wide")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in KCAL_MAP.keys())
st.title(f"⚖️ 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

cols = st.columns(7)
display_items = [("🍞主食", "carbs"), ("🥛奶類", "milk"), ("🥩低脂肉", "protein_low"), 
                 ("🍖中脂肉", "protein_mid"), ("🥦蔬菜", "veggie"), ("🍎水果", "fruit"), ("🥑油脂", "fat")]
for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f}", delta=f"{current:.1f}")

st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他", "💧 飲水"])

# --- Tab 0: 主食 ---
with tabs[0]:
    c_sel = st.selectbox("選擇主食", list(FIXED_CARBS_REF.keys()))
    if c_sel == "其他主食/自定義":
        c_n = st.text_input("輸入名稱 (如：地瓜)")
        c_w = st.number_input("重量 (g)", step=1.0)
        if st.button("紀錄自定義主食"):
            st.session_state.daily["carbs"] += (c_w / 60) # 預設以米飯密度估算
            st.rerun()
    elif "Tommi" in c_sel:
        num = st.number_input("數量", min_value=1)
        if st.button("紀錄米漢堡"):
            if "炭香" in c_sel:
                st.session_state.daily["carbs"] += 3.2 * num
                st.session_state.daily["protein_mid"] += 1.3 * num
                st.session_state.daily["fat"] += 1.8 * num
            else:
                st.session_state.daily["carbs"] += 3.3 * num
                st.session_state.daily["protein_mid"] += 1.5 * num
                st.session_state.daily["fat"] += 1.0 * num
            st.rerun()
    else:
        c_w = st.number_input("重量 (g)", step=1.0)
        if st.button("紀錄標配主食"):
            st.session_state.daily["carbs"] += c_w / FIXED_CARBS_REF[c_sel]
            st.rerun()

# --- Tab 1: 奶類 (新增默認與智慧判斷) ---
with tabs[1]:
    m_sel = st.radio("奶類選項", ["LP33 / AB 優酪乳 (預設)", "其他奶類選項"], horizontal=True)
    
    if m_sel == "LP33 / AB 優酪乳 (預設)":
        m_ml = st.number_input("飲用量 (ml)", value=240.0, step=10.0)
        if st.button("紀錄預設奶類"):
            st.session_state.daily["milk"] += (m_ml / 240)
            st.rerun()
    else:
        other_m_name = st.text_input("請問喝了什麼？ (例如：豆漿、燕麥奶、鮮奶)")
        other_m_ml = st.number_input("飲用量 (ml)", value=240.0, step=10.0, key="other_m_ml")
        if st.button("紀錄並智慧歸類"):
            if "豆漿" in other_m_name:
                st.session_state.daily["protein_low"] += (other_m_ml / 240)
                st.success(f"偵測到『{other_m_name}』，已自動歸類至 低脂蛋白質")
            elif "燕麥奶" in other_m_name:
                st.session_state.daily["carbs"] += (other_m_ml / 240) * 2 # 燕麥奶碳水較高
                st.success(f"偵測到『{other_m_name}』，已自動歸類至 主食份數")
            else:
                st.session_state.daily["milk"] += (other_m_ml / 240)
                st.success(f"已紀錄 {other_m_name} 為一般奶類")
            st.rerun()

# --- Tab 2: 肉類 (新增其他蛋白質判斷) ---
with tabs[2]:
    p_sel = st.selectbox("選擇肉類/蛋白質", ["雞胸肉", "雞蛋", "梅花豬", "其他肉類/蛋白質選項"])
    
    if p_sel == "其他肉類/蛋白質選項":
        other_p_name = st.text_input("吃了什麼蛋白質？ (例如：板豆腐、黑豆、毛豆)")
        other_p_w = st.number_input("重量 (g)", value=35.0, step=5.0)
        if st.button("分析並紀錄蛋白質"):
            low_fat_keywords = ["黑豆", "毛豆", "板豆腐", "豆腐", "雞胸", "里肌"]
            mid_fat_keywords = ["傳統豆腐", "蛋", "鮭魚"]
            
            if any(k in other_p_name for k in low_fat_keywords):
                st.session_state.daily["protein_low"] += (other_p_w / 35)
                st.info(f"『{other_p_name}』判定為：低脂蛋白質來源")
            elif any(k in other_p_name for k in mid_fat_keywords):
                st.session_state.daily["protein_mid"] += (other_p_w / 35)
                st.info(f"『{other_p_name}』判定為：中脂蛋白質來源")
            else:
                st.session_state.daily["protein_high"] += (other_p_w / 35)
                st.warning("未辨識種類，預設紀錄為高脂肉類")
            st.rerun()
    else:
        p_w = st.number_input("熟重 (g)", value=35.0)
        if st.button("紀錄固定肉類"):
            # 簡化範例：雞胸=low, 蛋=mid, 梅花=mid
            target = "protein_low" if "雞胸" in p_sel else "protein_mid"
            st.session_state.daily[target] += (p_w / 35)
            st.rerun()

# --- 剩餘 Tab 保持功能 ---
with tabs[3]: # 蔬菜
    v_w = st.number_input("蔬菜重量 (g)", step=50.0)
    if st.button("紀錄蔬菜"):
        st.session_state.daily["veggie"] += (v_w / 100); st.rerun()

with tabs[4]: # 其他
    col_a, col_b = st.columns(2)
    with col_a:
        fa = st.number_input("額外油脂 (份)", step=0.5)
        if st.button("記油"): st.session_state.daily["fat"] += fa; st.rerun()
    with col_b:
        sa = st.number_input("鹽巴 (g)", step=0.5)
        if st.button("記鹽"): st.session_state.daily["salt"] += sa; st.rerun()

with tabs[5]: # 飲水
    w_val = st.number_input("水量 (ml)", value=250.0)
    if st.button("記水"): st.session_state.water += w_val; st.rerun()

# --- 結算匯出 ---
st.divider()
res_row = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), 
           f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", 
           f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", 
           f"{st.session_state.daily['veggie']:.1f}", f"{st.session_state.daily['fat']:.1f}", 
           str(round(st.session_state.water))]
st.code("\t".join(res_row))

if st.button("🔄 重置今日數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.water = 0.0; st.rerun()
