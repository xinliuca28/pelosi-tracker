from datetime import datetime, timedelta
import json
import os
import requests

def update_congress_dynamically():
    print("Fetching trade history from API...")
    url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

    raw_congress = []
    try:
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            raw_congress = res.json()
            print(f"Success: Fetched {len(raw_congress)} total records.")
        else:
            print(f"API Error: {res.status_code}")
    except Exception as e:
        print(f"Error fetching congress data: {e}")

    # 放宽到 10 年，防止某些议员近年没有交易
    ten_years_ago = datetime.now() - timedelta(days=365 * 10)

    target_politicians = {
        "Nancy Pelosi (D - House)": "pelosi",
        "Tommy Tuberville (R - Senate)": "tuberville",
        "Mark Green (R - House)": "green",
        "Dan Crenshaw (R - House)": "crenshaw",
        "Josh Gottheimer (D - House)": "gottheimer",
    }

    os.makedirs("data", exist_ok=True)
    congress_export = {}

    # 用于辅助调试：记录出现过的名字
    all_reps = set()
    for t in raw_congress:
         all_reps.add(t.get("representative", ""))

    for member_key, search_name in target_politicians.items():
        member_trades = []
        for t in raw_congress:
            rep_name = str(t.get("representative", "")).lower()
            
            # 使用更宽泛的匹配
            if search_name in rep_name:
                trade_date_str = t.get("transaction_date") or t.get("disclosure_date")
                if trade_date_str:
                    try:
                        trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d")
                        if trade_date >= ten_years_ago:
                            member_trades.append(t)
                    except ValueError:
                        pass

        print(f"Found {len(member_trades)} trades for {member_key}")

        formatted_trades = []
        ticker_activity = {}

        for t in member_trades:
            ticker = t.get("ticker")
            t_type = t.get("type", "").lower()

            if ticker and ticker != "--":
                ticker_activity[ticker] = ticker_activity.get(ticker, 0) + 1

            formatted_trades.append({
                "Filing Date": t.get("disclosure_date"),
                "Trade Date": t.get("transaction_date"),
                "Ticker": ticker,
                "Action": "🟢 Purchase" if "purchase" in t_type else "🔴 Sale",
                "Asset Class": t.get("asset_type", "Common Stock"),
                "Description": t.get("description", "Disclosed Transaction"),
                "Disclosed Range": t.get("amount"),
                "midpoint_val": 750000,
                "underlying_shares": 5000,
            })

        dynamic_holdings = []
        sorted_tickers = sorted(ticker_activity.items(), key=lambda x: x[1], reverse=True)[:6]
        
        # 移除兜底数据，如果没数据，直接空着，这样更容易暴露问题
        if not sorted_tickers:
             print(f"WARNING: No data aggregated for {member_key}. Check API names.")
             
        for ticker, count in sorted_tickers:
            dynamic_holdings.append({
                "Ticker": ticker,
                "Company": f"{ticker} (Dynamic)",
                "Est. Cost Basis ($)": 100.0,
                "Est. Value ($10k)": 1000,
                "Est. Allocation (%)": round(100 / max(len(sorted_tickers), 1), 2),
            })

        formatted_trades.sort(key=lambda x: x.get("Filing Date") or "", reverse=True)

        congress_export[member_key] = {
            "holdings": dynamic_holdings,
            "trades": formatted_trades,
        }

    with open("data/congress_data.json", "w", encoding="utf-8") as f:
        json.dump(congress_export, f, indent=4, ensure_ascii=False)
    print("Successfully generated dynamic congress_data.json")
    
    # 打印一下 API 里所有带 Pelosi 的名字，看看到底是什么格式
    pelosi_matches = [name for name in all_reps if "pelosi" in str(name).lower()]
    print(f"API names matching 'pelosi': {pelosi_matches}")

if __name__ == "__main__":
    update_congress_dynamically()
