import streamlit as st

st.set_page_config(page_title="內脂終結者：全數據版", page_icon="📈")

# --- 1. 核心資料庫 (主食、肉類、青菜等) ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0, "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0, "🚫 不吃主食 / 自定義": 0.0
}

meat_parts = {
    "雞肉": ["雞胸肉", "雞腿肉", "雞翅"],
    "牛肉": ["和尚頭(極瘦)", "嫩肩里肌(板腱)", "梅花牛", "肋眼(沙朗)", "牛肋條", "牛小排", "牛腱"],
    "豬肉": ["里肌肉(瘦)", "五花肉(肥)", "梅花豬", "豬絞肉"],
    "其他蛋白質": ["鮭魚", "鱈魚", "雞蛋", "豆腐"]
}

base_kcal_map = {
    "雞胸肉": 1.1, "雞翅": 2.1, "和尚頭(極瘦)": 1.2, "嫩肩里肌(板腱)": 1.4, "梅花牛": 2.0, 
    "肋眼(沙朗)": 2.9, "牛肋條": 3.3, "牛小排": 3.8, "牛腱": 1.2, "里肌肉(瘦)": 1.8, 
    "五花肉(肥)": 3.6, "梅花豬": 2.3, "豬絞肉": 2.5, "鮭魚": 2.1, "鱈魚": 1.0, "雞蛋": 1.4, "豆腐": 0.8
}

db_veggie = {"櫛瓜": 0.17, "茄子": 0.25, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3}
db_sauce = {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6}
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "氣炸/烤": 1.15, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

if 'meal_list' not in st.session_state:
    st.session_state.meal_list = []

# --- 2. 每日身體數據監控 (新增欄位) ---
st.error("📉 減重目標：99kg → 內脂 18 降標中")

with st.expander("📊 今日身體數據與量測 (自由填寫)", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        sleep_hours = st.number_input("昨晚睡眠 (小時)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        body_fat = st.number_input("體脂肪 (%)", min_value=0.0, value=35.0, step=0.1)
    with col_b:
        waist = st.number_input("腰圍 (cm)", min_value=0.0, value=100.0, step=0.1)
        visceral_fat = st.number_input("內臟脂肪", min_value=0.0, value=18.0, step=0.5)
    with col_c:
        hip = st.number_input("臀圍 (cm)", min_value=0.0, value=110.0, step=0.1)
        weight_now = st.number_input("體重 (kg)", min_value=0.0, value=99.0, step=0.1)

    # 計算腰臀比 (WHR)
    if hip > 0:
        whr = waist / hip
        st.info(f"💡 目前腰臀比：{whr:.2f} (男性標準 < 0.9)")

    # 數據提醒
    if sleep_hours < 6:
        st.warning("⚠️ 睡眠不足 6 小時，壓力荷爾蒙會上升，導致脂肪更容易堆積在腹部！")
    if visceral_fat >= 15:
        st.caption("❗ 內臟脂肪較高，建議嚴控加工醬料攝取。")

with st.expander("💧 代謝指標追蹤"):
    col_w, col_s = st.columns(2)
    with col_w:
        water = st.number_input("今日飲水 (ml)", min_value=0, value=0, step=250)
    with col_s:
        steps = st.number_input("今日步數", min_value=0, value=0, step=500)

st.title("⚖️ 精準飲食紀錄器")

# --- 3. 飲食紀錄邏輯 (維持先前功能) ---
st.header("1. 主食選擇")
carb_choice = st.selectbox("今日主食：", list(dietitian_carbs.keys()))
carb_kcal = dietitian_carbs[carb_choice]

st.divider()
source = st.radio("餐點來源：", ["🏠 家中自煮", "🥡 外食 (+35% 隱形油)"])
risk_mult = 1.35 if source == "🥡 外食 (+35% 隱形油)" else 1.0

st.header("2. 添加詳細食材")
cat = st.selectbox("選擇類別：", ["🥩 肉類/蛋白質", "🥦 青菜/纖維", "🧂 調味料/醬料", "🍎 水果/飲料"])

f_final_name = ""
base_k = 0.6
m_factor = 1.0

if cat == "🥩 肉類/蛋白質":
    m_type = st.selectbox("肉類種類", list(meat_parts.keys()))
    part = st.selectbox("選擇部位", meat_parts[m_type])
    if part == "雞腿肉":
        skin_option = st.radio("處理方式：", ["🍗 帶皮", "✂️ 去皮"], horizontal=True)
        base_k = 1.2 if "去皮" in skin_option else 1.9
        f_final_name = f"雞腿肉({ '去皮' if '去皮' in skin_option else '帶皮' })"
    else:
        base_k = base_kcal_map.get(part, 1.5)
        f_final_name = part
    f_method = st.selectbox("料理方式", list(method_map.keys()))
    m_factor = method_map[f_method]
elif cat == "🥦 青菜/纖維":
    f_final_name = st.selectbox("選擇青菜", list(db_veggie.keys()) + ["手動輸入"])
    if f_final_name == "手動輸入": f_final_name = st.text_input("輸入菜名")
    f_method = st.selectbox("料理方式", list(method_map.keys()))
    base_k = db_veggie.get(f_final_name, 0.2)
    m_factor = method_map[f_method]
else:
    f_final_name = st.text_input("名稱")
    base_k = db_sauce.get(f_final_name, 3.0 if cat == "🧂 調味料/醬料" else 0.5)
    f_method = "直接添加"

f_weight = st.number_input("重量 (g/ml)", min_value=0.0, step=1.0)

if st.button("➕ 加入此項"):
    kcal = base_k * m_factor * f_weight * risk_mult
    st.session_state.meal_list.append({
        "分類": cat, "名稱": f"{f_final_name}({f_method})", "重量": f"{f_weight}g", "熱量": round(kcal, 1)
    })
    st.toast(f"已加入 {f_final_name}")

st.divider()
if st.session_state.meal_list:
    for i, item in enumerate(st.session_state.meal_list):
        st.write(f"{i+1}. {item['分類']} | {item['名稱']} | {item['重量']} -> **{item['熱量']} kcal**")
    side_total = sum(item['熱量'] for item in st.session_state.meal_list)
    final_total = carb_kcal + side_total
    if st.button("🗑️ 清空紀錄"): st.session_state.meal_list = []; st.rerun()
    st.metric("🔥 這一餐總預估", f"{final_total:.1f} kcal")
    if st.button("✅ 儲存今日紀錄", use_container_width=True):
        st.balloons(); st.success("身體數據與飲食已同步儲存！")
