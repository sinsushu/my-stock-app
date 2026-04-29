import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 網頁標題與設定
st.set_page_config(page_title="黃金分割率分析工具", layout="wide")
st.title("📈 股票黃金分割率 (Fibonacci) 追蹤器")

# 側邊欄輸入
st.sidebar.header("參數設定")
ticker = st.sidebar.text_input("輸入股票代號", value="2330.TW")
time_period = st.sidebar.selectbox("選擇分析區間", ["5d","17d","60d","1mo","3mo", "6mo", "1y", "2y"], index=1)

# 按下按鈕後執行
if st.sidebar.button("開始分析"):
    # 讀取數據
    df = yf.Ticker(ticker).history(period=time_period)
    
    if df.empty:
        st.error("找不到股票代號，請檢查格式是否正確 (例如台股需加 .TW)")
    else:
        # 計算最高、最低與價差
        high_price = df['High'].max()
        low_price = df['Low'].min()
        diff = high_price - low_price
        
        # 定義比例
        ratios = {
            "最高點 (0%)": 0.0,
            "回檔 23.6%": 0.236,
            "回檔 38.2%": 0.382,
            "回檔 50.0%": 0.5,
            "回檔 61.8%": 0.618,
            "回檔 78.6%": 0.786,
            "最低點 (100%)": 1.0
        }
        
        # 顯示數據卡片
        st.subheader(f"{ticker} 關鍵價位分析")
        cols = st.columns(len(ratios))
        for i, (label, ratio) in enumerate(ratios.items()):
            price = high_price - (diff * ratio)
            cols[i].metric(label, f"{price:.2f}")

        # 繪製 K 線圖與分割線
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="K線"
        )])

        # 加入黃金分割水平線
        colors = ['red', 'orange', 'green', 'blue', 'purple', 'brown', 'black']
        for (label, ratio), color in zip(ratios.items(), colors):
            level_price = high_price - (diff * ratio)
            fig.add_hline(y=level_price, line_dash="dash", line_color=color, 
                          annotation_text=label, annotation_position="top left")

        fig.update_layout(title=f"{ticker} 走勢與黃金分割位", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True,key="stock_fibonacci_chart")
        # --- 在圖表下方加入策略提醒 ---
        st.divider() # 加入一條橫線區隔
        st.subheader("💡 Fibonacci 交易策略提醒")
        # --- 隔日沖預測區塊 ---
        st.divider()
        st.subheader("🚀 隔日沖目標價預測 (Fibonacci Extension)")
        
        # 取得最後一根 K 線的數據 (今日數據)
        today_data = df.iloc[-1]
        t_high = today_data['High']
        t_low = today_data['Low']
        t_close = today_data['Close']
        t_diff = t_high - t_low

        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("**📈 明日壓力位 (預期獲利點)**")
            ext_1382 = t_high + (t_diff * 0.382)
            ext_1618 = t_high + (t_diff * 0.618)
            st.write(f"第一目標 (1.382): :red[{ext_1382:.2f}]")
            st.write(f"第二目標 (1.618): :red[{ext_1618:.2f}]")

        with col_b:
            st.write("**🛡️ 強勢股支撐 (若跌破不宜隔日沖)**")
            sup_0382 = t_high - (t_diff * 0.382)
            st.write(f"強勢回檔支撐 (0.382): :green[{sup_0382:.2f}]")
            st.write(f"今日收盤價: **{t_close:.2f}**")
        
        st.caption("註：隔日沖建議選擇收盤價接近今日高點，且守住 0.382 支撐位的標的。")
        
        st.info("""
        **關鍵位置強度說明：**
        1. **0.382（強勢修正）：** 股價僅微幅回檔即再度轉強，代表原趨勢極其強勁，後市噴出機率高。
        2. **0.618（黃金分界線）：** 技術面最重要的防線。若在此獲得支撐，多頭趨勢不變；若放量跌破，趨勢可能反轉。
        3. **0.5（心理關卡）：** 多空平衡的心理中軸，常有強大的支撐或壓力。

        **🎯 判斷標準：**
        * 觀察價格到達比例時的 **「K 線型態」** 與 **「成交量」**。
        * **止跌訊號：** 若在 **0.618** 處出現 **長下影線（錘子線）** 且 **量縮**，即是極佳的觀察點。
        """)
        st.success("分析完成！您可以縮放圖表來觀察股價是否在特定比例處止跌或受阻。")
