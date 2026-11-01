from datetime import datetime, timedelta
import json
import os
import requests


def update_congress_tracker():
  print("Fetching full 5-year Congressional trades from open API...")
  url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
  try:
    res = requests.get(url, timeout=20)
    if res.status_code != 200:
      print("Failed to fetch congress data.")
      return
    raw_congress = res.json()
  except Exception as e:
    print(f"Error fetching congress data: {e}")
    return

  # 设定时间过滤：只保留最近 5 年内的数据
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
    for t in member_trades:
      formatted_trades.append({
          "Filing Date": t.get("disclosure_date"),
          "Trade Date": t.get("transaction_date"),
          "Ticker": t.get("ticker"),
          "Action": (
              "🟢 Purchase"
              if "purchase" in t.get("type", "").lower()
              else "🔴 Sale"
          ),
          "Asset Class": t.get("asset_type", "Common Stock"),
          "Description": t.get("description", "Disclosed Transaction"),
          "Disclosed Range": t.get("amount"),
          "midpoint_val": 750000,
          "underlying_shares": 5000,
      })

    formatted_trades.sort(key=lambda x: x["Filing Date"] or "", reverse=True)
    congress_export[member_key] = formatted_trades

  # 保存到独立的国会数据文件
  with open("data/congress_data.json", "w", encoding="utf-8") as f:
    json.dump(congress_export, f, indent=4, ensure_ascii=False)
  print("Successfully updated 5-year Congress data!")


if __name__ == "__main__":
  update_congress_tracker()
