import streamlit as st
from datetime import datetime

# --- 1. 定義配額目標 ---
BASE_KCAL = 2710  
VEG_GOAL = 4.0  # 蔬菜目標份數

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

# --- 2. 初始化 ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

# --- 3. 網頁配置 ---
st.set_page_config(page_title="2710kcal 飲食達成率監控", layout="wide")
total_kcal = sum(st.session_state.daily[k] * KCAL_MAP.get(k, 0) for k in KCAL_MAP.keys())

st.title("⚖️ 2710kcal 達成率監控系統")
st.subheader(f"🔥 今日總熱量: {total_kcal:.0f} / {BASE_KCAL} kcal")

# 顯示各項進度
cols = st.columns(7)
display_items = [("🍞 主食", "carbs"), ("🥛 奶類", "milk"), ("🥩 低脂肉", "protein_low"), 
                 ("🍖 中脂肉", "protein_mid"), ("🥦 總蔬菜", "veggie"), ("🍎 水果", "fruit"), ("🥑 油脂", "fat")]
for i, (label, key) in enumerate(display_items):
    current = st.session_state.daily[key]
    rem = GOALS.get(key, 0) - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

st.divider()

# --- 4. 蔬菜紀錄邏輯 (達成率導向) ---
st.subheader("🥬 蔬菜紀錄")
v_name = st.text_input("輸入蔬菜名稱 (例如：綠花椰、高麗菜、地瓜葉)")
v_w = st.number_input("重量 (g)", value=100.0)

if st.button("➕ 紀錄蔬菜"):
    servings = v_w / 100
    st.session_state.daily["veggie"] += servings
    
    # 判定是否為綠色蔬菜
    is_green = any(k in v_name for k in ["綠", "青", "菠", "地瓜葉", "芥藍", "苗", "空心", "龍鬚"])
    if is_green:
        st.session_state.veggie_green += servings
    st.rerun()

# --- 5. 數據結算 (關鍵：達成率邏輯) ---
st.divider()
st.subheader("📋 今日數據匯出")

# 修正：綠色蔬菜佔比 = (已攝取綠色份數 / 蔬菜目標 4 份) * 100
green_achievement = (st.session_state.veggie_green / VEG_GOAL) * 100

headers = ["日期", "總熱量", "主食份", "奶類份", "低脂肉", "中脂肉", "總蔬菜", "綠菜達成率", "水果份", "油脂份", "鹽份(g)", "飲水(ml)"]
data_list = [
    datetime.now().strftime("%Y/%m/%d"), 
    str(round(total_kcal)), 
    f"{st.session_state.daily['carbs']:.1f}", 
    f"{st.session_state.daily['milk']:.1f}", 
    f"{st.session_state.daily['protein_low']:.1f}", 
    f"{st.session_state.daily['protein_mid']:.1f}", 
    f"{st.session_state.daily['veggie']:.1f}", 
    f"{green_achievement:.1f}%",  # 這裡現在顯示的是相對於目標 4 份的達成率
    f"{st.session_state.daily['fruit']:.1f}", 
    f"{st.session_state.daily['fat']:.1f}", 
    f"{st.session_state.daily['salt']:.1f}", 
    str(round(st.session_state.water))
]

st.table([headers, data_list])

# 一鍵複製純數據 (Tab 分隔)
copy_text = "\t".join(data_list)
copy_js = f"""
    <button onclick="copyToClipboard()" style="width: 100%; padding: 15px; background-color: #28a745; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer;">📋 點擊一鍵複製數據 (直接貼入 Excel)</button>
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

if st.button("🔄 重置今日"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
