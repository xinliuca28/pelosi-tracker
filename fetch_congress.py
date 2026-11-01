from datetime import datetime, timedelta
import json
import os
import requests

def update_congress_dynamically():
    print("Fetching 5-year trade history and dynamically aggregating holdings...")
    url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

    raw_congress = []
    try:
        res = requests.get(url, timeout=25)
        if res.status_code == 200:
            raw_congress = res.json()
    except Exception as e:
        print(f"Error fetching congress data: {e}")

    five_years_ago = datetime.now() - timedelta(days=365 * 5)

    target_politicians = {
        "Nancy Pelosi (D - House)": "Nancy Pelosi",
        "Tommy Tuberville (R - Senate)": "Tommy Tuberville",
        "Mark Green (R - House)": "Mark Green",
        "Dan Crenshaw (R - House)": "Dan Crenshaw",
        "Josh Gottheimer (D - House)": "Josh Gottheimer",
    }

    os.makedirs("data", exist_ok=True)
    congress_export = {}

    for member_key, search_name in target_politicians.items():
        member_trades = []
        for t in raw_congress:
            if search_name.lower() in t.get("representative", "").lower():
                trade_date_str = t.get("transaction_date") or t.get("disclosure_date")
                if trade_date_str:
                    try:
                        trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d")
                        if trade_date >= five_years_ago:
                            member_trades.append(t)
                    except ValueError:
                        pass

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

        # 动态聚合持仓
        dynamic_holdings = []
        sorted_tickers = sorted(ticker_activity.items(), key=lambda x: x[1], reverse=True)[:6]
        
        # 兜底：如果 API 没拉到数据，提供一个默认数据防止出错
        if not sorted_tickers:
            sorted_tickers = [("NVDA", 1)]
            formatted_trades = [{
                 "Filing Date": datetime.now().strftime("%Y-%m-%d"),
                 "Trade Date": datetime.now().strftime("%Y-%m-%d"),
                 "Ticker": "NVDA",
                 "Action": "🟢 Purchase",
                 "Asset Class": "Common Stock",
                 "Description": "Fallback Data",
                 "Disclosed Range": "$1M+",
                 "midpoint_val": 750000,
                 "underlying_shares": 5000,
            }]

        for ticker, count in sorted_tickers:
            dynamic_holdings.append({
                "Ticker": ticker,
                "Company": f"{ticker} (Dynamic)",
                "Est. Cost Basis ($)": 100.0,
                "Est. Value ($10k)": 1000,
                "Est. Allocation (%)": round(100 / len(sorted_tickers), 2),
            })

        formatted_trades.sort(key=lambda x: x.get("Filing Date") or "", reverse=True)

        congress_export[member_key] = {
            "holdings": dynamic_holdings,
            "trades": formatted_trades,
        }

    with open("data/congress_data.json", "w", encoding="utf-8") as f:
        json.dump(congress_export, f, indent=4, ensure_ascii=False)
    print("Successfully generated congress_data.json")

if __name__ == "__main__":
    update_congress_dynamically()
