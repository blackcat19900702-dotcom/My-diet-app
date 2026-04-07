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
    "雞蛋": "mid", "鮭魚": "mid", "梅花豬": "mid", "牛肋條": "high", "豬五花": "high"
}

# 綠色蔬菜關鍵字判定
GREEN_KEYWORDS = ["綠", "青", "菠", "苗", "地瓜葉", "芥藍", "空心菜", "龍鬚", "秋葵"]

# --- 3. 初始化 ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

# --- 4. 網頁配置 ---
st.set_page_config(page_title="2710kcal 智慧飲食監控系統", layout="wide")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in KCAL_MAP.keys())

st.title("⚖️ 2710kcal 智慧飲食監控")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

cols = st.columns(7)
display_items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), 
                 ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

# --- Tab 0: 主食 ---
with tabs[0]:
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
    if st.checkbox("外食主食 (+1.5 油脂)"): to_add["fat"] += 1.5
    if st.button("➕ 紀錄主食"):
        for k, v in to_add.items(): st.session_state.daily[k] += v
        st.rerun()

# --- Tab 1: 奶類 ---
with tabs[1]:
    m_opt = st.radio("選擇類型", ["LP33 / AB 優酪乳 (預設)", "其他奶類選項"], horizontal=True)
    if m_opt == "LP33 / AB 優酪乳 (預設)":
        m_ml = st.number_input("飲用量 (ml)", value=240.0)
        if st.button("➕ 紀錄預設奶類"): st.session_state.daily["milk"] += (m_ml / 240); st.rerun()
    else:
        m_name = st.text_input("喝了什麼？ (豆漿會轉低脂肉)"); m_ml = st.number_input("飲用量 (ml)", value=240.0, key="milk_ml")
        if st.button("➕ 奶類智慧紀錄"):
            if "豆漿" in m_name: st.session_state.daily["protein_low"] += (m_ml / 240)
            elif "燕麥奶" in m_name: st.session_state.daily["carbs"] += (m_ml / 240) * 2
            else: st.session_state.daily["milk"] += (m_ml / 240)
            st.rerun()

# --- Tab 2: 肉類 ---
with tabs[2]:
    p_sel = st.selectbox("選擇肉類", list(MEAT_DB.keys()) + ["其他肉類/蛋白質"])
    if p_sel == "其他肉類/蛋白質":
        p_name = st.text_input("吃了什麼？ (如：黑豆、板豆腐)"); p_w = st.number_input("重量 (g)", value=35.0)
        if st.button("➕ 蛋白質智慧紀錄"):
            low = ["黑豆", "毛豆", "板豆腐", "豆腐", "雞胸"]; mid = ["傳統豆腐", "蛋", "鮭魚"]
            if any(k in p_name for k in low): st.session_state.daily["protein_low"] += p_w/35
            elif any(k in p_name for k in mid): st.session_state.daily["protein_mid"] += p_w/35
            else: st.session_state.daily["protein_high"] += p_w/35
            st.rerun()
    else:
        p_w = st.number_input("重量 (g)", value=35.0); meth = st.selectbox("烹調", ["水煮", "氣炸", "油炒", "油炸"])
        if st.button("➕ 紀錄固定肉類"):
            st.session_state.daily[f"protein_{MEAT_DB[p_sel]}"] += p_w/35
            f_map = {"水煮":0, "氣炸":0.5, "油炒":1, "油炸":3.5}
            st.session_state.daily["fat"] += f_map[meth]; st.rerun()

# --- Tab 3: 蔬菜 (智慧判定綠色蔬菜邏輯) ---
with tabs[3]:
    v_opt = st.radio("蔬菜選擇", ["常用蔬菜", "其他蔬菜 (智慧判定)"], horizontal=True)
    if v_opt == "常用蔬菜":
        v_n = st.selectbox("種類", ["高麗菜", "綠花椰", "地瓜葉", "菠菜", "菇類", "櫛瓜"])
        v_w = st.number_input("重量 (g)", value=100.0)
        if st.button("➕ 紀錄常用蔬菜"):
            serv = v_w / 100
            st.session_state.daily["veggie"] += serv
            if any(k in v_n for k in ["綠", "菠", "地瓜葉"]): st.session_state.veggie_green += serv
            st.rerun()
    else:
        v_name = st.text_input("輸入蔬菜名稱 (例如：青江菜、娃娃菜)")
        v_w = st.number_input("重量 (g)", value=100.0, key="veg_custom_w")
        if st.button("➕ 智慧紀錄蔬菜"):
            serv = v_w / 100
            st.session_state.daily["veggie"] += serv
            if any(k in v_name for k in GREEN_KEYWORDS):
                st.session_state.veggie_green += serv
                st.success(f"偵測到『{v_name}』為深綠色蔬菜")
            st.rerun()

# --- Tab 4 & 5: 其他與飲水 ---
with tabs[4]:
    c1, c2, c3 = st.columns(3); fa = c1.number_input("油脂份"); fr = c2.number_input("水果份"); sa = c3.number_input("鹽(g)")
    if st.button("➕ 紀錄額外"): st.session_state.daily["fat"]+=fa; st.session_state.daily["fruit"]+=fr; st.session_state.daily["salt"]+=sa; st.rerun()
with tabs[5]:
    w_v = st.number_input("水量 (ml)", value=250.0)
    if st.button("➕ 記水"): st.session_state.water += w_v; st.rerun()

# --- 6. 結算匯出 (一鍵複製純數據) ---
st.divider()
st.subheader("📋 今日數據對照")
green_pct = (st.session_state.veggie_green / st.session_state.daily['veggie'] * 100) if st.session_state.daily['veggie'] > 0 else 0
headers = ["日期", "總熱量", "主食份", "奶類份", "低脂肉", "中脂肉", "總蔬菜", "綠菜佔比", "水果份", "油脂份", "鹽份(g)", "飲水(ml)"]
data_list = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", f"{st.session_state.daily['veggie']:.1f}", f"{green_pct:.1f}%", f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]

st.table([headers, data_list])
copy_text = "\t".join(data_list)
copy_js = f"""
    <button onclick="copyToClipboard()" style="width: 100%; padding: 15px; background-color: #28a745; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer;">📋 點擊一鍵複製數據列 (直接貼入 Excel)</button>
    <script>
    function copyToClipboard() {{
        const text = "{copy_text}";
        const dummy = document.createElement("textarea");
        document.body.appendChild(dummy); dummy.value = text; dummy.select(); document.execCommand("copy"); document.body.removeChild(dummy);
        alert("數據列已複製！");
    }}
    </script>
"""
st.components.v1.html(copy_js, height=80)

if st.button("🔄 重置今日數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}; st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
