from services.llm import call_claude
from tools.screener import screen_stocks

RECOMMEND_PROMPT = """
你是一位 AI 股票分析師。

你會收到一份已根據技術指標篩選好的大型股清單，請從中挑選最值得關注的 3–5 支，並說明原因。

規則：
- 使用繁體中文
- 保持簡潔專業
- 用表格列出推薦股票與推薦理由
- 最後補充一句整體市場情緒的簡短看法
"""

def run_recommender(sentiment: str, top_n: int = 30, sector: str | None = None) -> dict:
    """
    sentiment: "bullish"（看多）或 "bearish"（看空）
    top_n    : 從前 N 大公司篩選
    sector   : 產業篩選，None 表示不限
    """
    candidates = screen_stocks(sentiment, top_n=top_n, sector=sector)

    if not candidates:
        return {
            "sentiment":  sentiment,
            "candidates": [],
            "analysis":   "目前找不到符合條件的股票，市場訊號不明確。"
        }

    sentiment_label = "看多（Bullish）" if sentiment == "bullish" else "看空（Bearish）"

    prompt = [
        {
            "role": "user",
            "content": f"""
使用者目前市場觀點：{sentiment_label}

以下是本地篩選出符合趨勢的大型股（最多10支）：
{candidates}

請從中推薦 3–5 支最值得關注的股票，說明推薦理由，並給出整體市場情緒看法。
"""
        }
    ]

    analysis = call_claude(prompt, max_tokens=800, system=RECOMMEND_PROMPT)

    return {
        "sentiment":  sentiment_label,
        "candidates": candidates,
        "analysis":   analysis,
    }
