import streamlit as st
from datetime import datetime

# --- 1. 定義配額目標 (放在 BASE_KCAL 下方) ---
BASE_KCAL = 2710  
STAPLE_TOTAL_WEIGHT = 565.0   # 營養師給的總重上限 (g)
STAPLE_TOTAL_SERVINGS = 16.0  # 營養師給的總份數上限 (份)

# 自動換算出 1 份是多少公克 (35.31g)
GRAMS_PER_SERVING = STAPLE_TOTAL_WEIGHT / STAPLE_TOTAL_SERVINGS 

GOALS = {
    "carbs": STAPLE_TOTAL_SERVINGS, # 直接對齊 16 份
    "milk": 3.0, "protein_low": 7.0, 
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
    "白米飯": GRAMS_PER_SERVING,       # 自動對齊 35.31g
    "五穀米/混合米": GRAMS_PER_SERVING, # 自動對齊 35.31g
    "煮過白麵條": GRAMS_PER_SERVING,    # 自動對齊 35.31g
    "Tommi 炭香燒肉米漢堡": "TOMMI_BBQ",
    "Tommi 壽喜燒肉米漢堡": "TOMMI_SUKI",
    "其他主食/自定義": "CUSTOM"
}

MEAT_DB = {
    "雞胸肉": "low", "雞腿肉(去皮)": "low", "牛腱": "low", "里肌肉(豬)": "low", "豆腐": "low",
    "鱈魚": "low", "雞蛋": "mid", "鮭魚": "mid", "梅花豬": "mid", "梅花牛": "mid", 
    "雞腿肉(帶皮)": "mid", "豬絞肉": "mid", "牛肋條": "high", "肋眼牛排": "high", "豬五花": "high"
}

GREEN_LIST = ["綠花椰", "菠菜", "地瓜葉", "空心菜", "青江菜", "芥藍"]
OTHER_VEG_LIST = ["櫛瓜", "茄子", "高麗菜", "白花椰", "娃娃菜", "絲瓜", "洋蔥", "雪白菇", "鴻禧菇"]

# --- 3. 初始化 Session State ---
if 'daily' not in st.session_state:
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0  
    st.session_state.water = 0.0

# --- 4. 網頁配置與儀表板 ---
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
    goal = GOALS.get(key, 0)
    rem = goal - current
    cols[i].metric(label, f"剩 {rem:.1f} 份", delta=f"{current:.1f} 已吃")

# --- 5. 紀錄輸入區 ---
st.divider()
tabs = st.tabs(["🍚 主食", "🥛 奶類", "🥩 肉類", "🥬 蔬菜", "🍎 其他/油/鹽", "💧 飲水"])

# --- Tab 0: 主食 ---
with tabs[0]: 
    st.subheader("🍚 主食精準紀錄")
    food_name = st.text_input("主食名稱", value="白米飯")
    input_weight = st.number_input("輸入食物重量 (g)", min_value=0.0, step=1.0)

    if input_weight > 0:
        # 1. 計算份數
        calculated_servings = input_weight / GRAMS_PER_SERVING
        # 2. 計算熱量 (1份主食 = 70大卡)
        calculated_kcal = calculated_servings * 70
        
        st.info(f"💡 系統換算：{input_weight}g = {calculated_servings:.2f} 份 | 預計熱量：{calculated_kcal:.1f} kcal")

        if st.button("➕ 扣除主食配額"):
            # 扣除主食份數
            st.session_state.daily["carbs"] += calculated_servings
            st.success(f"已從 16 份額度中扣除 {calculated_servings:.2f} 份")
            st.rerun()

# --- Tab 1: 奶類 ---
with tabs[1]:
    m_opt = st.radio("選擇類型", ["LP33 / AB 優酪乳 (預設)", "其他奶類/蛋白質飲品"], horizontal=True)
    if m_opt == "LP33 / AB 優酪乳 (預設)":
        m_ml = st.number_input("飲用量 (ml)", value=240.0, step=10.0, key="default_milk")
        if st.button("➕ 紀錄預設奶類"):
            st.session_state.daily["milk"] += (m_ml / 240); st.rerun()
    else:
        m_name = st.text_input("輸入飲品名稱 (如：豆漿、燕麥奶、鮮奶)")
        m_ml = st.number_input("飲用量 (ml)", value=240.0, step=10.0, key="custom_milk")
        if st.button("➕ 分析並紀錄"):
            if "豆漿" in m_name:
                st.session_state.daily["protein_low"] += (m_ml / 240)
            elif "燕麥奶" in m_name:
                st.session_state.daily["carbs"] += (m_ml / 240) * 2
            else:
                st.session_state.daily["milk"] += (m_ml / 240)
            st.rerun()

