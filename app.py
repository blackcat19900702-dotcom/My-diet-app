import streamlit as st

st.set_page_config(page_title="35% 終結者：精準版", page_icon="⚖️")

# --- 修正後的精準資料庫 (每克大卡) ---
base_kcal = {
    "櫛瓜": 0.2, "青菜": 0.15, "高麗菜": 0.25, "花椰菜": 0.3, # 蔬菜類
    "白飯": 1.4, "地瓜": 1.2, "馬鈴薯": 0.8,              # 澱粉類
    "雞胸肉": 1.1, "雞腿": 1.6, "鮭魚": 2.1, "牛肉": 2.5,  # 蛋白質類
    "雞蛋": 1.4, "豆腐": 0.8, "優酪乳": 0.9, "橄欖油": 9.0  # 其他
}

# 料理方式加權
method_weight = {
    "水煮/清蒸": 1.0, "滷": 1.05, "氣炸": 1.1, 
    "乾煎": 1.2, "油炒": 1.3, "油炸": 1.7
}

st.error("📉 目標：內臟脂肪 18 -> 嚴格控管油脂")
st.title("⚖️ 精準飲食計算機 (修正版)")

col1, col2 = st.columns(2)
with col1:
    user_food = st.text_input("1. 輸入食材", "櫛瓜")
with col2:
    user_method = st.selectbox("2. 料理方式", list(method_weight.keys()))

user_weight = st.number_input("3. 輸入重量 (克 g)", min_value=0.0, value=100.0, step=10.0)

# --- 智慧判斷邏輯 (修正預設值) ---
# 如果找不到食材，預設給 0.6 (大約是瘦肉與蔬菜的平均)，避免跳到 1.5 甚至更高
found_base = base_kcal.get(user_food, 0.6) 
weight_factor = method_weight.get(user_method, 1.0)

total_kcal = user_weight * found_base * weight_factor

st.divider()
st.subheader("計算結果")

c1, c2, c3 = st.columns(3)
c1.metric("食材基礎", f"{found_base} kcal/g")
c2.metric("方式加成", f"x{weight_factor}")
c3.metric("總熱量", f"{total_kcal:.1f} kcal")

if st.button("確認紀錄", use_container_width=True):
    st.success(f"已紀錄：{user_method}{user_food} {user_weight}g，共 {total_kcal:.1f} kcal")
    if found_base < 0.4:
        st.info("🥦 這是優質的低卡蔬菜，對降低內脂非常有幫助！")
