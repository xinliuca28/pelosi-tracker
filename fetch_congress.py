from datetime import datetime, timedelta
import json
import os
import requests

def parse_flexible_date(date_str):
    if not date_str:
        return None
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    return None

def update_congress_dynamically():
    print("Fetching trade history from public endpoints...")
    
    # 尝试多个备用镜像源
    urls = [
        "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json",
        "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
    ]

    raw_congress = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    raw_congress.extend(data)
                    print(f"Loaded {len(data)} records from {url.split('/')[-2]}")
                elif isinstance(data, dict):
                    # 如果返回的是字典，尝试提取里面的列表数据
                    for key, val in data.items():
                        if isinstance(val, list):
                            raw_congress.extend(val)
                            print(f"Loaded {len(val)} records from dict key '{key}'")
                            break
            else:
                print(f"Failed to fetch {url}, status: {res.status_code}")
        except Exception as e:
            print(f"Error with {url}: {e}")

    print(f"Total raw records collected: {len(raw_congress)}")

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

    for member_key, search_name in target_politicians.items():
        member_trades = []
        for t in raw_congress:
            rep_name = str(t.get("representative") or t.get("senator") or "").lower()
            
            if search_name in rep_name:
                trade_date_str = t.get("transaction_date") or t.get("disclosure_date")
                trade_date = parse_flexible_date(trade_date_str)
                
                if trade_date and trade_date >= ten_years_ago:
                    member_trades.append(t)

        print(f"Found {len(member_trades)} trades for {member_key}")

        formatted_trades = []
        ticker_activity = {}

        for t in member_trades:
            ticker = t.get("ticker")
            t_type = str(t.get("type", "")).lower()

            if ticker and ticker != "--" and ticker != "N/A":
                ticker_activity[ticker] = ticker_activity.get(ticker, 0) + 1

            action = "🟢 Purchase" if "purchase" in t_type or "buy" in t_type else "🔴 Sale"
            
            formatted_trades.append({
                "Filing Date": t.get("disclosure_date"),
                "Trade Date": t.get("transaction_date"),
                "Ticker": ticker,
                "Action": action,
                "Asset Class": t.get("asset_type", "Common Stock"),
                "Description": t.get("description", "Disclosed Transaction"),
                "Disclosed Range": t.get("amount"),
                "midpoint_val": 750000,
                "underlying_shares": 5000,
            })

        dynamic_holdings = []
        sorted_tickers = sorted(ticker_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for ticker, count in sorted_tickers:
            dynamic_holdings.append({
                "Ticker": ticker,
                "Company": f"{ticker} (Dynamic)",
                "Est. Cost Basis ($)": 100.0,
                "Est. Value ($10k)": 1000,
                "Est. Allocation (%)": round(100 / max(len(sorted_tickers), 1), 2),
            })

        formatted_trades.sort(key=lambda x: str(x.get("Filing Date") or ""), reverse=True)

        congress_export[member_key] = {
            "holdings": dynamic_holdings,
            "trades": formatted_trades,
        }

    with open("data/congress_data.json", "w", encoding="utf-8") as f:
        json.dump(congress_export, f, indent=4, ensure_ascii=False)
    print("Successfully generated dynamic congress_data.json")

if __name__ == "__main__":
    update_congress_dynamically()
