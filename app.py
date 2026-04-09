import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from agent.controller import run_agent
from agent.recommender import run_recommender
from services.llm import call_claude
from utils.history import save_result, load_all

st.set_page_config(page_title="AI Stock Analyst", layout="wide")
st.title("📈 AI Stock Analyst")

# ──────────────────────────────────────────
# Sidebar — 查詢歷史
# ──────────────────────────────────────────
with st.sidebar:
    st.header("查詢歷史")
    history = load_all()

    if not history:
        st.write("尚無查詢記錄")
    else:
        for entry in history:
            label = f"{entry['date']} | {entry['ticker']}"
            if st.button(label, width='stretch', key=label):
                ohlcv_df = pd.DataFrame(entry["ohlcv"])
                if not ohlcv_df.empty and "Datetime" in ohlcv_df.columns:
                    ohlcv_df = ohlcv_df.set_index("Datetime")
                elif not ohlcv_df.empty and "Date" in ohlcv_df.columns:
                    ohlcv_df = ohlcv_df.set_index("Date")

                st.session_state["result"] = {
                    "price":        entry["price"],
                    "fundamentals": entry["fundamentals"],
                    "news":         entry["news"],
                    "tech":         entry["tech"],
                    "analysis":     entry["analysis"],
                    "ohlcv":        ohlcv_df,
                }

# ──────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["個股分析", "K 線圖", "股票推薦"])

# ──────────────────────────────────────────
# Tab 1 — 個股分析
# ──────────────────────────────────────────
with tab1:
    with st.form("search_form"):
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            ticker_input = st.text_input("股票代碼", placeholder="例如：NVDA、AAPL", label_visibility="collapsed")
        with col_btn:
            search_clicked = st.form_submit_button("搜尋", width='stretch')

    if search_clicked and ticker_input:
        with st.spinner("資料載入中..."):
            result = run_agent(ticker_input.strip().upper())
            st.session_state["result"] = result
            save_result(result)
            st.rerun()

    if "result" in st.session_state:
        result = st.session_state["result"]
        price  = result["price"]
        fund   = result["fundamentals"]
        news   = result["news"]

        if "error" in price:
            st.error("無法取得股票資料，請確認代碼是否正確，或稍後再試。")
            st.stop()

        # ── 股價區塊 ──
        st.subheader(f"{fund.get('公司名稱', price['ticker'])}（{price['ticker']}）")
        c1, c2, c3 = st.columns(3)
        c1.metric("當前股價",   f"${price['latest_price']}")
        c2.metric("單日漲跌",   f"${price['change']}",    delta=f"{price['change_pct']}%")
        c3.metric("產業",       fund.get("產業", "—"))

        st.divider()

        # ── 基本面區塊 ──
        st.subheader("公司基本面")
        f1, f2, f3 = st.columns(3)
        f1.metric("市值",           fund.get("市值", "—"))
        f1.metric("本益比 (PE)",    str(fund.get("本益比(PE)", "—")))
        f2.metric("每股盈餘 (EPS)", str(fund.get("每股盈餘(EPS)", "—")))
        f2.metric("營收年增率",     fund.get("營收年增率", "—"))
        f3.metric("淨利率",         fund.get("淨利率", "—"))
        f3.metric("負債比 (D/E)",   str(fund.get("負債比(D/E)", "—")))
        st.metric("自由現金流",     fund.get("自由現金流", "—"))

        st.divider()

        # ── 新聞區塊 ──
        st.subheader("最新新聞")
        if news:
            for item in news:
                with st.expander(f"{item.get('時間', '')}　{item.get('標題', '')}"):
                    st.write(item.get("摘要", "無摘要"))
        else:
            st.write("目前無相關新聞")

        st.divider()

        # ── Claude 分析 ──
        st.subheader("Claude 分析總結")
        st.markdown(result["analysis"])