# --- Tab 2: 肉類 ---
with tabs[2]:
    p_sel = st.selectbox("選擇肉類/蛋白質", list(MEAT_DB.keys()) + ["其他肉類/蛋白質選項"])
    if p_sel == "其他肉類/蛋白質選項":
        p_name = st.text_input("輸入名稱 (如：黑豆、板豆腐、毛豆)")
        p_w = st.number_input("重量 (g)", value=35.0)
        if st.button("➕ 智慧紀錄蛋白質"):
            low_fat = ["黑豆", "毛豆", "板豆腐", "豆腐", "雞胸", "里肌"]
            mid_fat = ["傳統豆腐", "蛋", "鮭魚"]
            if any(k in p_name for k in low_fat): st.session_state.daily["protein_low"] += p_w/35
            elif any(k in p_name for k in mid_fat): st.session_state.daily["protein_mid"] += p_w/35
            else: st.session_state.daily["protein_high"] += p_w/35
            st.rerun()
    else:
        p_w = st.number_input("重量 (g)", value=35.0, key="fixed_p_w")
        meth = st.selectbox("烹調", ["水煮", "氣炸", "油炒", "油炸"])
        p_out = st.checkbox("外食肉類 (+1.5 油脂)")
        if st.button("➕ 紀錄固定肉類"):
            fat_t = MEAT_DB[p_sel]
            st.session_state.daily[f"protein_{fat_t}"] += p_w/35
            f_map = {"水煮":0, "氣炸":0.5, "油炒":1, "油炸":3.5}
            st.session_state.daily["fat"] += f_map[meth] + (1.5 if p_out else 0)
            st.rerun()

# --- Tab 3: 蔬菜 (新增烹調與調味料邏輯) ---
with tabs[3]:
    v_n = st.selectbox("種類", GREEN_LIST + OTHER_VEG_LIST)
    v_w = st.number_input("重量 (g)", value=100.0, step=50.0, key="v_weight")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        v_cook = st.selectbox("選單1(料理方式)", ["清燙", "油炒"])
    with col_v2:
        v_sauce = st.selectbox("選單2(調味料)", ["無", "新東陽肉醬", "油蔥"])
    
    sauce_g = 0.0
    if v_sauce in ["新東陽肉醬", "油蔥"]:
        sauce_g = st.number_input(f"{v_sauce} 重量 (g)", min_value=0.0, step=5.0)

    if st.button("➕ 紀錄蔬菜"):
        # 1. 基礎蔬菜份數
        serv = v_w / 100
        st.session_state.daily["veggie"] += serv
        if v_n in GREEN_LIST: st.session_state.veggie_green += serv
        
        # 2. 料理方式油脂 (油炒加 1 份)
        if v_cook == "油炒":
            st.session_state.daily["fat"] += 1.0
            
        # 3. 調味料油脂計算 (換算成份數，1份=5g)
        if v_sauce == "新東陽肉醬":
            # 肉醬油脂率約 20% -> sauce_g * 0.2 / 5
            st.session_state.daily["fat"] += (sauce_g * 0.2) / 5
        elif v_sauce == "油蔥":
            # 油蔥油脂率約 60% -> sauce_g * 0.6 / 5
            st.session_state.daily["fat"] += (sauce_g * 0.6) / 5
            
        st.rerun()

# --- Tab 4: 其他 ---
with tabs[4]:
    col1, col2, col3 = st.columns(3)
    with col1:
        fa_g = st.number_input("手動油脂 (g)", step=1.0)
        if st.button("記油"): st.session_state.daily["fat"] += fa_g / 5; st.rerun()
    with col2:
        fr = st.number_input("水果(g)", step=10.0)
        if st.button("記果"): st.session_state.daily["fruit"] += fr/100; st.rerun()
    with col3:
        sa = st.number_input("鹽巴(g)", step=0.5)
        if st.button("記鹽"): st.session_state.daily["salt"] += sa; st.rerun()

