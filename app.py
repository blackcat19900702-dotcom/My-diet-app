import streamlit as st

# 設定介面
st.set_page_config(page_title="體脂35%紀錄器", layout="centered")

# 顯示警示標語
st.error("⚠️ 目前狀態：體脂 35% / 內脂 18")
st.title("⚖️ 精準飲食計算機")

# 食材係數 (每克大卡)
db = {
    "鮭魚": 2.1, "去皮雞腿": 1.5, "白飯": 1.4, 
    "初榨橄欖油": 9.0, "水煮蛋": 1.4, "原味優酪乳": 0.9,
    "米漢堡": 400.0, "香蕉/水果": 0.85
}

# 選擇食材
food = st.selectbox("選擇剛吃的食物：", list(db.keys()))

# 輸入克數
unit = "個" if food == "米漢堡" else "克(g) / 毫升(ml)"
amount = st.number_input(f"請輸入攝取量 ({unit})", min_value=0.0, step=1.0)

# 計算並顯示
kcal = amount * db[food]
if st.button("計算並紀錄", use_container_width=True):
    st.metric(label="這餐熱量", value=f"{kcal:.1f} kcal")
    st.info(f"💡 紀錄成功！今日已攝取量與目標還差一點點，加油！")
