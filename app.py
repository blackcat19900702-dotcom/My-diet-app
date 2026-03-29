import streamlit as st

st.set_page_config(page_title="內脂終結者：部位精準版", page_icon="🍗")

# --- 核心資料庫 ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0, "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0, "🚫 不吃主食 / 自定義": 0.0
}

# 肉類部位資料庫
meat_parts = {
    "雞肉": ["雞胸肉", "雞腿肉", "雞翅"],
    "豬肉": ["里肌肉(瘦)", "五花肉(肥)", "豬絞肉"],
    "牛肉": ["菲力(瘦)", "牛腩(肥)", "牛腱"],
    "其他蛋白質": ["鮭魚", "鱈魚", "雞蛋", "豆腐"]
}

# 基礎熱量係數 (每克)
base_kcal_map = {
    "雞胸肉": 1.1, "雞翅": 2.1, "里肌肉(瘦)": 1.8, "五花肉(肥)": 3.6,
    "豬絞肉": 2.5, "菲力(瘦)": 1.8, "牛腩(肥)": 3.3, "牛腱": 1.2,
    "鮭魚": 2.1, "鱈魚": 1.0, "雞蛋": 1.4, "豆腐": 0.8
}

db_veggie = {"櫛瓜": 0.17, "茄子": 0.25, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3}
db_sauce = {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6, "辣椒醬": 1.5}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "氣炸/烤": 1.15, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

if 'meal_list' not in st.session_state:
    st.session_state.meal_list = []

st.error("📉 當前目標：內臟脂肪 18 | 嚴控動物性脂肪攝取")
st.title("⚖️ 旗艦級飲食紀錄器 (部位精準版)")

# --- 第一區：主食 ---
st.header("1. 主食選擇")
carb_choice = st.selectbox("今日主食：", list(dietitian_carbs.keys()))
carb_kcal = dietitian_carbs[carb_choice]

# --- 第二區：來源 ---
st.divider()
source = st.radio("餐點來源：", ["🏠 家中自煮", "🥡 外食 (+35% 隱形油)"])
risk_mult = 1.35 if source == "🥡 外食 (+35% 隱形油)" else 1.0

# --- 第三區：添加食材 ---
st.header("2. 添加詳細食材")
cat = st.selectbox("選擇類別：", ["🥩 肉類/蛋白質", "🥦 青菜/纖維", "🧂 調味料/醬料", "🍎 水果/飲料"])

# 初始化本筆紀錄的變數
f_final_name = ""
base_k = 0.6
m_factor = 1.0

if cat == "🥩 肉類/蛋白質":
    c1, c2 = st.columns(2)
    with c1:
        m_type = st.selectbox("肉類種類", list(meat_parts.keys()))
    with c2:
        part = st.selectbox("選擇部位", meat_parts[m_type])
    
    # 雞腿肉專屬邏輯
    skin_factor = 1.0
    if part == "雞腿肉":
        skin_option = st.radio("處理方式：", ["🍗 帶皮 (脂肪較多)", "✂️ 去皮 (降內脂首選)"], horizontal=True)
        if "去皮" in skin_option:
            base_k = 1.2
            f_final_name = "雞腿肉(去皮)"
        else:
            base_k = 1.9
            f_final_name = "雞腿肉(帶皮)"
    else:
        base_k = base_kcal_map.get(part, 1.5)
        f_final_name = part

    f_method = st.selectbox("料理方式", list(method_map.keys()))
    m_factor = method_map[f_method]

elif cat == "🥦 青菜/纖維":
    c1, c2 = st.columns(2)
    with c1:
        f_final_name = st.selectbox("選擇青菜", list(db_veggie.keys()) + ["手動輸入"])
        if f_final_name == "手動輸入": f_final_name = st.text_input("輸入菜名")
    with c2:
        f_method = st.selectbox("料理方式", list(method_map.keys()))
    base_k = db_veggie.get(f_final_name, 0.2)
    m_factor = method_map[f_method]

else: # 醬料或水果
    f_final_name = st.text_input("名稱")
    base_k = db_sauce.get(f_final_name, 3.0 if cat == "🧂 調味料/醬料" else 0.5)
    f_method = "直接添加"

f_weight = st.number_input("重量 (g/ml)", min_value=0.0, step=1.0)

if st.button("➕ 加入此項到清單"):
    kcal = base_k * m_factor * f_weight * risk_mult
    st.session_state.meal_list.append({
        "分類": cat, "名稱": f"{f_final_name}({f_method})", "重量": f"{f_weight}g", "熱量": round(kcal, 1)
    })
    st.toast(f"已加入 {f_final_name}")

# --- 第四區：結算 ---
st.divider()
if st.session_state.meal_list:
    for i, item in enumerate(st.session_state.meal_list):
        st.write(f"{i+1}. {item['分類']} | {item['名稱']} | {item['重量']} -> **{item['熱量']} kcal**")
    
    side_total = sum(item['熱量'] for item in st.session_state.meal_list)
    final_total = carb_kcal + side_total

    if st.button("🗑️ 清空紀錄"): 
        st.session_state.meal_list = []; st.rerun()

    st.subheader("📊 總結報告")
    st.metric("🔥 這一餐總預估", f"{final_total:.1f} kcal")
    
    if any("帶皮" in item['名稱'] for item in st.session_state.meal_list):
        st.warning("⚠️ 內脂 18 警示：帶皮肉類飽和脂肪較高，建議下次嘗試去皮部位。")

    if st.button("✅ 儲存此餐紀錄", use_container_width=True):
        st.balloons(); st.success("紀錄已成功更新至您的健康日誌")
