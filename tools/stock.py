import yfinance as yf
import pandas as pd

def get_stock_price(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")

    if hist.empty:
        return {"error": "No data found"}

    latest_price = hist["Close"].iloc[-1]
    prev_price = hist["Close"].iloc[-2]

    change = latest_price - prev_price
    change_pct = (change / prev_price) * 100

    return {
        "ticker": ticker,
        "latest_price": round(latest_price, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2)
    }

def get_ohlcv(ticker: str, period: str = "3mo") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    if df.empty:
        return pd.DataFrame()

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    # 均線
    df["MA5"]  = df["Close"].rolling(window=5).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()

    # 布林通道（20日，2倍標準差）
    df["BB_mid"]   = df["Close"].rolling(window=20).mean()
    df["BB_upper"] = df["BB_mid"] + 2 * df["Close"].rolling(window=20).std()
    df["BB_lower"] = df["BB_mid"] - 2 * df["Close"].rolling(window=20).std()

    return df.round(2)