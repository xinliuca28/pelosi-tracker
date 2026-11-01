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
    print("Fetching trade history from robust multi-source public APIs...")
    
    # 覆盖多个高可用、免密直连的开源公共数据源
    api_endpoints = [
        "https://raw.githubusercontent.com/fja05680/congressional-stock-watcher-data/master/data/all_transactions.json",
        "https://raw.githubusercontent.com/ucsb-seclab/congress-stock-watcher/main/data/all_transactions.json",
        "https://house-stock-watcher-data.s3.amazonaws.com/data/all_transactions.json"
    ]

    raw_congress = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    for url in api_endpoints:
        try:
            print(f"Trying endpoint: {url}")
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    raw_congress = data
                    print(f"Success! Loaded {len(raw_congress)} records from {url}")
                    break
                elif isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0:
                            raw_congress = v
                            print(f"Success! Loaded {len(raw_congress)} records from dict key '{k}'")
                            break
                    if len(raw_congress) > 0:
                        break
            else:
                print(f"Endpoint returned status code: {res.status_code}")
        except Exception as e:
            print(f"Connection error with {url}: {e}")

    print(f"Total collected raw records: {len(raw_congress)}")

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
            rep_name = str(t.get("representative") or t.get("senator") or t.get("politician") or t.get("name") or "").lower()
            
            if search_name in rep_name:
                trade_date_str = t.get("transaction_date") or t.get("disclosure_date") or t.get("TransactionDate") or t.get("date")
                trade_date = parse_flexible_date(trade_date_str)
                
                if trade_date and trade_date >= ten_years_ago:
                    member_trades.append(t)

        print(f"Found {len(member_trades)} trades for {member_key}")

        formatted_trades = []
        ticker_activity = {}

        for t in member_trades:
            ticker = t.get("ticker") or t.get("Symbol") or t.get("asset_ticker")
            t_type = str(t.get("type") or t.get("Transaction") or t.get("transaction_type") or "").lower()

            if ticker and ticker != "--" and ticker != "N/A" and ticker is not None:
                ticker_activity[str(ticker)] = ticker_activity.get(str(ticker), 0) + 1

            action = "🟢 Purchase" if "purchase" in t_type or "buy" in t_type else "🔴 Sale"
            
            formatted_trades.append({
                "Filing Date": t.get("disclosure_date") or t.get("ReportDate") or t.get("filing_date"),
                "Trade Date": t.get("transaction_date") or t.get("TransactionDate") or t.get("date"),
                "Ticker": ticker,
                "Action": action,
                "Asset Class": t.get("asset_type") or "Common Stock",
                "Description": t.get("description") or t.get("asset_description") or "Disclosed Transaction",
                "Disclosed Range": t.get("amount") or t.get("Range") or t.get("value"),
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
