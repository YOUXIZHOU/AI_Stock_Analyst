import time
import yfinance as yf
from datetime import datetime

def get_news(ticker: str) -> list:
    for attempt in range(3):
        try:
            raw_news = yf.Ticker(ticker).news or []
            if raw_news:
                break
        except Exception:
            raw_news = []
        if attempt < 2:
            time.sleep(2 ** attempt)

    results = []
    for item in raw_news[:5]:
        content  = item.get("content", {})
        title    = content.get("title", "")
        summary  = content.get("summary", "")
        pub_date = content.get("pubDate", "")

        if pub_date:
            try:
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_date = dt.astimezone().strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass

        if title:
            results.append({"時間": pub_date, "標題": title, "摘要": summary})

    return results
