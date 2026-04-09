import time
import yfinance as yf

def get_fundamentals(stock: yf.Ticker) -> dict:

    def fmt_billion(value):
        try:
            v = float(value)
            return f"${v / 1_000_000_000:.2f}B"
        except Exception:
            return "無資料"

    def fmt_pct(value):
        try:
            return f"{float(value) * 100:.2f}%"
        except Exception:
            return "無資料"

    def fmt_val(value, decimals=2):
        try:
            return round(float(value), decimals)
        except Exception:
            return "無資料"

    # ── fast_info（輕量，幾乎不被 rate limit）──
    market_cap = None
    pe         = None
    eps        = None
    try:
        fi         = stock.fast_info
        market_cap = getattr(fi, "market_cap",    None)
        pe         = getattr(fi, "p_e_ratio",      None)
        eps        = getattr(fi, "trailing_eps",   None)
    except Exception:
        pass

    # ── .info（嘗試一次，只取公司名稱和產業）──
    company_name = "無資料"
    sector       = "無資料"
    try:
        info = stock.info
        if info and len(info) > 5:
            company_name = info.get("longName", "無資料")
            sector       = info.get("sector",   "無資料")
            if pe  is None: pe  = info.get("trailingPE")
            if eps is None: eps = info.get("trailingEps")
            if market_cap is None: market_cap = info.get("marketCap")
    except Exception:
        pass

    # ── 財務報表（revenue growth、margins、D/E、FCF）──
    rev_growth = None
    net_margin = None
    de_ratio   = None
    fcf        = None

    try:
        income = stock.income_stmt
        if income is not None and not income.empty:
            rev_key = next((k for k in income.index if "Revenue" in k and "Total" in k), None)
            ni_key  = next((k for k in income.index if "Net Income" in k), None)

            if rev_key and len(income.loc[rev_key]) >= 2:
                r_new = income.loc[rev_key].iloc[0]
                r_old = income.loc[rev_key].iloc[1]
                if r_old and r_old != 0:
                    rev_growth = (r_new - r_old) / abs(r_old)

            if ni_key and rev_key:
                ni = income.loc[ni_key].iloc[0]
                rv = income.loc[rev_key].iloc[0]
                if rv and rv != 0:
                    net_margin = ni / rv
    except Exception:
        pass

    try:
        balance = stock.balance_sheet
        if balance is not None and not balance.empty:
            debt_key   = next((k for k in balance.index if "Total Debt" in k), None)
            equity_key = next((k for k in balance.index if "Stockholders" in k or "Total Equity" in k), None)
            if debt_key and equity_key:
                debt   = balance.loc[debt_key].iloc[0]
                equity = balance.loc[equity_key].iloc[0]
                if equity and equity != 0:
                    de_ratio = debt / equity
    except Exception:
        pass

    try:
        cf = stock.cashflow
        if cf is not None and not cf.empty:
            fcf_key = next((k for k in cf.index if "Free Cash Flow" in k), None)
            if fcf_key:
                fcf = cf.loc[fcf_key].iloc[0]
    except Exception:
        pass

    return {
        "公司名稱":       company_name,
        "產業":           sector,
        "市值":           fmt_billion(market_cap),
        "本益比(PE)":     fmt_val(pe),
        "每股盈餘(EPS)":  fmt_val(eps),
        "營收年增率":     fmt_pct(rev_growth),
        "淨利率":         fmt_pct(net_margin),
        "負債比(D/E)":    fmt_val(de_ratio),
        "自由現金流":     fmt_billion(fcf),
    }
