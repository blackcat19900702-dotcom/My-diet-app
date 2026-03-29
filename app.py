import streamlit as st

st.set_page_config(page_title="內脂終結者：調味控管版", page_icon="🧂")

# --- 1. 資料庫設定 ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0,
    "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0,
    "🚫 不吃主食 / 自定義": 0.0
}

# 基礎熱量庫 (食材原型)
protein_db = {"雞肉": 1.6, "鮭魚": 2.1, "牛肉": 2.5, "雞蛋": 1.4, "豆腐": 0.8}
veggie_db = {"櫛瓜": 0.17, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3, "茄子": 0.25}

# 調味料資料庫 (熱量密度通常較高)
sauce_db = {
    "新東陽肉醬": 2.9,   # 100g 約 290kcal
    "沙拉油/橄欖油": 9.0,
    "沙拉醬/蛋黃醬": 6.5,
    "醬油/烏醋": 0.6,
    "辣椒醬/豆瓣醬": 1.5
}

method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

# 初始化清單
if 'meal_list' not in st.session_state:
    st.session_state.meal_list = []

st.error("📉 當前狀態：內臟脂肪 18 | 嚴控加工醬料與隱形油脂")
st.title("⚖️ 精準飲食紀錄器 (五區版)")

# --- 第一區：主食 ---
st.header("1. 選擇主食")
carb_choice = st.selectbox("主食選項：", list(dietitian_carbs.keys()))
carb_kcal = dietitian_carbs[carb_choice]

# --- 第二區：來源加權 ---
st.divider()
source = st.radio("餐點來源：", ["🏠 家中自煮", "🥡 外食 (+35% 隱形油)"])
risk_mult = 1.35 if source == "🥡 外食 (+35% 隱形油)" else 1.0

# --- 第三區：內容添加區 ---
st.header("2. 添加詳細食材")
cat = st.selectbox("選擇類別：", ["🥩 肉類/蛋白質", "🥦 青菜/纖維", "🧂 調味料/醬料", "🍎 水果/飲料"])

col1, col2 = st.columns(2)
with col1:
    f_name = st.text_input("食材/醬料名稱", "")
with col2:
    if cat in ["🥩 肉類/蛋白質", "🥦 青菜/纖維"]:
        f_method = st.selectbox("料理方式", list(method_map.keys()))
        m_factor = method_map[f_method]
    else:
        f_method = "直接添加/飲用"
        m_factor = 1.0

f_weight = st.number_input("重量 (g) / 容量 (ml)", min_value=0.0, value=0.0, step=1.0)

if st.button("➕ 加入清單"):
    # 智慧判斷基礎熱量
    if cat == "🥩 肉類/蛋白質":
        base = protein_db.get(f_name, 1.5)
    elif cat == "🥦 青菜/纖維":
        base = veggie_db.get(f_name, 0.2)
    elif cat == "🧂 調味料/醬料":
        base = sauce_db.get(f_name, 3.0) # 醬料若沒在清單，預設給較高的 3.0
    else: # 水果飲料
        base = 0.5
    
    kcal = base * m_factor * f_weight * risk_mult
    
    st.session_state.meal_list.append({
        "分類": cat,
        "名稱": f"{f_name}({f_method})",
        "重量": f"{f_weight}g",
        "熱量": round(kcal, 1)
    })
    st.toast(f"已加入 {f_name}")

# --- 第四區：清單結算 ---
st.divider()
st.header("📋 本餐紀錄明細")

if st.session_state.meal_list:
    for item in st.session_state.meal_list:
        st.write(f"{item['分類']} | {item['名稱']} | {item['重量']} -> **{item['熱量']} kcal**")
    
    if st.button("🗑️ 全部清空"):
        st.session_state.meal_list = []
        st.rerun()

    side_total = sum(item['熱量'] for item in st.session_state.meal_list)
    final_total = carb_kcal + side_total

    st.divider()
    st.metric("🔥 這一餐總熱量", f"{final_total:.1f} kcal")
    
    # 調味料警告邏輯
    sauce_kcal = sum(item['熱量'] for item in st.session_state.meal_list if item['分類'] == "🧂 調味料/醬料")
    if sauce_kcal > 100:
        st.warning(f"⚠️ 警示：本餐醬料熱量高達 {sauce_kcal} kcal，內脂 18 應減少加工醬料攝取！")
else:
    st.info("請開始添加食材...")    f_name = st.text_input("食材名稱", "雞肉" if cat == "🥩 蛋白質/肉類" else "青菜")
with col2:
    f_method = st.selectbox("料理方式", list(method_map.keys()))

f_weight = st.number_input("重量 (g)", min_value=0.0, value=100.0, step=10.0)

if st.button("➕ 加入這項食材"):
    # 根據類別抓取基礎熱量
    db = protein_db if cat == "🥩 蛋白質/肉類" else veggie_db
    base = db.get(f_name, 1.5 if cat == "🥩 蛋白質/肉類" else 0.2)
    kcal = base * method_map[f_method] * f_weight * risk_mult
    
    # 存入清單
    st.session_state.meal_list.append({
        "名稱": f"{cat} - {f_name}({f_method})",
        "重量": f"{f_weight}g",
        "熱量": round(kcal, 1)
    })
    st.toast(f"已加入 {f_name}")

# --- 第三區：本餐清單與總結 ---
st.divider()
st.header("📋 本餐清單")

if st.session_state.meal_list:
    for item in st.session_state.meal_list:
        st.write(f"· {item['名稱']} | {item['重量']} -> **{item['熱量']} kcal**")
    
    if st.button("🗑️ 清空重來"):
        st.session_state.meal_list = []
        st.rerun()
else:
    st.info("目前還沒有加入配菜喔！")

# 總和計算
side_total = sum(item['熱量'] for item in st.session_state.meal_list)
final_total = dietitian_carbs[carb_choice] + side_total

st.divider()
c1, c2 = st.columns(2)
c1.metric("主食熱量", f"{dietitian_carbs[carb_choice]} kcal")
c2.metric("配菜總計", f"{side_total:.1f} kcal")
st.metric("🔥 這一餐總共攝取", f"{final_total:.1f} kcal")

if st.button("✅ 確認這就是我吃的所有東西", use_container_width=True):
    st.balloons()
    st.success(f"紀錄完成！今日內脂戰鬥力 +1")
