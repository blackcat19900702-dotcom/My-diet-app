import streamlit as st
import urllib.parse
from datetime import datetime, timedelta

st.set_page_config(page_title="內脂終結者：長期數據版", page_icon="📈", layout="centered")

# --- 1. 核心資料庫 (牛肉部位、雞肉、醬料維持精準版) ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0, "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0, "🚫 不吃主食 / 自定義": 0.0
}
meat_parts = {
    "牛肉": ["和尚頭(極瘦)", "嫩肩里肌(板腱)", "梅花牛", "肋眼(沙朗)", "牛肋條", "牛小排", "牛腱"],
    "雞肉": ["雞胸肉", "雞腿肉", "雞翅"],
    "豬肉": ["里肌肉(瘦)", "五花肉(肥)", "梅花豬", "豬絞肉"],
    "其他蛋白質": ["鮭魚", "鱈魚", "雞蛋", "豆腐"]
}
base_kcal_map = {
    "和尚頭(極瘦)": 1.2, "嫩肩里肌(板腱)": 1.4, "梅花牛": 2.0, "肋眼(沙朗)": 2.9, "牛肋條": 3.3, "牛小排": 3.8, "牛腱": 1.2,
    "雞胸肉": 1.1, "雞翅": 2.1, "里肌肉(瘦)": 1.8, "五花肉(肥)": 3.6, "梅花豬": 2.3, "豬絞肉": 2.5,
    "鮭魚": 2.1, "鱈魚": 1.0, "雞蛋": 1.4, "豆腐": 0.8
}
db_veggie = {"櫛瓜": 0.17, "茄子": 0.25, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3}
db_sauce = {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "氣炸/烤": 1.15, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

# --- 2. 數據存儲邏輯 ---
if 'daily_total_kcal' not in st.session_state:
    st.session_state.daily_total_kcal = 0.0

# --- 3. 身體組成與日期 (手動/自動並行) ---
st.error("📉 內臟脂肪 18 減標計畫 | 長期數據監測")

with st.container(border=True):
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        # 自動判定日期，但允許手動修改
        record_date = st.date_input("記錄日期 (預設為當天)", datetime.now())
    with col_d2:
        if st.button("🔄 重置今日計算"):
            st.session_state.daily_total_kcal = 0.0
            st.rerun()

with st.expander("📊 身體量測與代謝指標 (Excel 欄位)", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        weight = st.number_input("體重 (kg)", value=99.0, step=0.1)
        body_fat = st.number_input("體脂 (%)", value=35.0, step=0.1)
        sleep = st.number_input("睡眠 (hr)", value=7.0, step=0.5)
    with c2:
        visceral = st.number_input("內臟脂肪", value=18.0, step=0.5)
        waist = st.number_input("腰圍 (cm)", value=100.0, step=0.1)
        water = st.number_input("飲水 (ml)", value=0, step=250)
    with c3:
        hip = st.number_input("臀圍 (cm)", value=110.0, step=0.1)
        steps = st.number_input("步數", value=0, step=500)
        st.metric("累計熱量", f"{st.session_state.daily_total_kcal:.1f} kcal")

# --- 4. 飲食錄入 (累計模式) ---
st.title("⚖️ 精準飲食紀錄")

with st.container(border=True):
    carb_choice = st.selectbox("1. 主食：", list(dietitian_carbs.keys()))
    source = st.radio("2. 來源：", ["🏠 自煮", "🥡 外食(+35%)"], horizontal=True)
    risk_mult = 1.35 if "外食" in source else 1.0
    
    cat = st.selectbox("3. 食材類別：", ["🥩 肉類/蛋白質", "🥦 青菜/纖維", "🧂 醬料/其他"])
    
    # 根據類別彈出對應選項 (省略重複的詳細部位代碼以簡化展示，實作時請保留之前的部位選單)
    # 此處假設已選好 base_k, m_factor, f_weight ... (同前次代碼)
    # [此處插入之前的肉類部位與料理方式邏輯]
    
    if st.button("➕ 累計此筆到今日熱量"):
        # 這裡會計算出這筆的 kcal，並加到 session_state
        # kcal = base_k * m_factor * f_weight * risk_mult
        # st.session_state.daily_total_kcal += kcal
        st.toast("已計入今日總熱量")

# --- 5. 一鍵同步至 Google Excel ---
st.divider()
st.header("📤 數據同步中心")

# Google 表單網址 (請替換為你的預填連結)
form_url = "https://docs.google.com/forms/d/e/你的表單ID/viewform?"

params = {
    "entry.1": record_date.strftime('%Y-%m-%d'),
    "entry.2": weight,
    "entry.3": body_fat,
    "entry.4": visceral,
    "entry.5": waist,
    "entry.6": hip,
    "entry.7": sleep,
    "entry.8": water,
    "entry.9": steps,
    "entry.10": f"{st.session_state.daily_total_kcal:.1f}"
}

export_link = form_url + urllib.parse.urlencode(params)

st.link_button("🚀 同步今日數據至 Excel", export_link, use_container_width=True)
st.caption("💡 點擊後會開啟表單並填好所有『每日指標』，確認無誤按提交即可。")
