import os
import json
from datetime import datetime
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

def _client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "item"):
            return obj.item()
        return super().default(obj)

def _to_json(obj) -> str:
    return json.loads(json.dumps(obj, cls=_Encoder))

def save_result(result: dict):
    if "error" in result.get("price", {}):
        return

    ohlcv = (
        _to_json(result["ohlcv"].reset_index().to_dict(orient="records"))
        if not result["ohlcv"].empty else []
    )

    entry = {
        "date":          datetime.now().strftime("%Y-%m-%d"),
        "ticker":        result["price"]["ticker"],
        "price":         result["price"],
        "fundamentals":  result["fundamentals"],
        "news":          result["news"],
        "tech":          result["tech"],
        "ohlcv":         ohlcv,
        "analysis":      result["analysis"],
    }

    try:
        _client().table("search_history").upsert(
            entry, on_conflict="date,ticker"
        ).execute()
    except Exception as e:
        print(f"[history] save failed: {e}")

def load_all() -> list:
    try:
        res = (
            _client()
            .table("search_history")
            .select("date, ticker, price, fundamentals, news, tech, ohlcv, analysis")
            .order("created_at", desc=True)
            .limit(30)
            .execute()
        )
        return res.data or []
    except Exception as e:
        print(f"[history] load failed: {e}")
        return []
