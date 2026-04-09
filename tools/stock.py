import time
import yfinance as yf
import pandas as pd

def _fetch_history(ticker: str, period: str, retries: int = 3) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            df = yf.Ticker(ticker).history(period=period)
            if not df.empty:
                return df
        except Exception:
            pass
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return pd.DataFrame()

def get_stock_price(ticker: str) -> dict:
    hist = _fetch_history(ticker, period="5d")

    if hist.empty:
        return {"error": "No data found"}

    latest_price = hist["Close"].iloc[-1]
    prev_price   = hist["Close"].iloc[-2]
    change       = latest_price - prev_price
    change_pct   = (change / prev_price) * 100

    return {
        "ticker":       ticker,
        "latest_price": round(latest_price, 2),
        "change":       round(change, 2),
        "change_pct":   round(change_pct, 2)
    }

def get_ohlcv(ticker: str, period: str = "1y") -> pd.DataFrame:
    df = _fetch_history(ticker, period=period)

    if df.empty:
        return pd.DataFrame()

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    df["MA5"]  = df["Close"].rolling(window=5).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()

    df["BB_mid"]   = df["Close"].rolling(window=20).mean()
    df["BB_upper"] = df["BB_mid"] + 2 * df["Close"].rolling(window=20).std()
    df["BB_lower"] = df["BB_mid"] - 2 * df["Close"].rolling(window=20).std()

    return df.round(2)