# --- Tab 5: 飲水 (新增熱量即時計算顯示) ---
with tabs[5]:
    w_type = st.radio("類型", ["純水", "飲料"], horizontal=True)
    
    if w_type == "純水":
        w_val = st.number_input("水量 (ml)", value=250.0, key="pure_water")
        if st.button("記水"): 
            st.session_state.water += w_val
            st.rerun()
    else:
        st.info("💡 系統將根據關鍵字自動分析成分與熱量 (範例：五十嵐珍珠奶茶無糖)")
        drink_name = st.text_input("輸入飲料名稱", key="d_name_input")
        drink_ml = st.number_input("飲用量 (ml)", value=700.0, step=50.0)
        
        if st.button("🥤 紀錄飲料"):
            # 1. 份數增量初始化
            d_carbs = 0.0  
            d_fat = 0.0    
            d_milk = 0.0   
            
            # 容量倍率 (以 700ml 為 1 單位基準)
            ratio = drink_ml / 700
            
            # 2. 判定基底 (奶精或鮮奶)
            if "奶茶" in drink_name:
                d_fat += 3.0 * ratio      # 奶精提供油脂
                d_carbs += 1.5 * ratio    # 奶精內的碳水
            elif any(k in drink_name for k in ["拿鐵", "鮮奶茶", "歐蕾"]):
                d_milk += 1.5 * ratio     # 鮮奶提供奶類份數
            
            # 3. 判定配料 (澱粉量)
            if any(k in drink_name for k in ["珍珠", "波霸", "粉圓", "混珠"]):
                d_carbs += 4.0 * ratio
            
            # 4. 判定甜度 (砂糖量)
            if "全糖" in drink_name: d_carbs += 3.0 * ratio
            elif "半糖" in drink_name: d_carbs += 1.5 * ratio
            elif "微糖" in drink_name: d_carbs += 0.8 * ratio
            elif "無糖" in drink_name: d_carbs += 0.0
            
            # --- 關鍵：計算這杯飲料的即時熱量 ---
            # 利用你定義的 KCAL_MAP: carbs=70, milk=150, fat=45
            this_drink_kcal = (d_carbs * 70) + (d_milk * 150) + (d_fat * 45)
            
            # 寫入系統狀態
            st.session_state.daily["carbs"] += d_carbs
            st.session_state.daily["fat"] += d_fat
            st.session_state.daily["milk"] += d_milk
            st.session_state.water += drink_ml
            
            # 彈出提示顯示計算結果
            st.success(f"✅ 已紀錄！這杯『{drink_name}』估計熱量為：{this_drink_kcal:.0f} kcal")
            st.info(f"拆解份數：主食 {d_carbs:.1f} | 奶類 {d_milk:.1f} | 油脂 {d_fat:.1f}")
            
            # 延遲一下讓你看清楚熱量再刷新
            import time
            time.sleep(2)
            st.rerun()

# --- 6. 結算匯出 ---
st.divider()
res_row = [datetime.now().strftime("%Y/%m/%d"), str(round(total_kcal)), 
           f"{st.session_state.daily['carbs']:.1f}", f"{st.session_state.daily['milk']:.1f}", 
           f"{st.session_state.daily['protein_low']:.1f}", f"{st.session_state.daily['protein_mid']:.1f}", 
           f"{st.session_state.daily['veggie']:.1f}", f"{(st.session_state.veggie_green / 4.0 * 100):.1f}%", 
           f"{st.session_state.daily['fruit']:.1f}", f"{st.session_state.daily['fat']:.1f}", 
           f"{st.session_state.daily['salt']:.1f}", str(round(st.session_state.water))]
st.code("\t".join(res_row))

if st.button("🔄 重置今日數據"):
    st.session_state.daily = {k: 0.0 for k in KCAL_MAP.keys()}
    st.session_state.veggie_green = 0.0; st.session_state.water = 0.0; st.rerun()
