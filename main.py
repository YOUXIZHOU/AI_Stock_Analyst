from agent.controller import run_agent

def display_results(result: dict):
    price = result["price"]
    fund  = result["fundamentals"]
    news  = result["news"]

    print("\n========== 股價數據 ==========")
    for key, value in price.items():
        print(f"  {key}: {value}")

    print("\n========== 公司基本面 ==========")
    for key, value in fund.items():
        print(f"  {key}: {value}")

    print("\n========== 最新新聞 ==========")
    for i, item in enumerate(news, 1):
        print(f"  [{i}] {item.get('時間', '')} | {item.get('標題', '')}")
        if item.get("摘要"):
            print(f"      {item['摘要'][:200]}...")

    print("\n========== Claude 分析 ==========")
    print(result["analysis"])
    print()

if __name__ == "__main__":
    while True:
        user_input = input("請輸入股票代碼（例如 NVDA）：")
        if user_input.lower() in ["exit", "quit"]:
            print("退出程式。")
            break
        result = run_agent(user_input)
        display_results(result)
