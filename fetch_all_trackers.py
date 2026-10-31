import json
import os
import requests


def fetch_congress_data():
  print("Fetching Congressional trades from open API...")
  url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
  try:
    res = requests.get(url, timeout=15)
    if res.status_code == 200:
      return res.json()
  except Exception as e:
    print(f"Error fetching congress data: {e}")
  return []


def update_all_trackers():
  raw_congress = fetch_congress_data()

  # 映射你需要追踪的议员名字
  target_politicians = {
      "Nancy Pelosi (D - House)": "Nancy Pelosi",
      "Tommy Tuberville (R - Senate)": "Tommy Tuberville",
      "Mark Green (R - House)": "Mark Green",
      "Dan Crenshaw (R - House)": "Dan Crenshaw",
      "Josh Gottheimer (D - House)": "Josh Gottheimer",
  }

  os.makedirs("data", exist_ok=True)
  database_export = {}

  # 1. 动态处理国会议员数据
  for member_key, search_name in target_politicians.items():
    member_trades = [
        t for t in raw_congress if search_name.lower() in t.get("representative", "").lower()
    ]
    
    formatted_trades = []
    for t in member_trades:
      formatted_trades.append({
          "Filing Date": t.get("disclosure_date"),
          "Trade Date": t.get("transaction_date"),
          "Ticker": t.get("ticker"),
          "Action": "🟢 Purchase" if "purchase" in t.get("type", "").lower() else "🔴 Sale",
          "Asset Class": t.get("asset_type", "Common Stock"),
          "Description": t.get("description", "Disclosed Transaction"),
          "Disclosed Range": t.get("amount"),
          "midpoint_val": 750000,
          "underlying_shares": 5000,
      })
    
    database_export[member_key] = formatted_trades

  # 2. 处理巴菲特 (Warren Buffett) 13F 数据源
  # 实际项目中可替换为 SEC API 或 FMP 的 13F 接口
  buffett_holdings = [
      {"Ticker": "AAPL", "Company": "Apple", "Est. Cost Basis ($)": 35.0, "Est. Value ($10k)": 842480, "Est. Allocation (%)": 35.0},
      {"Ticker": "GOOGL", "Company": "Alphabet (Google)", "Est. Cost Basis ($)": 140.0, "Est. Value ($10k)": 250000, "Est. Allocation (%)": 10.4},
      {"Ticker": "BAC", "Company": "Bank of America", "Est. Cost Basis ($)": 24.0, "Est. Value ($10k)": 411200, "Est. Allocation (%)": 9.5},
  ]
  database_export["Warren Buffett (Berkshire)"] = buffett_holdings

  # 统一写入本地 JSON 文件供前端读取
  with open("data/trackers_data.json", "w", encoding="utf-8") as f:
    json.dump(database_export, f, indent=4, ensure_ascii=False)
  print("Successfully updated all trackers data!")

if __name__ == "__main__":
  update_all_trackers()
