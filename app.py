import streamlit as st
from datetime import datetime

# --- 1. 核心配額與目標 ---
BASE_KCAL = 2710  
VEG_GOAL = 4.0
GOALS = {"carbs": 16.0, "milk": 3.0, "protein_low": 7.0, "protein_mid": 3.5, "veggie": 4.0, "fruit": 3.0, "fat": 5.5, "salt": 4.0}
KCAL_MAP = {"carbs": 70, "milk": 150, "protein_low": 55, "protein_mid": 75, "protein_high": 120, "veggie": 25, "fruit": 60, "fat": 45}

# --- 2. 初始化 Session State ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in GOALS.keys()}
    st.session_state.daily["protein_high"] = 0.0
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0
    st.session_state.logs = [] 

# --- 3. 頁面配置 ---
st.set_page_config(page_title="2710kcal 專業監控", layout="wide")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in st.session_state.daily.keys())

st.title("⚖️ 2710kcal 全功能精準監控系統")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

# 狀態列
cols = st.columns(7)
display_items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

# --- Tab 0: 主食 (恢復混合米、Tommi 數據) ---
with tabs[0]:
    c_sel = st.selectbox("主食選擇", ["白米飯 (60g/份)", "白米混合五穀米 (60g/份)", "五穀米/玄米 (60g/份)", "煮過白麵條 (75g/份)", "Tommi 炭香燒肉米漢堡", "Tommi 壽喜燒肉米漢堡", "其他自定義"])
    c_out = st.checkbox("外食主食 (+1.5 油脂)")
    if "Tommi" in c_sel:
        num = st.number_input("數量", min_value=1, step=1)
        if st.button("➕ 紀錄 Tommi"):
            if "炭香" in c_sel: c, p, f = 3.2*num, 1.3*num, 1.8*num
            else: c, p, f = 3.3*num, 1.5*num, 1.0*num
            st.session_state.daily["carbs"] += c
            st.session_state.daily["protein_mid"] += p
            st.session_state.daily["fat"] += f + (1.5 if c_out else 0)
            st.session_state.logs.append(f"{c_sel} x{num}")
            st.rerun()
    else:
        c_w = st.number_input("重量 (g)", value=60.0)
        if st.button("➕ 紀錄主食"):
            div = 75 if "麵" in c_sel else 60
            serv = c_w / div
            st.session_state.daily["carbs"] += serv
            if c_out: st.session_state.daily["fat"] += 1.5
            st.session_state.logs.append(f"{c_sel} {c_w}g")
            st.rerun()

# --- Tab 1: 奶類 ---
with tabs[1]:
    m_name = st.text_input("飲品名稱 (LP33、豆漿、燕麥奶)")
    m_ml = st.number_input("飲用量 (ml)", value=240.0)
    if st.button("➕ 紀錄飲品"):
        serv = m_ml / 240
        if "豆漿" in m_name: st.session_state.daily["protein_low"] += serv
        elif "燕麥奶" in m_name: st.session_state.daily["carbs"] += serv * 2
        else: st.session_state.daily["milk"] += serv
        st.session_state.logs.append(f"{m_name} {m_ml}ml")
        st.rerun()

# --- Tab 2: 肉類 (恢復牛肉判定：牛腱、牛肋、牛五花) ---
with tabs[2]:
    p_name = st.selectbox("選擇肉類", ["牛腱 (低脂)", "牛肋條 (高脂)", "牛五花 (高脂)", "雞胸肉", "雞蛋", "鮭魚", "豆腐", "黑豆", "其他"])
    p_w = st.number_input("重量 (g)", value=35.0)
    meth = st.selectbox("烹調方式", ["水煮", "氣炸(+0.5油)", "油炒(+1油)", "油炸(+3.5油)"])
    if st.button("➕ 紀錄蛋白質"):
        serv = p_w / 35
        # 判定分類
        low = ["雞胸", "黑豆", "豆腐", "牛腱", "鯛魚"]
        mid = ["雞蛋", "鮭魚", "雞腿", "梅花"]
        high = ["牛肋", "五花", "培根"]
        
        if any(k in p_name for k in low): p_key = "protein_low"
        elif any(k in p_name for k in mid): p_key = "protein_mid"
        else: p_key = "protein_high"
        
        st.session_state.daily[p_key] += serv
        st.session_state.daily["fat"] += {"水煮":0, "氣炸":0.5, "油炒":1, "油炸":3.5}[meth]
        st.session_state.logs.append(f"{p_name} {p_w}g ({meth})")
        st.rerun()

# --- Tab 3: 蔬菜 (達成率：分母 4.0) ---
with tabs[3]:
    v_name = st.text_input("蔬菜名稱")
    v_w = st.number_input("重量 (g)", value=100.0)
    if st.button("➕ 紀錄蔬菜"):
        serv = v_w / 100
        st.session_state.daily["veggie"] += serv
        if any(k in v_name for k in ["綠", "青", "菠", "地瓜葉", "芥藍", "苗", "空心", "龍鬚"]):
            st.session_state.veggie_green += serv
        st.session_state.logs.append(f"{v_name} {v_w}g")
        st.rerun()

# --- Tab 4 & 5: 其他與飲水 ---
with tabs[4]:
    c1, c2, c3 = st.columns(3)
    fa = c1.number_input("油脂份", step=0.5); fr = c2.number_input("水果份", step=0.5); sa = c3.number_input("鹽(g)", step=0.5)
    if st.button("➕ 紀錄項目"):
        st.session_state.daily["fat"]+=fa; st.session_state.daily["fruit"]+=fr; st.session_state.daily["salt"]+=sa
        st.session_state.logs.append(f"補充: 油{fa}/果{fr}/鹽{sa}")
        st.rerun()
with tabs[5]:
    w_ml = st.number_input("飲水量 (ml)", value=250.0)
    if st.button("➕ 記水"):
        st.session_state.water += w_ml
        st.session_state.logs.append(f"飲水 {w_ml}ml")
        st.rerun()

# --- 6. 結算匯出 ---
st.divider()
st.subheader("📋 今日數據匯出")
green_achieve = (st.session_state.veggie_green / VEG_GOAL) * 100
headers = ["日期", "總熱量", "主食份", "奶類份", "低脂肉", "中脂肉", "總蔬菜", "綠菜達成率", "水果份", "油脂份", "鹽份(g)", "飲水(ml)"]
data_list = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", f"{st.session_state.daily['veggie']:.1f}", f"{green_achieve:.1f}%", f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]

st.table([headers, data_list])
copy_data = "\t".join(data_list)
st.components.v1.html(f"""
    <button onclick="navigator.clipboard.writeText('{copy_data}').then(()=>alert('數據已複製'))" 
    style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:8px; font-size:18px; font-weight:bold; cursor:pointer;">
    📋 一鍵複製數據列 (貼入 Excel)
    </button>
""", height=70)

# --- 7. 今日紀錄明細 ---
with st.expander("📝 檢查今日明細"):
    for log in st.session_state.logs: st.write(f"- {log}")
    if st.button("🔄 重置今日"):
        st.session_state.daily = {k: 0.0 for k in GOALS.keys()}; st.session_state.daily["protein_high"]=0.0; st.session_state.veggie_green=0.0; st.session_state.water=0.0; st.session_state.logs=[]; st.rerun()
