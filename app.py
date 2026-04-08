# --- Tab 5: 飲水 (新增飲料智慧分析) ---
with tabs[5]:
    w_type = st.radio("類型", ["純水", "飲料"], horizontal=True)
    
    if w_type == "純水":
        w_val = st.number_input("水量 (ml)", value=250.0, key="pure_water")
        if st.button("記水"): 
            st.session_state.water += w_val
            st.rerun()
    else:
        st.info("💡 系統將根據關鍵字自動分析 (範例：五十嵐珍珠奶茶無糖)")
        drink_name = st.text_input("輸入飲料名稱", key="d_name_input")
        drink_ml = st.number_input("飲用量 (ml)", value=700.0, step=50.0)
        
        if st.button("🥤 紀錄飲料"):
            # 建立份數增量
            d_carbs = 0.0  
            d_fat = 0.0    
            d_milk = 0.0   
            
            # 容量倍率 (以 700ml 為 1 單位)
            ratio = drink_ml / 700
            
            # 判定基底
            if "奶茶" in drink_name:
                d_fat += 3.0 * ratio
                d_carbs += 1.5 * ratio
            elif any(k in drink_name for k in ["拿鐵", "鮮奶茶", "歐蕾"]):
                d_milk += 1.5 * ratio
            
            # 判定配料
            if any(k in drink_name for k in ["珍珠", "波霸", "粉圓", "混珠"]):
                d_carbs += 4.0 * ratio
            
            # 判定甜度
            if "全糖" in drink_name: d_carbs += 3.0 * ratio
            elif "半糖" in drink_name: d_carbs += 1.5 * ratio
            elif "微糖" in drink_name: d_carbs += 0.8 * ratio
            elif "無糖" in drink_name: d_carbs += 0.0
            
            # 寫入數據
            st.session_state.daily["carbs"] += d_carbs
            st.session_state.daily["fat"] += d_fat
            st.session_state.daily["milk"] += d_milk
            st.session_state.water += drink_ml
            
            st.rerun()
