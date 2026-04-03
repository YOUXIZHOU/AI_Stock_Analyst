"""
手動測試腳本 — 逐項驗證各功能
執行方式：python test.py
"""

import sys

def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

def ok(msg):   print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}"); sys.exit(1)

# ──────────────────────────────────────────
# Test 1: 股價數據
# ──────────────────────────────────────────
section("Test 1 - get_stock_price (NVDA)")
from tools.stock import get_stock_price
data = get_stock_price("NVDA")
print(f"  結果：{data}")
assert "error" not in data,             "找不到股票資料"
assert "latest_price" in data,          "缺少 latest_price"
assert isinstance(data["change_pct"], float), "change_pct 型別錯誤"
ok("股價數據正常")

# ──────────────────────────────────────────
# Test 2: OHLCV + 技術指標
# ──────────────────────────────────────────
section("Test 2 - get_ohlcv (NVDA)")
from tools.stock import get_ohlcv
df = get_ohlcv("NVDA")
print(f"  資料筆數：{len(df)} 筆，欄位：{list(df.columns)}")
assert not df.empty,          "DataFrame 為空"
assert "MA5"  in df.columns,  "缺少 MA5"
assert "MA20" in df.columns,  "缺少 MA20"
assert "MA60" in df.columns,  "缺少 MA60"
assert "BB_upper" in df.columns, "缺少 BB_upper"
ok("OHLCV 與技術指標正常")

# ──────────────────────────────────────────
# Test 3: 公司基本面
# ──────────────────────────────────────────
section("Test 3 - get_fundamentals (NVDA)")
from tools.fundamentals import get_fundamentals
fund = get_fundamentals("NVDA")
print(f"  結果：{fund}")
assert "error" not in fund,       "找不到基本面資料"
assert "本益比(PE)" in fund,       "缺少 PE"
assert "每股盈餘(EPS)" in fund,    "缺少 EPS"
assert "自由現金流" in fund,       "缺少自由現金流"
ok("公司基本面正常")

# ──────────────────────────────────────────
# Test 4: 新聞
# ──────────────────────────────────────────
section("Test 4 - get_news (NVDA)")
from tools.news import get_news
news = get_news("NVDA")
print(f"  取得 {len(news)} 則新聞")
if news:
    print(f"  第一則：{news[0].get('時間')} | {news[0].get('標題', '')[:50]}")
    assert "時間" in news[0],  "缺少時間欄位"
    assert "標題" in news[0],  "缺少標題欄位"
ok("新聞數據正常")

# ──────────────────────────────────────────
# Test 5: 完整 Agent 流程
# ──────────────────────────────────────────
section("Test 5 - run_agent (NVDA) — 會呼叫 Claude API")
from agent.controller import run_agent
result = run_agent("NVDA")
print(f"  回傳 keys：{list(result.keys())}")
assert "price"        in result, "缺少 price"
assert "tech"         in result, "缺少 tech"
assert "fundamentals" in result, "缺少 fundamentals"
assert "news"         in result, "缺少 news"
assert "ohlcv"        in result, "缺少 ohlcv"
assert "analysis"     in result, "缺少 analysis"
assert result["analysis"],       "Claude 分析為空"
print(f"\n  Claude 分析預覽（前200字）：\n  {result['analysis'][:200]}...")
ok("完整 Agent 流程正常")

# ──────────────────────────────────────────
# Test 6: 股票推薦（看多）
# ──────────────────────────────────────────
section("Test 6 - run_recommender (bullish) — 會呼叫 Claude API（較慢）")
from agent.recommender import run_recommender
rec = run_recommender("bullish")
print(f"  市場觀點：{rec['sentiment']}")
print(f"  篩選出 {len(rec['candidates'])} 支候選股")
if rec["candidates"]:
    print(f"  前3支：{[s['ticker'] for s in rec['candidates'][:3]]}")
assert "analysis" in rec,  "缺少 Claude 分析"
assert rec["analysis"],    "Claude 推薦為空"
print(f"\n  Claude 推薦預覽（前200字）：\n  {rec['analysis'][:200]}...")
ok("股票推薦（看多）正常")

# ──────────────────────────────────────────
section("所有測試通過 ✅")
