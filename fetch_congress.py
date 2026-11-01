from datetime import datetime, timedelta
import json
import os
import requests

# 新增：强大的多格式日期解析函数
def parse_flexible_date(date_str):
    if not date_str:
        return None
    # 穷举国会 API 中可能出现的随意日期格式
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    return None

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

    # 获取近 10 年的数据，确保覆盖足够长的时间线
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
            rep_name = str(t.get("representative", "")).lower()
            
            # 放宽的姓名匹配
            if search_name in rep_name:
                trade_date_str = t.get("transaction_date") or t.get("disclosure_date")
                
                # 使用灵活的日期解析
                trade_date = parse_flexible_date(trade_date_str)
                
                if trade_date and trade_date >= ten_years_ago:
                    member_trades.append(t)

        print(f"Found {len(member_trades)} trades for {member_key}")

        formatted_trades = []
        ticker_activity = {}

        for t in member_trades:
            ticker = t.get("ticker")
            t_type = t.get("type", "").lower()

            # 过滤掉无效的股票代码
            if ticker and ticker != "--" and ticker != "N/A":
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

        # 动态聚合持仓：从交易最多的股票中提取
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

        # 按申报日期安全排序
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
