import yfinance as yf

# S&P 500 前100大成分股（依市值排序）含產業標籤
LARGE_CAP_STOCKS = [
    # Technology
    ("AAPL",  "Technology"), ("MSFT",  "Technology"), ("NVDA",  "Technology"),
    ("AVGO",  "Technology"), ("ORCL",  "Technology"), ("CRM",   "Technology"),
    ("AMD",   "Technology"), ("ADBE",  "Technology"), ("QCOM",  "Technology"),
    ("TXN",   "Technology"), ("INTC",  "Technology"), ("IBM",   "Technology"),
    ("NOW",   "Technology"), ("AMAT",  "Technology"), ("LRCX",  "Technology"),

    # Communication Services
    ("GOOGL", "Communication Services"), ("META",  "Communication Services"),
    ("NFLX",  "Communication Services"), ("DIS",   "Communication Services"),
    ("T",     "Communication Services"), ("VZ",    "Communication Services"),
    ("TMUS",  "Communication Services"),

    # Consumer Discretionary
    ("AMZN",  "Consumer Discretionary"), ("TSLA",  "Consumer Discretionary"),
    ("HD",    "Consumer Discretionary"), ("MCD",   "Consumer Discretionary"),
    ("NKE",   "Consumer Discretionary"), ("SBUX",  "Consumer Discretionary"),
    ("LOW",   "Consumer Discretionary"), ("TJX",   "Consumer Discretionary"),
    ("BKNG",  "Consumer Discretionary"),

    # Consumer Staples
    ("WMT",   "Consumer Staples"), ("PG",    "Consumer Staples"),
    ("KO",    "Consumer Staples"), ("PEP",   "Consumer Staples"),
    ("COST",  "Consumer Staples"), ("PM",    "Consumer Staples"),
    ("MDLZ",  "Consumer Staples"),

    # Financials
    ("JPM",   "Financials"), ("V",     "Financials"), ("MA",    "Financials"),
    ("BAC",   "Financials"), ("WFC",   "Financials"), ("GS",    "Financials"),
    ("MS",    "Financials"), ("BLK",   "Financials"), ("AXP",   "Financials"),
    ("BRK-B", "Financials"), ("SCHW",  "Financials"),

    # Healthcare
    ("UNH",   "Healthcare"), ("LLY",   "Healthcare"), ("JNJ",   "Healthcare"),
    ("MRK",   "Healthcare"), ("ABBV",  "Healthcare"), ("TMO",   "Healthcare"),
    ("ABT",   "Healthcare"), ("DHR",   "Healthcare"), ("PFE",   "Healthcare"),
    ("AMGN",  "Healthcare"), ("ISRG",  "Healthcare"), ("MDT",   "Healthcare"),

    # Industrials
    ("GE",    "Industrials"), ("CAT",   "Industrials"), ("HON",   "Industrials"),
    ("UNP",   "Industrials"), ("RTX",   "Industrials"), ("BA",    "Industrials"),
    ("DE",    "Industrials"), ("MMM",   "Industrials"), ("LMT",   "Industrials"),
    ("UPS",   "Industrials"),

    # Energy
    ("XOM",   "Energy"), ("CVX",   "Energy"), ("COP",   "Energy"),
    ("SLB",   "Energy"), ("EOG",   "Energy"), ("PSX",   "Energy"),

    # Materials
    ("LIN",   "Materials"), ("APD",   "Materials"), ("SHW",   "Materials"),
    ("FCX",   "Materials"), ("NEM",   "Materials"),

    # Utilities
    ("NEE",   "Utilities"), ("DUK",   "Utilities"), ("SO",    "Utilities"),
    ("D",     "Utilities"),

    # Real Estate
    ("PLD",   "Real Estate"), ("AMT",   "Real Estate"), ("EQIX",  "Real Estate"),
    ("SPG",   "Real Estate"),
]

SECTORS = sorted(set(sector for _, sector in LARGE_CAP_STOCKS))

def _get_trend(ticker: str, sector: str) -> dict:
    try:
        df = yf.Ticker(ticker).history(period="3mo")
        if df.empty or len(df) < 25:
            return None

        close = df["Close"]
        ma5   = close.rolling(5).mean()
        ma20  = close.rolling(20).mean()

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

        return {
            "ticker":     ticker,
            "產業":       sector,
            "當前股價":   latest_close,
            "月內漲跌幅": f"{month_pct}%",
            "MA5趨勢":    ma5_trend,
            "站上MA20":   latest_close > latest_ma20,
        }
    except Exception:
        return None

def screen_stocks(sentiment: str, top_n: int = 30, sector: str = None) -> list:
    """
    sentiment : "bullish" 或 "bearish"
    top_n     : 從前 N 大公司篩選（依清單順序）
    sector    : 產業篩選，None 表示不限
    """
    pool = LARGE_CAP_STOCKS[:top_n]
    if sector:
        pool = [(t, s) for t, s in pool if s == sector]

    results = []
    for ticker, sec in pool:
        data = _get_trend(ticker, sec)
        if data is None:
            continue

        if sentiment == "bullish":
            if data["MA5趨勢"] == "上升" and data["站上MA20"]:
                results.append(data)
        elif sentiment == "bearish":
            if data["MA5趨勢"] == "下降" and not data["站上MA20"]:
                results.append(data)

    reverse = sentiment == "bullish"
    results.sort(key=lambda x: float(x["月內漲跌幅"].replace("%", "")), reverse=reverse)

    return results[:10]
