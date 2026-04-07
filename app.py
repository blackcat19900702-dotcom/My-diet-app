import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 (2710kcal) ---
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

# --- 2. 資料庫配置 ---
FIXED_CARBS_REF = {
    "白米飯 (60g/份)": 60, "五穀米/混合米 (60g/份)": 60, "煮過白麵條 (75g/份)": 75,
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

# --- 3. 初始化 ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

# --- 4. 網頁配置 ---
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
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

# --- Tab 內容 (維持所有智慧功能) ---
with tabs[0]: # 主食
    c_sel = st.selectbox("選擇主食", list(FIXED_CARBS_REF.keys()))
    to_add = {k: 0.0 for k in KCAL_MAP.keys()}
    if "Tommi" in c_sel:
        num = st.number_input("數量", min_value=1, step=1)
        if "炭香" in c_sel: to_add["carbs"], to_add["protein_mid"], to_add["fat"] = 3.2*num, 1.3*num, 1.8*num
        else: to_add["carbs"], to_add["protein_mid"], to_add["fat"] = 3.3*num, 1.5*num, 1.0*num
    elif FIXED_CARBS_REF[c_sel] == "BURGER":
        c1, c2, c3 = st.columns(3); b_c = c1.number_input("碳水(g)"); b_p = c2.number_input("蛋白(g)"); b_f = c3.number_input("脂肪(g)")
        to_add["carbs"], to_add["protein_mid"], to_add["fat"] = b_c/15, b_p/7, b_f/5
    elif FIXED_CARBS_REF[c_sel] == "CUSTOM":
        c_n = st.text_input("主食名稱"); c_w = st.number_input("重量(g)")
        to_add["carbs"] = c_w / 60
    else:
        c_w = st.number_input("重量(g)")
        to_add["carbs"] = c_w / FIXED_CARBS_REF[c_sel]
    if st.checkbox("外食主食 (+1.5 油脂)", key="c_out"): to_add["fat"] += 1.5
    if st.button("➕ 紀錄主食"):
        for k, v in to_add.items(): st.session_state.daily[k] += v
        st.rerun()

with tabs[1]: # 奶類
    m_opt = st.radio("選擇類型", ["LP33 / AB 優酪乳 (預設)", "其他奶類/蛋白質飲品"], horizontal=True)
    if m_opt == "LP33 / AB 優酪乳 (預設)":
        m_ml = st.number_input("飲用量 (ml)", value=240.0)
        if st.button("➕ 紀錄預設奶類"): st.session_state.daily["milk"] += (m_ml / 240); st.rerun()
    else:
        m_name = st.text_input("輸入名稱 (如：豆漿、燕麥奶)"); m_ml = st.number_input("飲用量 (ml)", value=240.0)
        if st.button("➕ 分析並紀錄"):
            if "豆漿" in m_name: st.session_state.daily["protein_low"] += (m_ml / 240)
            elif "燕麥奶" in m_name: st.session_state.daily["carbs"] += (m_ml / 240) * 2
            else: st.session_state.daily["milk"] += (m_ml / 240)
            st.rerun()

with tabs[2]: # 肉類
    p_sel = st.selectbox("選擇肉類", list(MEAT_DB.keys()) + ["其他肉類/蛋白質選項"])
    if p_sel == "其他肉類/蛋白質選項":
        p_name = st.text_input("輸入名稱"); p_w = st.number_input("重量 (g)", value=35.0)
        if st.button("➕ 智慧紀錄蛋白質"):
            low = ["黑豆", "毛豆", "板豆腐", "豆腐", "雞胸"]; mid = ["傳統豆腐", "蛋", "鮭魚"]
            if any(k in p_name for k in low): st.session_state.daily["protein_low"] += p_w/35
            elif any(k in p_name for k in mid): st.session_state.daily["protein_mid"] += p_w/35
            else: st.session_state.daily["protein_high"] += p_w/35
            st.rerun()
    else:
        p_w = st.number_input("重量 (g)", value=35.0); meth = st.selectbox("烹調法", ["水煮", "氣炸", "油炒", "油炸"]); p_out = st.checkbox("外食肉類 (+1.5 油脂)")
        if st.button("➕ 紀錄肉類"):
            st.session_state.daily[f"protein_{MEAT_DB[p_sel]}"] += p_w/35
            f_map = {"水煮":0, "氣炸":0.5, "油炒":1, "油炸":3.5}
            st.session_state.daily["fat"] += f_map[meth] + (1.5 if p_out else 0); st.rerun()

with tabs[3]: # 蔬菜
    v_n = st.selectbox("種類", GREEN_LIST + OTHER_VEG_LIST); v_w = st.number_input("重量 (g)", value=100.0)
    if st.button("➕ 紀錄蔬菜"):
        st.session_state.daily["veggie"] += v_w/100
        if v_n in GREEN_LIST: st.session_state.veggie_green += v_w/100
        st.rerun()

with tabs[4]: # 其他 / 5: 飲水
    c1, c2, c3 = st.columns(3); fa = c1.number_input("油脂份"); fr = c2.number_input("水果份"); sa = c3.number_input("鹽(g)")
    if st.button("➕ 紀錄額外項"): st.session_state.daily["fat"]+=fa; st.session_state.daily["fruit"]+=fr; st.session_state.daily["salt"]+=sa; st.rerun()
with tabs[5]:
    w_val = st.number_input("水量 (ml)", value=250.0)
    if st.button("➕ 記水"): st.session_state.water += w_val; st.rerun()

# --- 6. 結算匯出 (前台顯示標題，複製區僅數據) ---
st.divider()
st.subheader("📋 今日數據匯出")

# 計算綠色蔬菜佔比
green_pct = (st.session_state.veggie_green / st.session_state.daily['veggie'] * 100) if st.session_state.daily['veggie'] > 0 else 0

# 前台對照表 (僅顯示用)
headers = ["日期", "總熱量", "主食份", "奶類份", "低脂肉", "中脂肉", "總蔬菜", "綠菜佔比", "水果份", "油脂份", "鹽份(g)", "飲水(ml)"]
data_list = [
    datetime.now().strftime("%Y/%m/%d"), 
    str(round(total_kcal)), 
    f"{st.session_state.daily['carbs']:.1f}", 
    f"{st.session_state.daily['milk']:.1f}", 
    f"{st.session_state.daily['protein_low']:.1f}", 
    f"{st.session_state.daily['protein_mid']:.1f}", 
    f"{st.session_state.daily['veggie']:.1f}", 
    f"{green_pct:.1f}%", 
    f"{st.session_state.daily['fruit']:.1f}", 
    f"{st.session_state.daily['fat']:.1f}", 
    f"{st.session_state.daily['salt']:.1f}", 
    str(round(st.session_state.water))
]

# 顯示前台表格對照
st.table([headers, data_list])

# 複製專區 (僅存放純數據，方便直接貼入 Excel 下一列)
copy_data_only = "\t".join(data_list)
st.text_area("👇 僅複製下方純數據 (貼入 Excel)：", value=copy_data_only, height=70)

if st.button("🔄 重置今日數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
