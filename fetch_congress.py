import json
import os
import requests
from datetime import datetime, timedelta

def update_congress_dynamically():
    print("Fetching trade history using Financial Modeling Prep (FMP) API...")
    api_key = os.environ.get("FMP_API_KEY")
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("ERROR: FMP_API_KEY is not set. API request will fail.")
        return

    target_politicians = {
        "Nancy Pelosi (D - House)": {"endpoint": "house-trades-by-name", "name": "nancy pelosi"},
        "Tommy Tuberville (R - Senate)": {"endpoint": "senate-trades-by-name", "name": "tommy tuberville"},
        "Mark Green (R - House)": {"endpoint": "house-trades-by-name", "name": "mark green"},
        "Dan Crenshaw (R - House)": {"endpoint": "house-trades-by-name", "name": "dan crenshaw"},
        "Josh Gottheimer (D - House)": {"endpoint": "house-trades-by-name", "name": "josh gottheimer"},
    }

    os.makedirs("data", exist_ok=True)
    congress_export = {}

    for member_key, meta in target_politicians.items():
        member_trades = []
        # 调用 FMP 姓名搜索接口
        url = f"https://financialmodelingprep.com/stable/{meta['endpoint']}?name={meta['name'].replace(' ', '%20')}&apikey={api_key}"
        
        try:
            res = requests.get(url, timeout=30)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    member_trades.extend(data)
                print(f"Success: Fetched {len(member_trades)} trades for {member_key}.")
            else:
                print(f"API Error for {member_key}: {res.status_code}")
        except Exception as e:
            print(f"Error fetching data for {member_key}: {e}")

        formatted_trades = []
        ticker_activity = {}

        for t in member_trades:
            # 兼容 FMP 的字段名
            ticker = t.get("symbol") or t.get("ticker")
            t_type = str(t.get("type", "")).lower()

            if ticker and ticker != "--" and ticker != "N/A":
                ticker_activity[ticker] = ticker_activity.get(ticker, 0) + 1

            action = "🟢 Purchase" if "purchase" in t_type or "buy" in t_type else "🔴 Sale"
            
            formatted_trades.append({
                "Filing Date": t.get("disclosureDate") or t.get("disclosure_date"),
                "Trade Date": t.get("transactionDate") or t.get("transaction_date"),
                "Ticker": ticker,
                "Action": action,
                "Asset Class": t.get("assetType") or t.get("asset_type") or "Common Stock",
                "Description": t.get("assetDescription") or t.get("description", "Disclosed Transaction"),
                "Disclosed Range": t.get("amount"),
                "midpoint_val": 750000,
                "underlying_shares": 5000,
            })

        # 动态计算核心持仓
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
    print("Successfully generated dynamic congress_data.json via FMP")

if __name__ == "__main__":
    update_congress_dynamically()
