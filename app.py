import streamlit as st

st.set_page_config(page_title="內脂終結者：多食材版", page_icon="🥗")

# --- 資料庫設定 ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0,
    "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0,
    "🚫 不吃主食": 0.0
}
protein_db = {"雞胸肉": 1.1, "雞肉": 1.6, "鮭魚": 2.1, "牛肉": 2.5, "雞蛋": 1.4, "豆腐": 0.8}
veggie_db = {"櫛瓜": 0.17, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3, "地瓜葉": 0.25}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

# 初始化暫存清單 (Session State)
if 'meal_list' not in st.session_state:
    st.session_state.meal_list = []

st.error("📉 內臟脂肪 18 嚴格監控中 | 多樣化飲食紀錄")
st.title("⚖️ 精準飲食紀錄器")

# --- 第一區：主食 ---
st.header("1. 選擇主食")
carb_choice = st.selectbox("主食選項：", list(dietitian_carbs.keys()))

# --- 第二區：添加食材 (肉/菜) ---
st.divider()
st.header("2. 添加配菜 (可多次添加)")

source = st.radio("來源：", ["🏠 自煮", "🥡 外食 (+35%)"])
risk_mult = 1.35 if source == "🥡 外食 (+35%)" else 1.0

cat = st.selectbox("食材類別：", ["🥩 蛋白質/肉類", "🥦 青菜/纖維"])
col1, col2 = st.columns(2)
with col1:
    f_name = st.text_input("食材名稱", "雞肉" if cat == "🥩 蛋白質/肉類" else "青菜")
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
