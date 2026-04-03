import yfinance as yf

# S&P 500 前30大成分股
LARGE_CAP_STOCKS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "BRK-B", "LLY", "AVGO", "TSLA",
    "WMT", "JPM", "V", "UNH", "XOM",
    "ORCL", "MA", "COST", "HD", "PG",
    "JNJ", "NFLX", "BAC", "CRM", "AMD",
    "MRK", "ABBV", "CVX", "KO", "ADBE"
]

def _get_trend(ticker: str) -> dict:
    try:
        df = yf.Ticker(ticker).history(period="3mo")
        if df.empty or len(df) < 25:
            return None

        close = df["Close"]
        ma5  = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()

        latest_close = round(close.iloc[-1], 2)
        latest_ma5   = ma5.iloc[-1]
        latest_ma20  = ma20.iloc[-1]
        month_start  = close.iloc[-30] if len(close) >= 30 else close.iloc[0]
        month_pct    = round((latest_close - month_start) / month_start * 100, 2)

        ma5_trend_val = ma5.iloc[-1] - ma5.iloc[-5]
        if ma5_trend_val > 0:
            ma5_trend = "上升"
        elif ma5_trend_val < 0:
            ma5_trend = "下降"
        else:
            ma5_trend = "持平"

        above_ma20 = latest_close > latest_ma20

        return {
            "ticker":     ticker,
            "當前股價":   latest_close,
            "月內漲跌幅": f"{month_pct}%",
            "MA5趨勢":    ma5_trend,
            "站上MA20":   above_ma20,
        }
    except Exception:
        return None

def screen_stocks(sentiment: str) -> list:
    """
    sentiment: "bullish"（看多）或 "bearish"（看空）
    回傳符合趨勢的股票清單（最多10支）
    """
    results = []

    for ticker in LARGE_CAP_STOCKS:
        data = _get_trend(ticker)
        if data is None:
            continue

        if sentiment == "bullish":
            if data["MA5趨勢"] == "上升" and data["站上MA20"]:
                results.append(data)
        elif sentiment == "bearish":
            if data["MA5趨勢"] == "下降" and not data["站上MA20"]:
                results.append(data)

    # 看多依月內漲幅排序，看空依月內跌幅排序
    reverse = sentiment == "bullish"
    results.sort(key=lambda x: float(x["月內漲跌幅"].replace("%", "")), reverse=reverse)

    return results[:10]
