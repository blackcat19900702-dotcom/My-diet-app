import streamlit as st

# 設定頁面資訊
st.set_page_config(page_title="內脂終結者：旗艦整合版", page_icon="⚖️")

# --- 1. 核心資料庫 (營養師建議與標準值) ---
dietitian_carbs = {
    "🍚 白米飯 (240g)": 336.0,
    "🌾 白米混合五穀米 (240g)": 320.0,
    "🍜 煮過白麵條 (300g)": 345.0,
    "🚫 不吃主食 / 自定義": 0.0
}

# 基礎熱量庫 (每克 kcal)
db = {
    "🥩 肉類/蛋白質": {"雞胸肉": 1.1, "雞肉": 1.6, "鮭魚": 2.1, "牛肉": 2.5, "雞蛋": 1.4, "豆腐": 0.8},
    "🥦 青菜/纖維": {"櫛瓜": 0.17, "茄子": 0.25, "青菜": 0.2, "高麗菜": 0.25, "花椰菜": 0.3},
    "🧂 調味料/醬料": {"新東陽肉醬": 2.9, "橄欖油": 9.0, "醬油": 0.6, "沙拉醬": 6.5, "辣椒醬": 1.5},
    "🍎 水果/飲料": {"蘋果/芭樂": 0.5, "含糖飲料": 0.4, "無糖茶/水": 0.0}
}

# 料理方式加權
method_map = {"水煮/清蒸": 1.0, "滷/燉": 1.1, "乾煎": 1.25, "油炒": 1.4, "油炸": 1.8}

# 初始化清單儲存 (Session State)
if 'meal_list' not in st.session_state:
    st.session_state.meal_list = []

# --- App 介面 ---
st.error("📉 當前目標：內臟脂肪 18 | 嚴格控管加工醬料與隱形油脂")
st.title("⚖️ 旗艦級飲食紀錄器")

# 第一區：主食快捷鍵
st.header("1. 主食選擇")
carb_choice = st.selectbox("今日主食：", list(dietitian_carbs.keys()))
carb_kcal = dietitian_carbs[carb_choice]

# 第二區：來源判定
st.divider()
source = st.radio("餐點來源：", ["🏠 家中自煮", "🥡 外食 (自動加成 35% 隱形油)"])
risk_mult = 1.35 if source == "🥡 外食 (自動加成 35% 隱形油)" else 1.0

# 第三區：詳細食材添加
st.header("2. 添加內容 (肉/菜/醬/飲)")
cat = st.selectbox("選擇類別：", list(db.keys()))

col1, col2 = st.columns(2)
with col1:
    # 讓使用者可以從資料庫選或自己打字
    options = list(db[cat].keys())
    f_name = st.selectbox(f"選擇{cat}", options + ["➕ 手動輸入其他"])
    if f_name == "➕ 手動輸入其他":
        f_name = st.text_input("請輸入名稱", "")
with col2:
    # 只有肉類跟青菜需要選料理方式
    if cat in ["🥩 肉類/蛋白質", "🥦 青菜/纖維"]:
        f_method = st.selectbox("料理方式", list(method_map.keys()))
        m_factor = method_map[f_method]
    else:
        f_method = "直接添加"
        m_factor = 1.0

f_weight = st.number_input("輸入重量 (g/ml)", min_value=0.0, value=0.0, step=1.0)

if st.button("➕ 加入此項到本餐清單"):
    # 抓取基礎熱量邏輯
    base = db[cat].get(f_name, 0.6 if "肉" in cat else 0.2)
    kcal = base * m_factor * f_weight * risk_mult
    
    st.session_state.meal_list.append({
        "分類": cat,
        "名稱": f"{f_name}({f_method})",
        "重量": f"{f_weight}g",
        "熱量": round(kcal, 1)
    })
    st.toast(f"已加入 {f_name}")

# 第四區：清單結算
st.divider()
st.header("📋 本餐明細")
if st.session_state.meal_list:
    for i, item in enumerate(st.session_state.meal_list):
        st.write(f"{i+1}. {item['分類']} | {item['名稱']} | {item['重量']} -> **{item['熱量']} kcal**")
    
    if st.button("🗑️ 清空整餐紀錄"):
        st.session_state.meal_list = []
        st.rerun()

    # 計算各項總合
    side_total = sum(item['熱量'] for item in st.session_state.meal_list)
    final_total = carb_kcal + side_total

    st.divider()
    st.subheader("📊 結算報告")
    c1, c2 = st.columns(2)
    c1.metric("主食熱量", f"{carb_kcal} kcal")
    c2.metric("配菜/醬料總計", f"{side_total:.1f} kcal")
    st.metric("🔥 這一餐總攝取", f"{final_total:.1f} kcal")
    
    # 內脂警告邏輯
    sauce_kcal = sum(item['熱量'] for item in st.session_state.meal_list if "醬料" in item['分類'])
    if sauce_kcal > 80:
        st.warning(f"⚠️ 警告：調味料熱量 ({sauce_kcal} kcal) 偏高，這對內脂 18 非常不利！")
    
    if st.button("✅ 確認儲存今日紀錄", use_container_width=True):
        st.balloons()
        st.success("紀錄已儲存！為了內脂 18，吃完記得多走幾步路！")
else:
    st.info("請在上方添加食材...")
