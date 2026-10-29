import json
import os
import requests

# 1. 定义您“只想追踪”的议员白名单 (White List)
TARGET_MEMBERS = [
    "Nancy Pelosi",
    "Tommy Tuberville",
    "Mark Green",
    "Dan Crenshaw",
    "Josh Gottheimer",
]

# 2. 从开源数据源（例如 capitol-stock-watch 或 House Clerk JSON）请求最新披露
DATA_URL = "https://raw.githubusercontent.com/capitol-stock-watch-open-data/capitol-stock-watch-data/main/data/disclosures.json"


def check_new_transactions():
  try:
    response = requests.get(DATA_URL, timeout=10)
    if response.status_code != 200:
      print("Failed to fetch data source.")
      return

    disclosures = response.json()

    # 3. 过滤数据：只留下您关注的议员
    target_trades = [
        d for d in disclosures if d.get("member_name") in TARGET_MEMBERS
    ]

    print(f"Found {len(target_trades)} records for target members.")

    # 4. 对比是否有新披露，如果存在新数据则进行推送/更新处理
    # （可根据最新一条交易的 filing_id 或 trade_date 与旧文件对比）

  except Exception as e:
    print(f"Error checking updates: {e}")


if __name__ == "__main__":
  check_new_transactions()
