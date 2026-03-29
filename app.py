import streamlit as st

# 設定 App 頁面
st.set_page_config(page_title="體脂35%紀錄器", page_icon="⚖️")

# 警示與標題
st.error("⚠️ 目前狀態：體脂 35% / 內脂 18")
st.title("⚖️ 精準飲食計算機 (含料理方式)")

# --- 食材資料庫 ---
# 格式：{"食材名稱": {"料理方式": 每克熱量}}
food_db = {
    "雞腿 (去皮)": {"水煮/滷": 1.5, "油煎": 2.1, "氣炸": 1.8},
    "鮭魚": {"清蒸": 2.1, "乾煎": 2.6, "生食": 2.0},
    "青菜": {"燙青菜": 0.2, "油炒": 0.6},
    "雞蛋": {"水煮": 1.4, "荷包蛋": 1.9, "歐姆蛋": 2.2},
    "白飯": {"一般": 1.4},
    "優酪乳": {"原味": 0.9, "無糖": 0.6},
    "米漢堡": {"一個": 400.0},
    "香蕉/水果": {"一般": 0.85}
}

# --- 介面操作 ---
# 1. 選擇食材
food_choice = st.selectbox("1. 選擇食材：", list(food_db.keys()))

# 2. 選擇料理方式 (根據食材自動變動)
methods = food_db[food_choice]
method_choice = st.selectbox("2. 選擇料理方式：", list(methods.keys()))

# 3. 輸入量
unit = "個" if food_choice == "米漢堡" else "克(g) / 毫升(ml)"
amount = st.number_input(f"3. 輸入攝取量 ({unit})", min_value=0.0, value=100.0, step=1.0)

# 4. 計算結果
kcal_per_unit = methods[method_choice]
total_kcal = amount * kcal_per_unit

# 顯示按鈕
if st.button("計算並紀錄", use_container_width=True):
    st.divider()
    st.metric(label=f"本次攝取：{food_choice} ({method_choice})", value=f"{total_kcal:.1f} kcal")
    
    # 針對內臟脂肪的幽默提醒
    if method_choice in ["油煎", "油炒", "荷包蛋"]:
        st.warning("⚠️ 內脂 18 的警訊：這份油比較多，下一餐記得選清淡點！")
    else:
        st.success("✨ 選得好！清淡飲食是降內脂的捷徑。")
