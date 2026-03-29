import streamlit as st

st.set_page_config(page_title="35% 終結者：主食快捷版", page_icon="🍚")

# --- 營養師專屬主食資料庫 ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0,
    "🌾 五穀混合米 (240g)": 315.0,
    "🍜 熟麵條 (300g)": 345.0,
    "✏️ 手動輸入其他": 0.0
}

# --- 基礎食材資料庫 (每克大卡) ---
base_kcal = {
    "櫛瓜": 0.17, "青菜": 0.2, "雞胸肉": 1.1, "雞肉": 1.6, "鮭魚": 2.1, "橄欖油": 9.0
}

st.error("📉 當前目標：內臟脂肪 18 | 穩定控糖")
st.title("⚖️ 精準飲食計算機")

# --- 第一區：主食快捷區 ---
st.subheader("1. 選擇主食 (營養師建議量)")
carb_choice = st.selectbox("今天的主食是？", list(dietitian_carbs.keys()))

if carb_choice == "✏️ 手動輸入其他":
    custom_carb = st.number_input("輸入主食熱量 (kcal)", min_value=0.0, value=0.0)
    carb_kcal = custom_carb
else:
    carb_kcal = dietitian_carbs[carb_choice]
    st.info(f"💡 已自動設定熱量：{carb_kcal} kcal")

# --- 第二區：配菜自由計算 ---
st.divider()
st.subheader("2. 紀錄配菜 (依重量與煮法)")

source = st.radio("配菜來源：", ["🏠 自煮", "🥡 外食 (+35% 隱形油)"])

col1, col2 = st.columns(2)
with col1:
    user_food = st.text_input("食材 (如：雞肉)", "櫛瓜")
with col2:
    user_method = st.selectbox("料理方式", ["水煮/清蒸", "滷/燉", "乾煎", "油炒", "油炸"])

user_weight = st.number_input("重量 (g)", min_value=0.0, value=100.0)

# 計算配菜熱量
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}
risk_mult = 1.35 if source == "🥡 外食 (+35% 隱形油)" else 1.0
side_kcal = base_kcal.get(user_food, 0.6) * method_map[user_method] * user_weight * risk_mult

# --- 第三區：總和 ---
st.divider()
total_all = carb_kcal + side_kcal
st.metric("🔥 本餐預估總熱量", f"{total_all:.1f} kcal")

if st.button("確認紀錄", use_container_width=True):
    st.success(f"紀錄成功！主食 {carb_kcal} + 配菜 {side_kcal:.1f} = {total_all:.1f} kcal")
    if carb_choice == "🌾 五穀混合米 (240g)":
        st.write("✨ 五穀米對降低內脂非常有幫助，繼續保持！")
