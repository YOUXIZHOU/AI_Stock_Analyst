import json
import math
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "history.json"


class _Encoder(json.JSONEncoder):
    """處理 Timestamp、numpy 型別及 NaN/Inf"""
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "item"):
            v = obj.item()
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return None
            return v
        return super().default(obj)

    def encode(self, obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return "null"
        return super().encode(obj)


def _to_json(obj):
    raw = json.dumps(obj, cls=_Encoder)
    return json.loads(raw)


def save_result(result: dict):
    if "error" in result.get("price", {}):
        return

    ohlcv = []
    if not result["ohlcv"].empty:
        ohlcv = _to_json(
            result["ohlcv"].reset_index().to_dict(orient="records")
        )

    entry = {
        "date":         datetime.now().strftime("%Y-%m-%d"),
        "ticker":       result["price"]["ticker"],
        "price":        result["price"],
        "fundamentals": result["fundamentals"],
        "news":         result["news"],
        "tech":         _to_json(result["tech"]),
        "ohlcv":        ohlcv,
        "analysis":     result["analysis"],
    }

    history = load_all()

    # 同一天同一股票只保留最新一筆
    history = [h for h in history if not (h["date"] == entry["date"] and h["ticker"] == entry["ticker"])]
    history.insert(0, entry)
    history = history[:30]  # 最多保留 30 筆

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_all() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
