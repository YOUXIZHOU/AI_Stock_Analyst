import time
import yfinance as yf

def get_fundamentals(stock: yf.Ticker) -> dict:
    info = {}
    for attempt in range(3):
        try:
            data = stock.info
            if data and len(data) > 5:
                info = data
                break
        except Exception:
            pass
        if attempt < 2:
            time.sleep(2 ** attempt)

    def fmt_billion(value):
        if value is None:
            return "無資料"
        return f"${value / 1_000_000_000:.2f}B"

    def fmt_pct(value):
        if value is None:
            return "無資料"
        return f"{value * 100:.2f}%"

    def fmt_val(value, decimals=2):
        if value is None:
            return "無資料"
        return round(value, decimals)

    return {
        "公司名稱":       info.get("longName", "無資料"),
        "產業":           info.get("sector",   "無資料"),
        "市值":           fmt_billion(info.get("marketCap")),
        "本益比(PE)":     fmt_val(info.get("trailingPE")),
        "每股盈餘(EPS)":  fmt_val(info.get("trailingEps")),
        "營收年增率":     fmt_pct(info.get("revenueGrowth")),
        "淨利率":         fmt_pct(info.get("profitMargins")),
        "負債比(D/E)":    fmt_val(info.get("debtToEquity")),
        "自由現金流":     fmt_billion(info.get("freeCashflow")),
    }
