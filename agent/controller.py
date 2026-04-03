from services.llm import call_claude
from tools.stock import get_stock_price, get_ohlcv
from tools.news import get_news
from tools.fundamentals import get_fundamentals

SYSTEM_PROMPT = """
你是一位 AI 股票分析師。

你會收到已整理好的數據，根據這些數據進行分析。

規則：
- 保持簡潔專業
- 用易懂的表格呈現分析結果
- 必須提供一個明確的投資建議總結
- 不要列出新聞標題或摘要，除非它們對分析非常重要，必須簡短引用
- 在建議的最後加上**風險提示**，提醒投資者注意潛在風險
"""

def _build_tech_summary(ohlcv_df) -> dict:
    if ohlcv_df.empty:
        return {}

    month_df = ohlcv_df.iloc[-30:]
    latest   = month_df.iloc[-1]
    ma5_series = month_df["MA5"].dropna()

    if len(ma5_series) >= 5:
        ma5_trend_val = ma5_series.iloc[-1] - ma5_series.iloc[-5]
        if ma5_trend_val > 0:
            ma5_trend = "上升"
        elif ma5_trend_val < 0:
            ma5_trend = "下降"
        else:
            ma5_trend = "持平"
    else:
        ma5_trend = "無資料"

    close       = latest["Close"]
    bb_upper    = latest.get("BB_upper")
    bb_lower    = latest.get("BB_lower")
    bb_mid      = latest.get("BB_mid")

    if bb_upper and bb_lower and bb_mid:
        if close >= bb_upper:
            bb_position = "高於上緣（超買區）"
        elif close <= bb_lower:
            bb_position = "低於下緣（超賣區）"
        elif close >= bb_mid:
            bb_position = "中線至上緣之間"
        else:
            bb_position = "中線至下緣之間"
    else:
        bb_position = "無資料"

    return {
        "近一個月最高價":   round(month_df["High"].max(), 2),
        "近一個月最低價":   round(month_df["Low"].min(), 2),
        "月初收盤價":       round(month_df["Close"].iloc[0], 2),
        "當前收盤價":       round(close, 2),
        "月內漲跌幅":       f"{round((close - month_df['Close'].iloc[0]) / month_df['Close'].iloc[0] * 100, 2)}%",
        "MA5（當前）":      round(latest.get("MA5", 0), 2),
        "MA5趨勢（5日）":   ma5_trend,
        "MA20（當前）":     round(latest.get("MA20", 0), 2),
        "MA60（當前）":     round(latest.get("MA60", 0), 2),
        "布林上緣":         round(bb_upper, 2) if bb_upper else "無資料",
        "布林中線":         round(bb_mid, 2)   if bb_mid   else "無資料",
        "布林下緣":         round(bb_lower, 2) if bb_lower else "無資料",
        "股價位置":         bb_position,
    }

def run_agent(ticker: str) -> dict:
    ticker = ticker.strip().upper()

    # Step 1: 執行所有工具
    price_data        = get_stock_price(ticker)
    fundamentals_data = get_fundamentals(ticker)
    news_data         = get_news(ticker)
    ohlcv_df          = get_ohlcv(ticker)
    tech_data         = _build_tech_summary(ohlcv_df)

    # Step 2: Claude 只負責分析
    prompt = [
        {
            "role": "user",
            "content": f"""
股票代碼：{ticker}

股價：
{price_data}

技術指標：
{tech_data}

公司基本面：
{fundamentals_data}

請根據以上數據提供技術面、基本面分析與簡短投資建議總結，不要列出原始數據。
"""
#最新新聞：
#{news_data}
        }
    ]

    analysis = call_claude(prompt, max_tokens=1500, system=SYSTEM_PROMPT)

    return {
        "price":        price_data,
        "tech":         tech_data,
        "fundamentals": fundamentals_data,
        "news":         news_data,
        "ohlcv":        ohlcv_df,
        "analysis":     analysis,
    }