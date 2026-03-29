import streamlit as st

st.set_page_config(page_title="35% 終結者：自由紀錄版", page_icon="⚖️")

# --- 核心邏輯：熱量估算引擎 ---
# 基礎食材每克熱量 (公認標準)
base_kcal = {
    "白飯": 1.4, "糙米飯": 1.1, "雞胸肉": 1.1, "雞腿": 1.6, 
    "鮭魚": 2.1, "雞蛋": 1.4, "青菜": 0.15, "牛肉": 2.5,
    "豬肉": 2.8, "橄欖油": 9.0, "地瓜": 1.2
}

# 料理方式加權 (額外增加的油脂/熱量係數)
method_weight = {
    "水煮": 1.0, "清蒸": 1.0, "滷": 1.05, 
    "氣炸": 1.1, "乾煎": 1.2, "油炒": 1.3, "油炸": 1.6
}

st.error("📉 目標：內臟脂肪 18 -> 穩定下降")
st.title("⚖️ 自由飲食計算機")

# --- 第一區：自由輸入 ---
col1, col2 = st.columns(2)

with col1:
    user_food = st.text_input("1. 輸入食材 (例如：雞腿)", "雞腿")
with col2:
    user_method = st.selectbox("2. 料理方式", list(method_weight.keys()))

user_weight = st.number_input("3. 輸入重量 (克 g)", min_value=0.0, value=100.0, step=10.0)

# --- 第二區：智慧計算 ---
# 判斷食材係數，如果不在資料庫，預設為 1.5 (一般肉類平均)
found_base = base_kcal.get(user_food, 1.5)
weight_factor = method_weight.get(user_method, 1.0)

# 最終計算
final_rate = found_base * weight_factor
total_kcal = user_weight * final_rate

# --- 第三區：結果顯示 ---
st.divider()
st.subheader("計算結果")

c1, c2, c3 = st.columns(3)
c1.metric("食材基礎", f"{found_base} kcal/g")
c2.metric("方式加成", f"x{weight_factor}")
c3.metric("總熱量", f"{total_kcal:.1f} kcal")

if st.button("確認紀錄此餐", use_container_width=True):
    st.balloons()
    st.success(f"已紀錄：{user_method}{user_food} {user_weight}g，共 {total_kcal:.1f} 大卡！")
    
    # 針對內脂 18 的警語
    if weight_factor >= 1.3:
        st.warning("🚨 警告：這種料理方式油脂過高，不利於降低內臟脂肪！")
    else:
        st.info("✅ 優質選擇：清淡料理是內脂的剋星。")

# --- 底部工具：手掌估算參考 ---
with st.expander("💡 沒秤在身邊？外食克數估計法"):
    st.write("""
    - **一個拳頭大的飯**：約 200g
    - **一個掌心的肉**：約 100g (厚 1cm)
    - **兩手捧滿的生青菜**：約 100g
    - **超商雞胸肉**：一包約 120g - 150g
    """)