# ──────────────────────────────────────────
# Tab 2 — K 線圖
# ──────────────────────────────────────────
with tab2:
    if "result" not in st.session_state:
        st.info("請先在「個股分析」Tab 搜尋股票。")
    else:
        result = st.session_state["result"]
        df     = result["ohlcv"]
        ticker = result["price"]["ticker"]

        st.subheader(f"{ticker} K 線圖")

        col_ma, col_bb = st.columns(2)
        with col_ma:
            show_ma5  = st.checkbox("MA5",  value=True)
            show_ma20 = st.checkbox("MA20", value=True)
            show_ma60 = st.checkbox("MA60", value=False)
        with col_bb:
            show_bb = st.checkbox("布林通道", value=False)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"],   close=df["Close"],
            name="K線",
            increasing_line_color="#ef5350",
            decreasing_line_color="#26a69a",
        ))

        if show_ma5  and "MA5"  in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA5"],  name="MA5",  line=dict(color="#ff9800", width=1)))
        if show_ma20 and "MA20" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20", line=dict(color="#2196f3", width=1)))
        if show_ma60 and "MA60" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA60"], name="MA60", line=dict(color="#9c27b0", width=1)))

        if show_bb and "BB_upper" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="布林上緣", line=dict(color="#78909c", width=1, dash="dash")))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_mid"],   name="布林中線", line=dict(color="#78909c", width=1)))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="布林下緣", line=dict(color="#78909c", width=1, dash="dash"),
                                     fill="tonexty", fillcolor="rgba(120,144,156,0.1)"))

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=600,
            template="plotly_dark",
            legend=dict(orientation="h", y=1.02),
            margin=dict(l=20, r=20, t=40, b=20),
        )

        st.plotly_chart(fig, width='stretch')

# ──────────────────────────────────────────
# Tab 3 — 股票推薦
# ──────────────────────────────────────────
with tab3:
    from tools.screener import SECTORS

    st.subheader("股票推薦")
    st.write("根據技術指標篩選大型股，由 Claude 推薦最值得關注的標的。")

    col_n, col_sector = st.columns(2)
    with col_n:
        top_n = st.select_slider(
            "篩選母體（前 N 大公司）",
            options=list(range(10, 101, 10)),
            value=30,
        )
    with col_sector:
        sector_options = ["不限"] + SECTORS
        selected_sector = st.selectbox("產業篩選", options=sector_options)
        sector = None if selected_sector == "不限" else selected_sector

    col_bull, col_bear = st.columns(2)
    run_bull = col_bull.button("📈 看多推薦", width='stretch')
    run_bear = col_bear.button("📉 看空推薦", width='stretch')

    if run_bull or run_bear:
        sentiment = "bullish" if run_bull else "bearish"
        with st.spinner("篩選中，約需 20–30 秒..."):
            rec = run_recommender(sentiment, top_n=top_n, sector=sector)
            st.session_state["rec"] = rec

    if "rec" in st.session_state:
        rec = st.session_state["rec"]
        st.markdown(f"**市場觀點：{rec['sentiment']}**")

        if rec["candidates"]:
            st.subheader("篩選結果")
            display_candidates = [{k: v for k, v in c.items() if k != "站上MA20"} for c in rec["candidates"]]
            st.dataframe(display_candidates, width='stretch', hide_index=True)

        st.subheader("Claude 推薦")
        st.markdown(rec["analysis"])

        st.divider()
        st.subheader("進一步提問")

        QUICK_QUESTIONS = [
            "我該如何操作？",
            "這些股票的風險是什麼？",
            "適合長期持有嗎？",
            "現在是好的進場時機嗎？",
        ]

        if "rec_chat" not in st.session_state:
            st.session_state["rec_chat"] = []

        cols = st.columns(len(QUICK_QUESTIONS))
        for i, q in enumerate(QUICK_QUESTIONS):
            if cols[i].button(q, width='stretch'):
                st.session_state["rec_pending"] = q

        user_input = st.chat_input("輸入你的問題...")
        if user_input:
            st.session_state["rec_pending"] = user_input

        if "rec_pending" in st.session_state:
            question = st.session_state.pop("rec_pending")
            st.session_state["rec_chat"].append({"role": "user", "content": question})

            context = f"""
以下是剛才的股票推薦結果：
市場觀點：{rec['sentiment']}
推薦分析：{rec['analysis']}

使用者問題：{question}
"""
            history_chat = st.session_state["rec_chat"][:-1]
            messages = history_chat + [{"role": "user", "content": context}]

            with st.spinner("思考中..."):
                reply = call_claude(messages, max_tokens=500, system="你是一位 AI 股票分析師，請用繁體中文簡潔專業地回答使用者關於股票推薦的問題。")

            st.session_state["rec_chat"].append({"role": "assistant", "content": reply})

        for msg in st.session_state["rec_chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
