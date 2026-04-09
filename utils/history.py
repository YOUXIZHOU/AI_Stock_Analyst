import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "history.json")
MAX_ENTRIES  = 30

def _load() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "item"):
            return obj.item()
        return super().default(obj)

def _save(entries: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2, cls=_Encoder)

def save_result(result: dict):
    entries = _load()

    entry = {
        "date":         datetime.now().strftime("%Y-%m-%d"),
        "ticker":       result["price"]["ticker"],
        "price":        result["price"],
        "fundamentals": result["fundamentals"],
        "news":         result["news"],
        "tech":         result["tech"],
        "analysis":     result["analysis"],
        # ohlcv DataFrame 轉為可序列化格式
        "ohlcv":        result["ohlcv"].reset_index().to_dict(orient="records")
                        if not result["ohlcv"].empty else [],
    }

    # 移除重複（同日同股票）
    entries = [e for e in entries if not (e["date"] == entry["date"] and e["ticker"] == entry["ticker"])]
    entries.insert(0, entry)
    entries = entries[:MAX_ENTRIES]

    _save(entries)

def load_all() -> list:
    return _load()
